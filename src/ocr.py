# ============================================================
# MODULO 1 — OCR  (foto manuscrita  ->  productos + cantidades)
# ------------------------------------------------------------
# Responsabilidad UNICA: hablar con la API de Google Gemini.
# Recibe una imagen, devuelve una lista de items detectados.
# Si manana cambiamos de Gemini a otro OCR, solo se toca AQUI.
# ============================================================

import json
import time
import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions as google_errors

# --- Configuracion del modelo ---
# gemini-2.0-flash: estable, buena vision para letra manuscrita y con su
# propia cuota gratuita (aparte de la del 2.5). Cambiar aqui si hace falta.
MODELO = "gemini-2.0-flash"   # cambiar aqui si quieres otro modelo

REINTENTOS = 3          # cuantas veces reintentar si llega un 429
ESPERA_SEGUNDOS = 5     # cuanto esperar entre reintentos


class CuotaAgotada(Exception):
    """Se agoto la cuota gratuita del modelo (Gemini respondio 429)."""


def _conectar():
    """Conecta con Gemini usando la llave guardada en secrets.toml."""
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # temperature=0 -> respuestas mas precisas y consistentes (menos "creativas").
    # Ideal para leer datos: queremos exactitud, no imaginacion.
    return genai.GenerativeModel(MODELO, generation_config={"temperature": 0})


def _armar_prompt(productos_catalogo):
    """
    Construye las instrucciones para la IA.
    Le pasamos el catalogo como 'vocabulario' para que reconozca
    la letra manuscrita y la mapee a nuestros productos exactos.
    """
    lista = "\n".join(
        f"- {p['nombre']} (tambien escrito: {', '.join(p['sinonimos'])})"
        for p in productos_catalogo
    )

    return f"""
Eres un asistente que lee listas de ventas escritas a mano de una
tienda de medicamentos agricolas y veterinarios.

Estos son los UNICOS productos que existen en la tienda:
{lista}

Trabaja en DOS PASOS:

PASO 1 — Transcribe la imagen TAL CUAL, renglón por renglón, sin
interpretar todavía. Copia cada línea aunque se repita o esté fea.

PASO 2 — Para CADA renglón del paso 1 que sea un producto, mapéalo a
un producto del catálogo con su cantidad.

Reglas importantes:
- Cada renglón del paso 1 que sea un producto DEBE aparecer en el paso 2.
- Un mismo producto base (ej "Ivermectina") puede aparecer varias veces con
  diferente presentacion (50ml, 100ml, 500ml, 1L, galon). Cada presentacion
  es un producto DISTINTO: NO los unas y NO descartes ninguno.
- Fíjate en el numero de tamaño (ml, L, galon) para elegir la presentacion.
- Los líquidos por litro se venden en presentacion de 1 L (y por galon, en 1
  galon). Si ves un numero de litros distinto de 1 (por ejemplo "Glifosol 3 L"
  o "Stop 2 L"), NO es un producto nuevo: es la presentacion de 1 L con la
  CANTIDAD igual a ese numero. Ejemplo: "Glifosol 3 L" = nombre "Glifosol 1L"
  con cantidad 3. Lo mismo con galones.
- Usa SIEMPRE el nombre exacto del catalogo (no inventes nombres).
- Si la letra coincide con un sinonimo, devuelve el nombre oficial.
- Si ves un renglón que parece un producto pero NO está en el catálogo (o
  no logras identificarlo), NO lo inventes ni lo fuerces: ponlo TAL CUAL lo
  leíste en la lista "no_reconocidos".

Responde SOLO con un JSON con esta forma exacta, sin texto extra:
{{
  "lectura_literal": ["renglón 1 tal cual", "renglón 2 tal cual"],
  "productos": [
    {{"nombre": "Ivermectina 1% 50ml", "cantidad": 2}},
    {{"nombre": "Ivermectina 1% 100ml", "cantidad": 1}}
  ],
  "no_reconocidos": ["lo que viste pero no está en el catálogo"]
}}
"""


def extraer_productos(imagen, productos_catalogo):
    """
    Recibe una imagen (PIL) y el catalogo de productos.
    Devuelve solo los productos VALIDOS (que existen en el catalogo).
    Guarda en st.session_state:
      - "ultima_lectura": la transcripcion literal
      - "no_reconocidos": lo que se vio pero no esta en el catalogo
    """
    modelo = _conectar()
    prompt = _armar_prompt(productos_catalogo)

    # Reintentamos si Gemini responde 429 (limite de peticiones)
    for intento in range(REINTENTOS):
        try:
            respuesta = modelo.generate_content([prompt, imagen])
            break
        except google_errors.ResourceExhausted:
            if intento < REINTENTOS - 1:
                time.sleep(ESPERA_SEGUNDOS)   # esperamos y volvemos a intentar
            else:
                # Traducimos el error tecnico de Google a uno claro de dominio
                raise CuotaAgotada()

    # Limpiamos posibles ```json que a veces agrega el modelo
    texto = respuesta.text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()

    datos = json.loads(texto)

    # Guardamos lo que el modelo "leyo" literalmente (para mostrarlo/depurar)
    st.session_state["ultima_lectura"] = datos.get("lectura_literal", [])

    # Lo que el modelo marco como "no reconocido"
    no_reconocidos = list(datos.get("no_reconocidos", []))

    # Validacion extra: si el modelo igual devolvio un producto cuyo nombre NO
    # esta en el catalogo (alucinacion), lo sacamos de las facturas y lo
    # mandamos a "no reconocidos". Asi NUNCA entra basura a las facturas.
    nombres_catalogo = {p["nombre"] for p in productos_catalogo}
    validos = []
    for prod in datos.get("productos", []):
        if prod.get("nombre") in nombres_catalogo:
            validos.append(prod)
        else:
            no_reconocidos.append(prod.get("nombre", "desconocido"))

    st.session_state["no_reconocidos"] = no_reconocidos
    return validos

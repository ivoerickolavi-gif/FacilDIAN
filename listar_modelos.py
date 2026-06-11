# ============================================================
# listar_modelos.py  —  DIAGNOSTICO (no es parte de la app)
# ------------------------------------------------------------
# Pregunta a Google que modelos puede usar TU llave.
# Correr con:   python listar_modelos.py
# ============================================================

import tomllib
import google.generativeai as genai

# Leemos la llave del mismo archivo que usa la app
with open(".streamlit/secrets.toml", "rb") as archivo:
    secretos = tomllib.load(archivo)

genai.configure(api_key=secretos["GEMINI_API_KEY"])

print("Modelos disponibles para tu llave (que sirven para generar contenido):\n")
for modelo in genai.list_models():
    if "generateContent" in modelo.supported_generation_methods:
        print("  -", modelo.name)

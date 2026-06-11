# ============================================================
# MODULO 4 — CONTROL LIMITE DIARIO DIAN
# ------------------------------------------------------------
# Responsabilidad UNICA: vigilar el tope de facturacion del dia
# (ej: $5.000.000). Acepta facturas hasta el limite y manda el
# excedente a "lista de espera" para el dia siguiente.
# ============================================================

import json
from datetime import date

RUTA_ESTADO = "data/facturas_dia.json"

# --- Regla del negocio ---
LIMITE_DIARIO_DIAN = 4000000   # tope diario en pesos
MAX_HISTORIAL = 30             # cuantas facturas verificadas guardamos en el historial


def cargar_estado():
    """
    Lee el estado del dia desde el JSON.
    Si el archivo es de un dia anterior, reinicia el dia y SUBE solas
    a la DIAN las facturas que estaban en espera (las que quepan en el
    tope de hoy; las que no quepan, siguen en espera otro dia mas).
    """
    with open(RUTA_ESTADO, "r", encoding="utf-8") as archivo:
        estado = json.load(archivo)

    hoy = str(date.today())
    if estado["fecha"] != hoy:
        en_espera = estado.get("lista_espera", [])
        historial = estado.get("facturas", [])   # NO lo borramos: es el historial

        # Reiniciamos solo el contador del dia; conservamos el historial
        estado = {
            "fecha": hoy,
            "acumulado_dian": 0,
            "facturas": historial,
            "lista_espera": [],
        }

        # Las facturas que esperaban se suben automaticamente hoy, pasando
        # por el mismo control de tope. Lo que no quepa, vuelve a espera.
        for factura in en_espera:
            verificar_factura(estado, factura)

        guardar_estado(estado)   # dejamos el dia nuevo guardado en disco
    return estado


def guardar_estado(estado):
    """Escribe el estado actual de vuelta al JSON (lo hace permanente)."""
    with open(RUTA_ESTADO, "w", encoding="utf-8") as archivo:
        json.dump(estado, archivo, ensure_ascii=False, indent=2)


def disponible_hoy(estado):
    """Cuanto falta para llegar al tope diario."""
    return LIMITE_DIARIO_DIAN - estado["acumulado_dian"]


def verificar_factura(estado, factura):
    """
    Intenta aprobar una factura contra el limite diario.
    - Si cabe: la suma al acumulado y la marca como aprobada.
    - Si NO cabe: la manda a la lista de espera.
    Devuelve el texto del resultado: "aprobada" o "espera".
    """
    if factura["total"] <= disponible_hoy(estado):
        estado["acumulado_dian"] += factura["total"]
        estado["facturas"].append(factura)
        # Mantenemos solo las ultimas MAX_HISTORIAL para no crecer infinito
        estado["facturas"] = estado["facturas"][-MAX_HISTORIAL:]
        resultado = "aprobada"
    else:
        estado["lista_espera"].append(factura)
        resultado = "espera"

    guardar_estado(estado)
    return resultado


def anular_factura(estado, indice):
    """
    Revierte una factura ya verificada (la 'des-factura').
    - La saca de la lista de verificadas.
    - Le DEVUELVE su valor al acumulado diario (resta el total).
    - Devuelve la factura para poder mandarla de nuevo a pendientes.
    """
    factura = estado["facturas"].pop(indice)
    estado["acumulado_dian"] -= factura["total"]
    guardar_estado(estado)
    return factura

# ============================================================
# ALMACEN DE FACTURAS VERIFICADAS
# ------------------------------------------------------------
# Guarda en disco las facturas que el empleado ya reviso y
# verifico. Mantiene solo las ultimas MAX_HISTORIAL.
# ============================================================

import json

RUTA_ESTADO = "data/facturas_dia.json"
MAX_HISTORIAL = 30   # cuantas facturas verificadas guardamos en el historial


def cargar_estado():
    """Lee las facturas verificadas del disco."""
    try:
        with open(RUTA_ESTADO, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        datos = {}
    return {"facturas": datos.get("facturas", [])}


def guardar_estado(estado):
    """Escribe el estado de vuelta al disco (lo hace permanente)."""
    with open(RUTA_ESTADO, "w", encoding="utf-8") as archivo:
        json.dump(estado, archivo, ensure_ascii=False, indent=2)


def verificar_factura(estado, factura):
    """Marca una factura como verificada: la guarda en el historial."""
    estado["facturas"].append(factura)
    # Mantenemos solo las ultimas MAX_HISTORIAL para no crecer infinito
    estado["facturas"] = estado["facturas"][-MAX_HISTORIAL:]
    guardar_estado(estado)


def anular_factura(estado, indice):
    """Saca una factura del historial y la devuelve para volver a editarla."""
    factura = estado["facturas"].pop(indice)
    guardar_estado(estado)
    return factura

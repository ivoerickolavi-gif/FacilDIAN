# ============================================================
# ALMACEN  —  guarda las facturas PENDIENTES en disco
# ------------------------------------------------------------
# Responsabilidad UNICA: que las facturas sin verificar NO se
# pierdan al cerrar la app. Las guarda en su propio archivo,
# aparte del control DIAN (que se reinicia cada dia).
# ============================================================

import json

RUTA_PENDIENTES = "data/pendientes.json"


def cargar_pendientes():
    """Lee las facturas pendientes del disco. Si no hay archivo, devuelve []."""
    try:
        with open(RUTA_PENDIENTES, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []


def guardar_pendientes(pendientes):
    """Escribe la lista de facturas pendientes al disco (las hace permanentes)."""
    with open(RUTA_PENDIENTES, "w", encoding="utf-8") as archivo:
        json.dump(pendientes, archivo, ensure_ascii=False, indent=2)

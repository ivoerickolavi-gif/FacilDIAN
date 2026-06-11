# ============================================================
# MODULO 2 — INVENTARIO  (productos y precios)
# ------------------------------------------------------------
# Responsabilidad UNICA: leer data/inventario.json y resolver
# cada producto detectado por el OCR a su precio real.
# Es la "fuente de verdad" de que existe y cuanto cuesta.
# ============================================================

import json

RUTA_CATALOGO = "data/inventario.json"


def cargar_catalogo():
    """Lee el archivo JSON y devuelve la lista de productos."""
    with open(RUTA_CATALOGO, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return datos["productos"]


def _buscar_precio(nombre, catalogo):
    """Busca un producto por su nombre y devuelve su precio (0 si no existe)."""
    for producto in catalogo:
        if producto["nombre"] == nombre:
            return producto["precio"]
    return 0


def valorar_productos(items_detectados, catalogo):
    """
    Recibe lo que devolvio el OCR  ->  [{"nombre": ..., "cantidad": ...}]
    Devuelve la misma lista pero con precio y subtotal agregados:
        [{"nombre": ..., "cantidad": ..., "precio": ..., "subtotal": ...}]
    """
    valorados = []
    for item in items_detectados:
        precio = _buscar_precio(item["nombre"], catalogo)
        cantidad = int(item["cantidad"])   # nos aseguramos de que sea entero
        valorados.append({
            "nombre": item["nombre"],
            "cantidad": cantidad,
            "precio": precio,
            "subtotal": precio * cantidad,
        })
    return valorados

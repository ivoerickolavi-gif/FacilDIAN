# ============================================================
# MODULO 3 — AGRUPADOR  (productos  ->  borradores de factura)
# ------------------------------------------------------------
# Responsabilidad UNICA: el algoritmo que reparte los productos
# en facturas. Reglas: maximo 3-4 items por factura y no superar
# el tope de valor por factura. Es matematica pura, sin internet.
# ============================================================

# --- Reglas del negocio (cambialas aqui si hace falta) ---
MAX_ITEMS_POR_FACTURA = 4
TOPE_POR_FACTURA = 1500000   # valor maximo en pesos por factura


def _factura_vacia():
    """Crea el molde de una factura nueva, sin productos."""
    return {"items": [], "total": 0}


def _cabe(factura, subtotal):
    """Decide si un producto cabe en la factura actual."""
    cabe_por_cantidad = len(factura["items"]) < MAX_ITEMS_POR_FACTURA
    cabe_por_valor = factura["total"] + subtotal <= TOPE_POR_FACTURA
    return cabe_por_cantidad and cabe_por_valor


def agrupar_en_facturas(productos_valorados):
    """
    Recibe productos con precio  ->  [{"nombre", "cantidad", "precio", "subtotal"}]
    Devuelve una lista de borradores de factura:
        [{"items": [...], "total": ...}, ...]
    """
    facturas = []
    factura_actual = _factura_vacia()

    for producto in productos_valorados:
        subtotal = producto["subtotal"]

        # Si NO cabe en la factura actual, guardamos esa y abrimos una nueva
        if not _cabe(factura_actual, subtotal):
            if factura_actual["items"]:           # evitamos guardar facturas vacias
                facturas.append(factura_actual)
            factura_actual = _factura_vacia()

        # Metemos el producto en la factura actual
        factura_actual["items"].append(producto)
        factura_actual["total"] += subtotal

    # Al terminar el bucle, guardamos la ultima factura si tiene productos
    if factura_actual["items"]:
        facturas.append(factura_actual)

    return facturas

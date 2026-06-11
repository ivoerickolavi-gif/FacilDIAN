# ============================================================
# MODULO 3 — ARMAR FACTURA  (productos  ->  factura)
# ------------------------------------------------------------
# Responsabilidad UNICA: tomar los productos detectados y
# armar la factura con todos ellos (con su total).
# ============================================================


def agrupar_en_facturas(productos_valorados):
    """
    Recibe productos con precio  ->  [{"nombre", "cantidad", "precio", "subtotal"}]
    Devuelve una lista con UNA factura que contiene todos los productos:
        [{"items": [...], "total": ...}]
    """
    if not productos_valorados:
        return []

    total = sum(p["subtotal"] for p in productos_valorados)
    factura = {"items": productos_valorados, "total": total}
    return [factura]

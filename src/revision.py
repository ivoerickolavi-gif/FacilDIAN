# ============================================================
# MODULO 5 — REVISION HUMANA  (panel de aprobacion)
# ------------------------------------------------------------
# Responsabilidad UNICA: armar los datos que el empleado ve en
# pantalla para revisar cada borrador y marcarlo como verificado.
# Aqui NO hay Streamlit: solo funciones de presentacion puras.
# ============================================================


def formatear_pesos(valor):
    """Convierte 1500000  ->  '$1.500.000' (formato colombiano)."""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def resumen_factura(factura):
    """
    Arma un texto legible de una factura para mostrar al empleado.
    Ejemplo de retorno:
        'Ivermectina 1% 50ml x2  ->  $56.000
         Glifosato 1L x1  ->  $25.000
         TOTAL: $81.000'
    """
    lineas = []
    for item in factura["items"]:
        linea = f"{item['nombre']} x{item['cantidad']}  ->  {formatear_pesos(item['subtotal'])}"
        lineas.append(linea)

    lineas.append(f"TOTAL: {formatear_pesos(factura['total'])}")
    return "\n".join(lineas)


def filas_tabla(factura):
    """
    Convierte los items de una factura en filas listas para una TABLA.
    Devuelve una lista de dicts; cada dict es una fila con columnas
    bonitas: Producto, Cantidad, Precio, Subtotal.
    """
    filas = []
    for item in factura["items"]:
        filas.append({
            "Producto": item["nombre"],
            "Cantidad": item["cantidad"],
            "Precio": formatear_pesos(item["precio"]),
            "Subtotal": formatear_pesos(item["subtotal"]),
        })
    return filas

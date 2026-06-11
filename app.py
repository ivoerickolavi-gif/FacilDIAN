# ============================================================
# app.py  —  PUNTO DE ENTRADA (Streamlit)
# ------------------------------------------------------------
# Unico archivo que ejecuta el usuario. Solo ORQUESTA:
# llama a los modulos de src/ en orden y dibuja la pantalla.
# NO debe contener logica de negocio (eso vive en src/).
# ============================================================

from datetime import datetime

import streamlit as st
from PIL import Image

# Importamos los modulos
from src import ocr
from src import inventario
from src import agrupador
from src import control_dian
from src import revision
from src import almacen

# ------------------------------------------------------------
# CONFIGURACION GENERAL
# ------------------------------------------------------------
st.set_page_config(page_title="FacilDIAN", page_icon="🧾", layout="wide")

# Cargamos datos una vez (catalogo fijo + estado del dia)
catalogo = inventario.cargar_catalogo()
estado = control_dian.cargar_estado()

# ------------------------------------------------------------
# MEMORIA DE SESION (navegacion + facturas pendientes)
# ------------------------------------------------------------
if "seccion" not in st.session_state:
    st.session_state["seccion"] = "Facturar"               # pantalla inicial
if "pendientes" not in st.session_state:
    # Cargamos desde el disco: asi NO se pierden al cerrar la app
    st.session_state["pendientes"] = almacen.cargar_pendientes()
if "facturando" not in st.session_state:
    st.session_state["facturando"] = False                 # ¿esta en el paso de subir foto?
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0                   # truco para limpiar la imagen
if "aviso_pendiente" not in st.session_state:
    st.session_state["aviso_pendiente"] = 0                # notificacion que se muestra 1 vez
if "editando" not in st.session_state:
    st.session_state["editando"] = None                   # indice de la factura en edicion
if "proceso_completado" not in st.session_state:
    st.session_state["proceso_completado"] = 0            # nº de facturas recien procesadas


# ============================================================
# CABECERA CON MARCA  —  banner verde arriba de cada pantalla
# ============================================================
def cabecera():
    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg, #2E7D32 0%, #66BB6A 100%);
            padding: 16px 22px; border-radius: 14px; margin-bottom: 14px;">
            <div style="color:white; font-size:26px; font-weight:700;">
                🌿 FacilDIAN
            </div>
            <div style="color:#E8F5E9; font-size:14px; margin-top:2px;">
                De tu lista escrita a mano a una factura, en segundos
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BARRA LATERAL  —  navegacion tipo app web
# ============================================================
def dibujar_menu():
    with st.sidebar:
        st.markdown("### 🌿 FacilDIAN")
        st.caption("Facturación asistida por IA")
        st.divider()

        activo = st.session_state["seccion"]

        if st.button("Facturar", use_container_width=True,
                     type="primary" if activo == "Facturar" else "secondary"):
            st.session_state["seccion"] = "Facturar"
            st.session_state["facturando"] = False          # siempre arranca en el inicio
            st.session_state["proceso_completado"] = 0
            st.rerun()

        if st.button("Mis facturas", use_container_width=True,
                     type="primary" if activo == "Facturas" else "secondary"):
            st.session_state["seccion"] = "Facturas"
            st.session_state["editando"] = None             # salimos de cualquier edicion
            st.rerun()

        st.divider()
        st.caption(f"⚡ Potenciado por Google Gemini")
        st.caption(f"Modelo: `{ocr.MODELO}`")
        st.caption("Puede saturarse por exceso de solicitudes (cuota).")


# ============================================================
# SECCION 1  —  FACTURACION
# ============================================================
def pantalla_inicio():
    """Pantalla de entrada: presentacion + boton para empezar."""
    st.subheader("Convierte tu lista escrita a mano en una factura, en segundos")
    st.write(
        "Toma una foto de la lista de ventas y la IA arma la factura por ti. "
        "Tú solo la revisas y la verificas."
    )

    if st.button("Iniciar facturación", type="primary", use_container_width=True):
        st.session_state["facturando"] = True
        st.session_state["proceso_completado"] = 0
        st.rerun()

    # Notificacion tras crear facturas (se muestra una sola vez)
    if st.session_state["aviso_pendiente"] > 0:
        st.toast(
            f"{st.session_state['aviso_pendiente']} factura(s) creada(s) con éxito "
            "· Están en Mis facturas",
            icon="✅",
        )
        st.session_state["aviso_pendiente"] = 0   # consumida: no se repite

    # --- Info de la app en mini pestañas desplegables ---
    st.write("")
    st.markdown("##### Conoce FacilDIAN")

    with st.expander("¿En qué consiste?"):
        st.write(
            "FacilDIAN es una **herramienta** que le ahorra tiempo al empleado de la tienda. "
            "En vez de digitar producto por producto la lista que un cliente mandó a comprar "
            "(muchas veces desde lejos, con un cotero o un tercero), el empleado solo sube una "
            "foto de esa lista: el agente la lee y arma **una sola factura** con todos los "
            "productos, sus nombres y precios, lista para subirla a la facturación electrónica "
            "del sistema que la tienda ya use."
        )

    with st.expander("¿Por qué se hizo?"):
        st.write(
            "Pasar a mano una lista larga de productos a un sistema de facturación es lento, "
            "tedioso y propenso a errores por letra ilegible. FacilDIAN convierte esa lista en "
            "una factura digital en segundos, sin volver a digitar nada."
        )

    with st.expander("¿A quién está dirigido?"):
        st.write(
            "A tiendas y distribuidoras de insumos agrícolas y veterinarios que reciben pedidos "
            "en listas escritas a mano y quieren facturarlos mucho más rápido en su propio "
            "sistema de facturación electrónica. No reemplaza ese sistema: es una herramienta "
            "que lo alimenta más rápido."
        )


def pantalla_subir_foto():
    """Paso de subir la imagen y procesarla con la IA."""
    foto = st.file_uploader(
        "¡Sube aquí la foto de la lista de productos que quieres facturar!",
        type=["jpg", "jpeg", "png"],
        key=f"uploader_{st.session_state['uploader_key']}",
    )

    if foto is None:
        return

    imagen = Image.open(foto)
    col_imagen, col_accion = st.columns([1, 2])

    with col_imagen:
        st.image(imagen, caption="Lista subida", use_container_width=True)

    with col_accion:
        # PASO 1: mientras no se haya completado, mostramos "Procesar foto"
        if st.session_state["proceso_completado"] == 0:
            if not st.button("Procesar foto", type="primary", use_container_width=True):
                return

            # Procesamos AQUI (dentro de la columna) para que el proceso se vea
            # al lado de la imagen y no debajo, fuera de vista.
            # Procesamos dentro de un try/except para atrapar errores de ejecucion
            # (sobre todo la cuota del modelo) y NO mostrar un traceback rojo.
            nuevas = None
            error_cuota = False
            error_otro = None
            with st.status("El agente está trabajando...", expanded=True) as status:
                try:
                    st.write("Leyendo la imagen con visión artificial...")
                    detectados = ocr.extraer_productos(imagen, catalogo)            # Modulo 1

                    # Mostramos lo que el modelo leyo literalmente (transparencia)
                    lectura = st.session_state.get("ultima_lectura", [])
                    if lectura:
                        st.write("Esto fue lo que leí en la lista:")
                        for linea in lectura:
                            st.write(f"• {linea}")

                    st.write(f"{len(detectados)} producto(s) detectado(s).")
                    st.write("Buscando precios en el inventario...")
                    valorados = inventario.valorar_productos(detectados, catalogo)  # Modulo 2

                    st.write("Armando la factura...")
                    nuevas = agrupador.agrupar_en_facturas(valorados)              # Modulo 3

                    # Sellamos cada factura con fecha y hora (para el historial)
                    ahora = datetime.now()
                    for factura in nuevas:
                        factura["fecha"] = ahora.strftime("%Y-%m-%d")
                        factura["hora"] = ahora.strftime("%H:%M:%S")

                    st.write(f"{len(nuevas)} factura(s) creada(s).")
                    status.update(label="¡Listo!", state="complete")
                except ocr.CuotaAgotada:
                    error_cuota = True
                    status.update(label="Límite de IA alcanzado", state="error")
                except Exception as fallo:
                    error_otro = fallo
                    status.update(label="No se pudo completar el proceso", state="error")

            # --- Mensajes AMABLES (sin texto rojo de Python) ---
            if error_cuota:
                st.warning(
                    "⏳ El asistente de IA alcanzó su límite de uso gratuito por ahora. "
                    "Espera unos minutos y vuelve a intentarlo; si continúa, el cupo "
                    "gratuito se renueva al día siguiente. No es un fallo de la aplicación."
                )
                return

            if error_otro is not None:
                st.warning(
                    "Ocurrió un problema al procesar la imagen. Inténtalo de nuevo o "
                    "prueba con otra foto más clara."
                )
                st.caption(f"Detalle técnico: {error_otro}")
                return

            if not nuevas:
                st.warning(
                    "No se detectaron productos del catálogo en la imagen. "
                    "Revisa que la foto sea clara e inténtalo de nuevo."
                )
                no_rec = st.session_state.get("no_reconocidos", [])
                if no_rec:
                    st.caption("La IA vio (pero no está en el catálogo): " + ", ".join(no_rec))
                return

            # Guardamos en pendientes (memoria) y en disco (permanente) y marcamos
            # el proceso como completado para mostrar la pantalla de exito.
            st.session_state["pendientes"].extend(nuevas)
            almacen.guardar_pendientes(st.session_state["pendientes"])
            st.session_state["proceso_completado"] = len(nuevas)

        # PASO 2: pantalla de exito con cierre MANUAL (dos caminos)
        if st.session_state["proceso_completado"] > 0:
            n = st.session_state["proceso_completado"]
            st.success("El proceso ha sido completado exitosamente")
            st.caption(f"Se creó la factura. Está en Mis facturas.")

            # Aviso de lo que la IA vio pero NO esta en el catalogo
            no_rec = st.session_state.get("no_reconocidos", [])
            if no_rec:
                st.warning("Estos renglones NO están en el catálogo y no se facturaron:")
                for nombre in no_rec:
                    st.write(f"• {nombre}")
                st.caption(
                    "Si deben venderse, agrégalos al catálogo (data/inventario.json) "
                    "y vuelve a subir la foto."
                )

            # Aceptar -> vuelve al menu de facturar (con notificacion)
            if st.button("Aceptar", type="primary", use_container_width=True):
                st.session_state["proceso_completado"] = 0
                st.session_state["facturando"] = False
                st.session_state["uploader_key"] += 1        # limpia la imagen
                st.session_state["aviso_pendiente"] = n
                st.rerun()

            # Ir a mis facturas -> va directo a la seccion Facturas a verificar
            if st.button("Ir a mis facturas", use_container_width=True):
                st.session_state["proceso_completado"] = 0
                st.session_state["facturando"] = False
                st.session_state["uploader_key"] += 1
                st.session_state["seccion"] = "Facturas"
                st.rerun()


def pagina_facturar():
    if st.session_state["facturando"]:
        pantalla_subir_foto()
    else:
        pantalla_inicio()


# ============================================================
# SECCION 2  —  FACTURAS  (dos pestañas: pendientes / verificadas)
# ============================================================
def _tarjeta_factura(factura):
    """Dibuja una factura como tarjeta desplegable con su tabla adentro."""
    fecha = factura.get("fecha", "—")
    hora = factura.get("hora", "")
    sello = f"{fecha} · {hora}".strip(" ·")
    titulo = f"Factura · {sello}  ·  {revision.formatear_pesos(factura['total'])}"

    with st.expander(titulo):
        st.dataframe(revision.filas_tabla(factura),        # Modulo 5 (tabla bonita)
                     hide_index=True, use_container_width=True)
        st.markdown(
            f"<div style='text-align:right; font-size:18px; margin-top:2px;'>"
            f"Total: <b style='color:#2E7D32;'>"
            f"{revision.formatear_pesos(factura['total'])}</b></div>",
            unsafe_allow_html=True,
        )


def _editar_factura(indice, factura):
    """Modo edicion: cambiar cantidades, quitar items y agregar productos."""
    st.markdown(f"**Editando factura · {factura.get('fecha', '')} {factura.get('hora', '')}**")

    # 1) Editar CANTIDAD y PRECIO de cada producto (cantidad 0 = quitarlo)
    cantidades = []
    precios = []
    for j, item in enumerate(factura["items"]):
        st.markdown(f"**{item['nombre']}**")
        col_cant, col_prec = st.columns(2)
        cant = col_cant.number_input(
            "Cantidad", min_value=0, step=1, value=item["cantidad"],
            key=f"cant_{indice}_{j}",
        )
        prec = col_prec.number_input(
            "Precio (c/u)", min_value=0, step=500, value=item["precio"],
            key=f"prec_{indice}_{j}",
        )
        cantidades.append(cant)
        precios.append(prec)

    # 2) Agregar un producto que la IA no haya detectado
    st.caption("¿Faltó un producto? Agrégalo aquí:")
    nombres = [p["nombre"] for p in catalogo]
    col_p, col_q, col_add = st.columns([3, 1, 1])
    producto_sel = col_p.selectbox("Producto", nombres, key=f"addprod_{indice}",
                                   label_visibility="collapsed")
    cant_sel = col_q.number_input("Cant.", min_value=1, step=1, value=1,
                                  key=f"addcant_{indice}", label_visibility="collapsed")
    if col_add.button("Agregar", key=f"add_{indice}"):
        # Conservamos cantidad y precio que el usuario ya haya cambiado
        for item, cant, prec in zip(factura["items"], cantidades, precios):
            item["cantidad"] = cant
            item["precio"] = prec
            item["subtotal"] = prec * cant

        precio = next(p["precio"] for p in catalogo if p["nombre"] == producto_sel)
        factura["items"].append({
            "nombre": producto_sel,
            "cantidad": cant_sel,
            "precio": precio,
            "subtotal": precio * cant_sel,
        })
        factura["total"] = sum(it["subtotal"] for it in factura["items"])
        almacen.guardar_pendientes(st.session_state["pendientes"])
        st.rerun()

    # 3) Guardar o cancelar
    col_g, col_c = st.columns(2)
    if col_g.button("Guardar cambios", key=f"guardar_{indice}", type="primary"):
        # Aplicamos cantidad y precio nuevos; quitamos los que quedaron en 0
        items_nuevos = []
        for item, cant, prec in zip(factura["items"], cantidades, precios):
            if cant > 0:
                item["cantidad"] = cant
                item["precio"] = prec
                item["subtotal"] = prec * cant
                items_nuevos.append(item)
        factura["items"] = items_nuevos
        factura["total"] = sum(it["subtotal"] for it in items_nuevos)

        # Si la factura quedo sin productos, la eliminamos
        if not factura["items"]:
            st.session_state["pendientes"].pop(indice)

        almacen.guardar_pendientes(st.session_state["pendientes"])
        st.session_state["editando"] = None
        st.toast("Cambios guardados", icon="✅")
        st.rerun()

    if col_c.button("Cancelar", key=f"cancelar_{indice}"):
        st.session_state["editando"] = None
        st.rerun()


def pagina_facturas():
    st.title("Facturas")

    pendientes = st.session_state["pendientes"]
    verificadas = estado["facturas"]

    tab_pend, tab_verif = st.tabs([
        f"Facturas ({len(pendientes)})",
        f"Facturas subidas ({len(verificadas)})",
    ])

    # ---------- PESTAÑA 1: FACTURAS (escaneadas, listas para subir) ----------
    with tab_pend:
        if not pendientes:
            st.info("No hay facturas. Escanea una lista en la sección Facturar.")
        else:
            # Accion masiva ARRIBA: subir todas de una vez (comodo si hay muchas)
            if st.button("Subir todas",
                         type="primary", use_container_width=True):
                for factura in pendientes:
                    control_dian.verificar_factura(estado, factura)
                pendientes.clear()                                    # quedan todas subidas
                almacen.guardar_pendientes(pendientes)
                st.toast("Todas las facturas fueron subidas", icon="✅")
                st.rerun()
            st.caption("…o revísalas y súbelas una por una:")

        for i, factura in enumerate(pendientes):
            # Si esta factura esta en modo edicion, mostramos el editor
            if st.session_state["editando"] == i:
                with st.container(border=True):
                    _editar_factura(i, factura)
                continue

            # Tarjeta con la tabla y, DENTRO, los botones de accion centrados
            fecha = factura.get("fecha", "—")
            hora = factura.get("hora", "")
            sello = f"{fecha} · {hora}".strip(" ·")
            titulo = f"Factura · {sello}  ·  {revision.formatear_pesos(factura['total'])}"

            with st.expander(titulo):
                st.dataframe(revision.filas_tabla(factura),
                             hide_index=True, use_container_width=True)
                st.markdown(
                    f"<div style='text-align:right; font-size:18px;'>"
                    f"Total: <b style='color:#2E7D32;'>"
                    f"{revision.formatear_pesos(factura['total'])}</b></div>",
                    unsafe_allow_html=True,
                )

                # Botones pequeños y centrados: las columnas vacias de los
                # extremos empujan el grupo hacia el centro.
                _, b_ver, b_edit, b_del, _ = st.columns([1.5, 2.3, 1.3, 0.8, 2],
                                                        gap="small")

                if b_ver.button("Subir factura", key=f"verificar_{i}",
                                type="primary", use_container_width=True):
                    control_dian.verificar_factura(estado, factura)
                    pendientes.pop(i)                          # sale de Facturas
                    almacen.guardar_pendientes(pendientes)     # guardamos en disco
                    st.toast("Factura subida", icon="✅")
                    st.rerun()

                if b_edit.button("Editar", key=f"editar_{i}", use_container_width=True):
                    st.session_state["editando"] = i
                    st.rerun()

                if b_del.button("🗑️", key=f"borrar_{i}", help="Eliminar factura",
                                use_container_width=True):
                    pendientes.pop(i)
                    almacen.guardar_pendientes(pendientes)
                    st.toast("Factura eliminada", icon="🗑️")
                    st.rerun()

    # ---------- PESTAÑA 2: FACTURAS SUBIDAS (historial) ----------
    with tab_verif:
        if not verificadas:
            st.info("Aún no has subido facturas. Súbelas desde la pestaña Facturas.")

        for i, factura in enumerate(verificadas):
            _tarjeta_factura(factura)

            col_anular, _ = st.columns([2, 6])
            if col_anular.button("Devolver", key=f"anular_{i}",
                                 help="Devuelve la factura a la pestaña Facturas"):
                devuelta = control_dian.anular_factura(estado, i)
                st.session_state["pendientes"].append(devuelta)          # vuelve a Facturas
                almacen.guardar_pendientes(st.session_state["pendientes"])
                st.toast("La factura volvió a Facturas", icon="↩️")
                st.rerun()


# ============================================================
# ENRUTADOR  —  decide que pagina mostrar
# ============================================================
dibujar_menu()
cabecera()

if st.session_state["seccion"] == "Facturar":
    pagina_facturar()
else:
    pagina_facturas()

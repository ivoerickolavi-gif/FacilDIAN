# FacilDIAN

MVP que automatiza la facturacion de una tienda de medicamentos agricolas
y veterinarios: foto de la lista manuscrita -> la IA extrae los productos ->
arma la factura -> el empleado la revisa y la verifica.

## Modulos
1. OCR — foto a productos (Google Gemini)
2. Inventario — productos y precios
3. Armar factura — productos a factura
4. Almacen de verificadas — guarda las facturas verificadas
5. Revision — panel humano de aprobacion

## Stack
Streamlit · Google Gemini 2.5 Flash · JSON local · Streamlit Community Cloud

## Como correr (local)
1. `pip install -r requirements.txt`
2. Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml` y pon tu clave.
3. `streamlit run app.py`

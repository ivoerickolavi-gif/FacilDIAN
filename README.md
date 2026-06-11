# FacilDIAN

MVP que automatiza la facturacion diaria de una tienda de medicamentos
agricolas y veterinarios: foto manuscrita -> productos -> borradores de
factura, respetando topes por factura y el limite diario de la DIAN.

## Los 5 modulos
1. OCR — foto a productos (Google Gemini)
2. Inventario — productos y precios
3. Agrupador — productos a borradores de factura
4. Control DIAN — limite diario acumulado
5. Revision — panel humano de aprobacion

## Stack
Streamlit · Google Gemini 2.0 Flash · JSON local · Streamlit Community Cloud

## Como correr (local)
1. `pip install -r requirements.txt`
2. Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml` y pon tu clave.
3. `streamlit run app.py`

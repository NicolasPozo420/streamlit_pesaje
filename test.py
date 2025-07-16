import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import datetime
import base64
import random

# Reporteria PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

#Email
import smtplib
from email.message import EmailMessage

# Usuarios permitidos
usuarios = {
    "admin": "1234",
    "nicolas": "clave1",
    "claudia": "clave2",
    "luis": "clave3",
    "ana": "clave4"
}

# Codigo Proovedor
proveedores = {
    "P001": "Proveedor A",
    "P002": "Proveedor B",
    "P003": "Proveedor C"
}

# Mostrar logo arriba solo si existe
try:
    img = Image.open("logo.jpeg")
    st.image(img, use_column_width=True)
except FileNotFoundError:
    pass  # Puedes mostrar un texto o logo alternativo aquí si quieres

def login():
    st.title("🔐 Inicio de Sesión")
    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        login_btn = st.form_submit_button("Iniciar sesión")
    if login_btn:
        if usuario in usuarios and usuarios[usuario] == contraseña:
            st.session_state['logueado'] = True
            st.session_state['usuario'] = usuario
            st.success(f"Bienvenido, {usuario} 👋")
        else:
            st.error("❌ Usuario o contraseña incorrectos")
def generar_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 80
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y, "📋 Registro de Pesaje de Leche")
    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Nombre del proveedor: {data['proveedor_nombre']}")
    y -= 25
    c.drawString(50, y, f"Código del proveedor: {data['proveedor_codigo']}")
    y -= 25
    c.drawString(50, y, f"Tipo de leche: {data['tipo']}")
    y -= 25
    c.drawString(50, y, f"Peso capturado: {data['peso']} kg")
    y -= 25
    c.drawString(50, y, f"Fecha y hora: {data['hora']}")
    y -= 50

    # Campos para llenar a mano
    c.setFont("Helvetica", 12)
    c.drawString(50, y, "Nombre del responsable de la empresa: ___________________________")
    y -= 30
    c.drawString(50, y, "Firma del responsable: ___________________________")
    y -= 50
    c.drawString(50, y, "Nombre del proveedor: ___________________________")
    y -= 30
    c.drawString(50, y, "Firma del proveedor: ___________________________")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def get_image_base64(path):
    with open(path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()
    return b64_string

def animacion_caja(tipo):
    # Cambia esta ruta al path absoluto o relativo de tu imagen local
    ruta_imagen_local = "./caja.png"  # ejemplo en Windows
    # o "./mi_caja.png" si está en la misma carpeta que tu script

    # Convierte la imagen a base64
    img_b64 = get_image_base64(ruta_imagen_local)
    # Crea el "data URI" para incrustar la imagen directamente
    caja_url = f"data:image/png;base64,{img_b64}"


    animaciones = {
        "Pequeño": "clasificar-arriba",
        "Mediano": "clasificar-abajo",
        "Grande": "clasificar-derecha"
    }
    animacion = animaciones.get(tipo, "clasificar-arriba")

    html_code = f"""
<style>
@keyframes mover-caja {{
    0% {{ left: -140px; opacity: 1; }}
    100% {{ left: 380px; opacity: 0; }}
}}

@keyframes clasificar-arriba {{
    0%   {{ top: 130px; left: 380px; opacity: 0; }}
    40%  {{ opacity: 1; }}
    100% {{ top: 30px; left: 380px; opacity: 1; }}
}}

@keyframes clasificar-abajo {{
    0%   {{ top: 130px; left: 380px; opacity: 0; }}
    40%  {{ opacity: 1; }}
    100% {{ top: 230px; left: 380px; opacity: 1; }}
}}

@keyframes clasificar-derecha {{
    0%   {{ top: 130px; left: 380px; opacity: 0; }}
    40%  {{ opacity: 1; }}
    100% {{ top: 130px; left: 620px; opacity: 1; }}
}}

.contenedor {{
    position: relative; 
    width: 100%; 
    max-width: 700px; 
    height: 350px; 
    margin: 0 auto; 
    background: #e9f0f7; 
    border-radius: 12px; 
    box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
    overflow: hidden;
}}

.banda {{
    position: absolute;
    bottom: 90px;
    left: 0;
    width: 100%;
    height: 40px;
    background: repeating-linear-gradient(
        45deg,
        #666,
        #666 10px,
        #888 10px,
        #888 20px
    );
    border-radius: 12px;
    box-shadow: inset 0 0 8px rgba(255,255,255,0.3);
}}

.caja-entrando {{
    position: absolute;
    top: 130px;
    left: -140px;
    height: 70px;
    animation: mover-caja 2.5s ease forwards;
    z-index: 10;
}}

.caja-saliendo {{
    position: absolute;
    top: 130px;
    left: 380px;
    height: 70px;
    opacity: 0;
    animation: {animacion} 2.5s 2.5s ease forwards;
    z-index: 10;
}}

.clasificadora {{
    position: absolute;
    top: 120px;
    left: 380px;
    width: 110px;
    height: 90px;
    background-color: #000;
    border-radius: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1.2rem;
    color: white;
    font-weight: bold;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    z-index: 20;
    user-select: none;
}}
</style>

<div class="contenedor">
    <div class="banda"></div>
    <img class="caja-entrando" src="{caja_url}" />
    <img class="caja-saliendo" src="{caja_url}" />
    <div class="clasificadora">Clasificador</div>
</div>
"""

    components.html(html_code, height=370)

def mostrar_contenido(opcion):
    if opcion == "Pesaje":
        st.write("📦 Gestión de registros de pesaje")

        # Asegurar que exista la lista de datos
        if 'datos_cajas' not in st.session_state:
            st.session_state['datos_cajas'] = []

        # FORMULARIO PARA CARGAR DATOS
        with st.form("form_pesaje"):
            cod_proveedor = st.selectbox("🏷️ Código de proveedor:", list(proveedores.keys()))
            tipo = st.selectbox("📦 Tipo de caja:", ["Pequeño", "Mediano", "Grande"])
            simular = st.form_submit_button("▶️ Simular")

        if simular:
            ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            peso_simulado = round(random.uniform(5.0, 30.0), 2)  # genera peso real aleatorio

            # Guarda en la variable Peso_PLC
            st.session_state["Peso_PLC"] = {
                "proveedor_codigo": cod_proveedor,
                "proveedor_nombre": proveedores[cod_proveedor],
                "tipo": tipo,
                "hora": ahora,
                "peso": peso_simulado
            }

            # Agrega a la lista general de datos
            st.session_state["datos_cajas"].append({
                "Proveedor": proveedores[cod_proveedor],
                "Código": cod_proveedor,
                "Tipo": tipo,
                "Hora": ahora,
                "Peso (kg)": peso_simulado
            })

            # Muestra animación
            animacion_caja(tipo)

            # Mostrar recuadro de peso
            st.success(f"⚖️ Peso simulado: **{peso_simulado} kg**")
        if "Peso_PLC" in st.session_state:
            st.markdown("### 📦 Datos actuales de la caja (Peso_PLC)")
            st.json(st.session_state["Peso_PLC"])

            pdf_buffer = generar_pdf(st.session_state["Peso_PLC"])
            st.download_button(
                label="📄 Descargar reporte en PDF",
                data=pdf_buffer,
                file_name="reporte_pesaje.pdf",
                mime="application/pdf"
            )
            st.markdown("### 📧 Enviar PDF por correo")
            destinatario = st.text_input("Correo del destinatario")
            if st.button("📤 Enviar correo"):
                if destinatario and "@" in destinatario:
                    enviado = enviar_pdf_por_correo(pdf_buffer, destinatario)
                    if enviado:
                        st.success("✅ Correo enviado correctamente.")
                else:
                    st.warning("⚠️ Ingresa un correo válido.")

        # Mostrar tabla de historial
        if st.session_state.get("datos_cajas"):
            st.markdown("### 🗃️ Datos simulados de cajas")
            st.table(st.session_state["datos_cajas"])

    elif opcion == "Consulta despachos":
        st.write("🚚 Consultar historial de despachos y guías.")
    elif opcion == "Tendencias":
        st.write("📈 Visualización de tendencias y análisis.")
    elif opcion == "Estado máquina":
        st.write("⚙️ Estado actual y monitoreo de las máquinas.")
def contenido_principal():
    st.sidebar.title("📋 Menú principal")
    opcion = st.sidebar.selectbox(
        "Seleccione una opción:",
        ["Pesaje", "Consulta despachos", "Tendencias", "Estado máquina"]
    )
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Usuario: `{st.session_state['usuario']}`")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state['logueado'] = False
        st.session_state['usuario'] = ""
        st.experimental_rerun()

    st.title(f"📌 {opcion}")
    mostrar_contenido(opcion)
def enviar_pdf_por_correo(pdf_buffer, destinatario, asunto="Reporte de pesaje", mensaje="Adjunto el PDF generado."):
    emisor = "proyectos@esmec-ec.com"
    clave = "1998"  # Usa una contraseña de aplicación (no la normal)

    # Crear el mensaje
    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = emisor
    msg['To'] = destinatario
    msg.set_content(mensaje)

    # Adjuntar el PDF
    pdf_bytes = pdf_buffer.getvalue()
    msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename='reporte_pesaje.pdf')

    # Enviar
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(emisor, clave)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {e}")
        return False
def main():
    if 'logueado' not in st.session_state:
        st.session_state['logueado'] = False
        st.session_state['usuario'] = ""

    if st.session_state['logueado']:
        contenido_principal()
    else:
        login()

if __name__ == '__main__':
    main()

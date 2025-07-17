import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import datetime
import base64
import random
import io
import time
import tempfile

# Reporteria PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Graficas
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

# Usuarios permitidos
usuarios = {
    "admin": "1234",
    "nicolas": "clave1",
    "claudia": "clave2",
    "luis": "clave3",
    "ana": "clave4"
}

# Codigo Proveedor
proveedores = {
    "P001": "Proveedor A",
    "P002": "Proveedor B",
    "P003": "Proveedor C"
}

# Mostrar logo arriba solo si existe
try:
    img = Image.open("logo.jpeg")
    st.image(img, use_container_width =True)
except FileNotFoundError:
    pass

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
            st.rerun()  # ✅ Esto fuerza la recarga con la sesión activa
        else:
            st.error("❌ Usuario o contraseña incorrectos")
            
def animacion_caja(tipo):
    ruta_imagen_local = "./caja.png"
    try:
        with open(ruta_imagen_local, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode()
        caja_url = f"data:image/png;base64,{img_b64}"
    except FileNotFoundError:
        st.warning("Imagen de caja no encontrada")
        return

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

def generar_pdf_tabla(lista_datos):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "📦 Reporte de Despachos Filtrados")
    y -= 30
    c.setFont("Helvetica", 10)

    headers = ["Proveedor", "Código", "Tipo", "Hora", "Peso (kg)"]
    col_x = [50, 150, 230, 300, 420]
    for i, h in enumerate(headers):
        c.drawString(col_x[i], y, h)
    y -= 20
    c.line(50, y + 5, 500, y + 5)
    y -= 15

    for row in lista_datos:
        if y < 100:
            c.showPage()
            y = height - 50
        c.drawString(col_x[0], y, str(row["Proveedor"]))
        c.drawString(col_x[1], y, str(row["Código"]))
        c.drawString(col_x[2], y, str(row["Tipo"]))
        c.drawString(col_x[3], y, str(row["Hora"]))
        c.drawString(col_x[4], y, f"{row['Peso (kg)']} kg")
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer

def mostrar_contenido(opcion):
    if opcion == "Pesaje":
        st.write("📦 Gestión de registros de pesaje")
        if 'datos_cajas' not in st.session_state:
            st.session_state['datos_cajas'] = []

        with st.form("form_pesaje"):
            cod_proveedor = st.selectbox("🏷️ Código de proveedor:", list(proveedores.keys()))
            tipo = st.selectbox("📦 Tipo de caja:", ["Pequeño", "Mediano", "Grande"])
            simular = st.form_submit_button("▶️ Simular")

        if simular:
            ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            peso_simulado = round(random.uniform(5.0, 30.0), 2)
            st.session_state["Peso_PLC"] = {
                "proveedor_codigo": cod_proveedor,
                "proveedor_nombre": proveedores[cod_proveedor],
                "tipo": tipo,
                "hora": ahora,
                "peso": peso_simulado
            }
            st.session_state["datos_cajas"].append({
                "Proveedor": proveedores[cod_proveedor],
                "Código": cod_proveedor,
                "Tipo": tipo,
                "Hora": ahora,
                "Peso (kg)": peso_simulado
            })
            animacion_caja(tipo)
            st.success(f"⚖️ Peso simulado: **{peso_simulado} kg**")

        if "Peso_PLC" in st.session_state:
            st.markdown("### 📦 Datos actuales de la caja (Peso_PLC)")
            st.json(st.session_state["Peso_PLC"])

    elif opcion == "Consulta despachos":
        st.write("🚚 Consultar historial de despachos y guías.") 
        if st.session_state.get("datos_cajas"):
            datos = st.session_state["datos_cajas"]
            st.markdown("### 🔍 Filtros")
            col1, col2, col3 = st.columns(3)
            with col1:
                proveedor_filtro = st.selectbox("Proveedor", ["Todos"] + sorted(set(d["Proveedor"] for d in datos)))
            with col2:
                tipo_filtro = st.selectbox("Tipo de caja", ["Todos", "Pequeño", "Mediano", "Grande"])
            with col3:
                fechas = [datetime.datetime.strptime(d["Hora"], "%Y-%m-%d %H:%M:%S") for d in datos]
                fecha_min = min(fechas)
                fecha_max = max(fechas)
                rango_fechas = st.date_input("Rango de fechas", [fecha_min.date(), fecha_max.date()])

            filtrados = []
            for d in datos:
                fecha = datetime.datetime.strptime(d["Hora"], "%Y-%m-%d %H:%M:%S").date()
                if (proveedor_filtro == "Todos" or d["Proveedor"] == proveedor_filtro) and \
                   (tipo_filtro == "Todos" or d["Tipo"] == tipo_filtro) and \
                   (rango_fechas[0] <= fecha <= rango_fechas[1]):
                    filtrados.append(d)

            st.markdown("### 📦 Registros filtrados")
            st.dataframe(filtrados)

            if filtrados:
                if st.button("📄 Generar reporte en PDF"):
                    buffer = generar_pdf_tabla(filtrados)
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=buffer,
                        file_name="reporte_filtrado.pdf",
                        mime="application/pdf"
                    )
        else:
            st.info("Aún no hay datos registrados.")

    elif opcion == "Tendencias":
        st.write("📈 Visualización de tendencias y análisis.")
        
        if st.session_state.get("datos_cajas"):
            datos = st.session_state["datos_cajas"]
            df = pd.DataFrame(datos)

            st.markdown("### 🔍 Filtros")
            col1, col2, col3 = st.columns(3)

            with col1:
                proveedor_filtro = st.selectbox("Proveedor", ["Todos"] + sorted(df["Proveedor"].unique()))
            with col2:
                tipo_filtro = st.selectbox("Tipo de caja", ["Todos", "Pequeño", "Mediano", "Grande"])
            with col3:
                fechas = pd.to_datetime(df["Hora"])
                fecha_min = fechas.min().date()
                fecha_max = fechas.max().date()
                fecha_inicio, fecha_fin = st.date_input("Rango de fechas", [fecha_min, fecha_max])

            # Aplicar filtros
            df_filtrado = df.copy()
            df_filtrado["Fecha"] = pd.to_datetime(df_filtrado["Hora"]).dt.date
            df_filtrado = df_filtrado[
                (df_filtrado["Fecha"] >= fecha_inicio) &
                (df_filtrado["Fecha"] <= fecha_fin)
            ]
            if proveedor_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Proveedor"] == proveedor_filtro]
            if tipo_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_filtro]

            # --- KPI CARDS ---
            st.markdown("### 📊 Indicadores clave (KPI)")
            total_cajas = len(df_filtrado)
            peso_total = df_filtrado["Peso (kg)"].sum()
            peso_promedio = df_filtrado["Peso (kg)"].mean() if total_cajas > 0 else 0
            colk1, colk2, colk3 = st.columns(3)
            colk1.metric("📦 Total de cajas", total_cajas)
            colk2.metric("⚖️ Peso total", f"{peso_total:.2f} kg")
            colk3.metric("📊 Promedio por caja", f"{peso_promedio:.2f} kg")

            st.markdown("### 📉 Selecciona gráfico para visualizar")
            grafico_opcion = st.selectbox("📊 Tipo de gráfico", [
                "Proveedor vs Peso por tipo de caja",
                "Tendencia diaria por proveedor"
            ])

            if grafico_opcion == "Proveedor vs Peso por tipo de caja":
                fig = px.bar(
                    df_filtrado,
                    x="Proveedor",
                    y="Peso (kg)",
                    color="Tipo",
                    barmode="group",
                    title="Peso entregado por proveedor y tipo de caja"
                )
                st.plotly_chart(fig, use_container_width=True)

            elif grafico_opcion == "Tendencia diaria por proveedor":
                df_agrupado = df_filtrado.groupby(["Fecha", "Proveedor"])["Peso (kg)"].sum().reset_index()
                fig = px.bar(
                    df_agrupado,
                    x="Fecha",
                    y="Peso (kg)",
                    color="Proveedor",
                    barmode="group",
                    title="Peso diario reportado por proveedor"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Mostrar tabla de datos filtrados
            st.markdown("### 📦 Datos filtrados")
            st.dataframe(df_filtrado)

            # Botón para descargar PDF
            if st.button("📄 Descargar reporte con gráfico y tabla"):
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.pagesizes import A4, landscape
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet
                import io

                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
                elementos = []
                estilos = getSampleStyleSheet()
                elementos.append(Paragraph("📄 Reporte de tendencias", estilos['Heading1']))
                elementos.append(Spacer(1, 12))

                # KPIs
                elementos.append(Paragraph(f"Total de cajas: {total_cajas}", estilos['Normal']))
                elementos.append(Paragraph(f"Peso total: {peso_total:.2f} kg", estilos['Normal']))
                elementos.append(Paragraph(f"Peso promedio por caja: {peso_promedio:.2f} kg", estilos['Normal']))
                elementos.append(Spacer(1, 12))

                # NO imagen del gráfico para evitar error en Streamlit Cloud

                # Tabla de datos
                tabla_data = [df_filtrado.columns.tolist()] + df_filtrado.values.tolist()
                tabla = Table(tabla_data)
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.gray),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('FONTNAME', (0,0),(-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0),(-1,0), 12),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.black)
                ]))
                elementos.append(tabla)

                doc.build(elementos)
                buffer.seek(0)

                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=buffer,
                    file_name="reporte_tendencias.pdf",
                    mime="application/pdf"
                )
        else:
            st.info("No hay datos aún. Ingresa primero registros en la sección de Pesaje.")
    elif opcion == "Estado máquina":
        st.write("⚙️ Estado actual y monitoreo de las máquinas.")
        estado_maquina()
        

def contenido_principal():
    st.sidebar.title("📋 Menú principal")
    opcion = st.sidebar.selectbox(
        "Seleccione una opción:",
        ["Pesaje", "Consulta despachos", "Tendencias", "Estado máquina"]
    )
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Usuario: {st.session_state.get('usuario','')}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state['logueado'] = False
        st.session_state['usuario'] = ""
        st.experimental_rerun()

    st.title(f"📌 {opcion}")
    mostrar_contenido(opcion)

def estado_maquina():
    import random
    st.header("⚙️ Estado de la máquina")

    # Estado simulado
    estados = ["En funcionamiento", "En pausa", "En mantenimiento", "Error"]
    estado_actual = random.choice(estados)

    # Datos simulados
    temperatura = random.uniform(40, 90)
    rpm = random.randint(1000, 3000)
    horas_operacion = random.randint(50, 200)
    proximo_mantenimiento = random.randint(1, 30)

    # Mostrar KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Estado", estado_actual)
    col2.metric("Temperatura (°C)", f"{temperatura:.1f}")
    col3.metric("RPM", rpm)
    col4.metric("Horas de operación", horas_operacion)

    st.markdown(f"⏳ **Días para próximo mantenimiento:** {proximo_mantenimiento}")

    # Semáforo simple para estado
    colores = {
        "En funcionamiento": "green",
        "En pausa": "yellow",
        "En mantenimiento": "blue",
        "Error": "red"
    }
    st.markdown(
        f"<div style='width:20px; height:20px; background-color:{colores[estado_actual]}; border-radius:50%;'></div>",
        unsafe_allow_html=True
    )

    # Botones simulados
    if st.button("Pausar máquina"):
        st.info("La máquina ha sido pausada (simulado).")
    if st.button("Reanudar máquina"):
        st.success("La máquina ha sido reanudada (simulado).")
    if st.button("Reiniciar sistema"):
        st.warning("El sistema se está reiniciando (simulado).")





def main():
    if 'logueado' not in st.session_state:
        st.session_state['logueado'] = False
        st.session_state['usuario'] = ""

    if st.session_state['logueado']:
        contenido_principal()
    else:
        login()

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Simulador de Aduanas", page_icon="🚢", layout="wide")
st.title("Simulador de Tiempos de Nacionalización 🚢")

# BARRA LATERAL: Controles de Configuración
st.sidebar.header("⚙️ Configuración del Proceso")

cant_guias = st.sidebar.number_input("Cantidad de Guías", min_value=1, value=707, step=10)
pct_a = st.sidebar.slider("% Anexo A", 0, 100, 70) / 100
pct_b = st.sidebar.slider("% Anexo B", 0, 100, 30) / 100

st.sidebar.subheader("👥 Equipos de Trabajo (Operadores)")
op_valoradores = st.sidebar.number_input("Valoradores", min_value=1, value=6)
op_aux_ops = st.sidebar.number_input("Auxiliares OPS", min_value=1, value=5)
op_gestores = st.sidebar.number_input("Gestores", min_value=1, value=2)

st.sidebar.subheader("🕒 Horarios")
hora_inicio = st.sidebar.time_input("Hora de Inicio", value=pd.to_datetime("08:00").time())

# CÁLCULOS MATEMÁTICOS (Basados en tu hoja "Tiempos específicos")
# Nota: Aquí abstraemos la lógica para demostrar el funcionamiento
tiempo_transferencia = 2.63 * cant_guias / op_aux_ops
tiempo_clasificacion = 40.18 * cant_guias / op_valoradores
tiempo_descarga = 6.16 * cant_guias / op_aux_ops

lead_time_previo = (tiempo_transferencia + tiempo_clasificacion) / 3600 # Convertido a horas
lead_time_vuelo = tiempo_descarga / 3600

# DASHBOARD DE RESULTADOS (Pantalla principal)
st.header("📊 Dashboard de Resultados")

col1, col2, col3 = st.columns(3)
col1.metric("Lead Time: Día Previo", f"{lead_time_previo:.2f} hrs")
col2.metric("Lead Time: Día del Vuelo", f"{lead_time_vuelo:.2f} hrs")
col3.metric("Capacidad Est. (Cuello Botella)", f"{int(cant_guias / 1.2)} guías/día")

st.markdown("---")

# GRÁFICO INTERACTIVO
st.subheader("Distribución del Tiempo por Etapa")
datos_grafico = pd.DataFrame({
    "Etapa": ["Día Previo", "Día del Vuelo", "Día Siguiente"],
    "Lead Time (Horas)": [lead_time_previo, lead_time_vuelo, 9.12] # 9.12 tomado de tu Hoja 3
})

fig = px.bar(datos_grafico, x="Etapa", y="Lead Time (Horas)", color="Etapa", text_auto='.2f')
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)
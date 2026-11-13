import streamlit as st 
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador de Desaduanamiento de carga courier de importación", page_icon="✈️", layout="wide")
st.title("Simulador Operativo de Desaduanamiento Courier ✈️")

# --- 2. PANEL LATERAL (INPUTS) ---
st.sidebar.header("⚙️ Parámetros")
cant_guias = st.sidebar.number_input("Cantidad de Guías a procesar", min_value=1, value=707, step=10)

st.sidebar.header("⚙️ Parámetros de Carga")
cant_guias = st.sidebar.number_input("Cantidad de Guías a procesar", min_value=1, value=707, step=10)
# --- NUEVO INPUT DE PAQUETES ---
cant_paquetes = st.sidebar.number_input("Cantidad de Paquetes a procesar", min_value=1, value=1500, step=50)

col_a, col_b = st.sidebar.columns(2)
pct_a = col_a.number_input("% Tipo A", min_value=0.0, max_value=100.0, value=70.0) / 100
pct_b = col_b.number_input("% Tipo B", min_value=0.0, max_value=100.0, value=30.0) / 100

st.sidebar.header("👥 Equipos de Trabajo")
col_op1, col_op2 = st.sidebar.columns(2)
op_val = col_op1.number_input("Valoradores", min_value=1, value=6)
op_aux = col_op2.number_input("Auxiliares OPS", min_value=1, value=5)
op_ges = col_op1.number_input("Gestores", min_value=1, value=2)
op_fac = col_op2.number_input("Facturadores", min_value=1, value=1)

st.sidebar.header("🕒 Horarios")
hora_inicio = st.sidebar.time_input("Hora inicio jornada", value=pd.to_datetime("08:00").time())
hora_fin = st.sidebar.time_input("Hora fin jornada", value=pd.to_datetime("17:00").time())
horas_descanso = st.sidebar.number_input("Horas de descanso", min_value=0.0, value=1.0, step=0.5)

st.sidebar.header("✈️ Hitos")
hora_transferencia = st.sidebar.time_input("Hora de transferencia", value=pd.to_datetime("08:00").time())
hora_vuelo = st.sidebar.time_input("Hora llegada vuelo", value=pd.to_datetime("08:00").time())

# --- 3. MOTOR DE CÁLCULO (RÉPLICA EXACTA DE GOOGLE SHEETS) ---

# A. Tiempo Disponible
t_disp_seg = ((datetime.combine(datetime.today(), hora_fin) - datetime.combine(datetime.today(), hora_inicio)).total_seconds()) - (horas_descanso * 3600)

# B. CAPA 1: Tiempos Específicos
datos_especificos = [
    # Día Previo
    {"Etapa": "Día previo al vuelo", "Actividad": "Transferencia", "Op": 1, "Setup": 0, "TE_u": 2.63, "Mod": 1},
    {"Etapa": "Día previo al vuelo", "Actividad": "Depuración", "Op": op_aux, "Setup": 63.48, "TE_u": 10.18, "Mod": 1},
    {"Etapa": "Día previo al vuelo", "Actividad": "Adicional (Dep. Anexo C)", "Op": 1, "Setup": 0, "TE_u": 0.86, "Mod": 1},
    {"Etapa": "Día previo al vuelo", "Actividad": "Clasificación aran. (A)", "Op": max(1, op_val // 2), "Setup": 0, "TE_u": 33.85, "Mod": pct_a},
    {"Etapa": "Día previo al vuelo", "Actividad": "Clasificación aran. (B)", "Op": max(1, op_val - (op_val // 2)), "Setup": 0, "TE_u": 40.18, "Mod": pct_b},
    {"Etapa": "Día previo al vuelo", "Actividad": "Registrar DAI Anexo A", "Op": 1, "Setup": 118.74, "TE_u": 0.87, "Mod": pct_a},
    {"Etapa": "Día previo al vuelo", "Actividad": "Registrar DAI Anexo B", "Op": 1, "Setup": 118.74, "TE_u": 0.73, "Mod": pct_b},
    {"Etapa": "Día previo al vuelo", "Actividad": "Registrar DAI Documento", "Op": 1, "Setup": 118.74, "TE_u": 0, "Mod": 1},
    # Día del Vuelo
    {"Etapa": "Día del vuelo", "Actividad": "Aterrizaje", "Op": 1, "Setup": 5400, "TE_u": 0, "Mod": 1},
    {"Etapa": "Día del vuelo", "Actividad": "Checkpoint", "Op": 1, "Setup": 300, "TE_u": 8.16, "Mod": 1},
    {"Etapa": "Día del vuelo", "Actividad": "Descarga ULD", "Op": max(1, op_aux - 1), "Setup": 0, "TE_u": 6.16, "Mod": 1},
    {"Etapa": "Día del vuelo", "Actividad": "Registrar DUA Anexo A", "Op": 1, "Setup": 120, "TE_u": 1.14, "Mod": 1}, 
    {"Etapa": "Día del vuelo", "Actividad": "Registrar DUA Anexo B", "Op": 1, "Setup": 120, "TE_u": 1.38, "Mod": 1},
    {"Etapa": "Día del vuelo", "Actividad": "Registrar DUA Documento", "Op": 1, "Setup": 178.26, "TE_u": 0, "Mod": 1},
    {"Etapa": "Día del vuelo", "Actividad": "Pago de impuestos", "Op": 1, "Setup": 4635.13, "TE_u": 0, "Mod": 1},
    {"Etapa": "Día del vuelo", "Actividad": "Inspección del SENIAT", "Op": 1, "Setup": 0, "TE_u": 7.40, "Mod": 1},
    {"Etapa": "Día del vuelo", "Actividad": "Cargar camión", "Op": op_ges, "Setup": 0, "TE_u": 14.81, "Mod": 1},
    # Día Siguiente
    {"Etapa": "Día siguiente al vuelo", "Actividad": "Validación del pago de imp.", "Op": op_ges, "Setup": 0, "TE_u": 275.81, "Mod": 1},
    {"Etapa": "Día siguiente al vuelo", "Actividad": "Envío de factura digital", "Op": op_fac, "Setup": 0, "TE_u": 16.85, "Mod": 1},
]

df_esp = pd.DataFrame(datos_especificos)
df_esp["Setup Real (s)"] = df_esp["Setup"] / df_esp["Op"]
df_esp["TE Real (s)"] = (df_esp["TE_u"] / df_esp["Op"]) * df_esp["Mod"]

# C. CAPA 2: Tiempos Generales (Agrupaciones MAX y SUM)
def agrupar_tiempos(actividades, metodo="sum"):
    sub = df_esp[df_esp["Actividad"].isin(actividades)]
    if metodo == "sum": return sub["Setup Real (s)"].sum(), sub["TE Real (s)"].sum()
    if metodo == "max": return sub["Setup Real (s)"].max(), sub["TE Real (s)"].max()

datos_generales = [
    {"Etapa": "Día previo al vuelo", "Actividad": "Totalización", **dict(zip(['Setup Real (s)', 'TE Real Acum (s)'], agrupar_tiempos(["Transferencia", "Depuración", "Adicional (Dep. Anexo C)"], "sum")))},
    {"Etapa": "Día previo al vuelo", "Actividad": "Clasificación arancelaria", **dict(zip(['Setup Real (s)', 'TE Real Acum (s)'], agrupar_tiempos(["Clasificación aran. (A)", "Clasificación aran. (B)"], "max")))},
    {"Etapa": "Día previo al vuelo", "Actividad": "Registrar DAI", **dict(zip(['Setup Real (s)', 'TE Real Acum (s)'], agrupar_tiempos(["Registrar DAI Anexo A", "Registrar DAI Anexo B", "Registrar DAI Documento"], "max")))},
    {"Etapa": "Día del vuelo", "Actividad": "Aterrizaje", **dict(zip(['Setup Real (s)', 'TE Real Acum (s)'], agrupar_tiempos(["Aterrizaje"], "sum")))},
    {"Etapa": "Día del vuelo", "Actividad": "Recepción y descarga ULD", **dict(zip(['Setup Real (s)', 'TE Real Acum (s)'], agrupar_tiempos(["Checkpoint", "Descarga ULD"], "sum")))},
    {"Etapa": "Día del vuelo", "Actividad": "Registrar DUA", **dict(zip(['Setup Real (s)', 'TE Real Acum (s)'], agrupar_tiempos(["Registrar DUA Anexo A", "Registrar DUA Anexo B", "Registrar DUA Documento"], "max")))},
    {"Etapa": "Día del vuelo", "Actividad": "Pago de impuestos", **dict(zip(['Setup Real (s)', 'TE Real Acum (s)'], agrupar_tiempos(["Pago de impuestos"], "sum")))},
    {"Etapa": "Día del vuelo", "Actividad": "Liberación aduanal", **dict(zip(['Setup Real (s)', 'TE Real Acum (s)'], agrupar_tiempos(["Inspección del SENIAT", "Cargar camión"], "sum")))},
    {"Etapa": "Día siguiente al vuelo", "Actividad": "Liberación administrativa", **dict(zip(['Setup Real (s)', 'TE Real Acum (s)'], agrupar_tiempos(["Validación del pago de imp.", "Envío de factura digital"], "sum")))}
]
df_gen = pd.DataFrame(datos_generales)

# D. CAPA 3: KPIs (Cálculos de Hoja 3)
def calc_kpi(etapa, factor_guias=1.0):
    df_filtrado = df_gen[df_gen["Etapa"] == etapa]
    t_fijo = df_filtrado["Setup Real (s)"].sum()
    
    # Identificar las actividades agrupadas de Capa 2 que dependen de paquetes
    actividades_paquetes = ["Recepción y descarga ULD", "Liberación aduanal"]
    
    # Separar el TE (Tiempo Estándar) por tipo de dependencia
    te_paquetes = df_filtrado[df_filtrado["Actividad"].isin(actividades_paquetes)]["TE Real Acum (s)"].sum()
    te_guias = df_filtrado[~df_filtrado["Actividad"].isin(actividades_paquetes)]["TE Real Acum (s)"].sum()
    
    # Cálculo del Lead Time (separando la multiplicación de guías y paquetes)
    tiempo_variable_guias = te_guias * (cant_guias * factor_guias)
    tiempo_variable_paquetes = te_paquetes * cant_paquetes
    lt = (t_fijo + tiempo_variable_guias + tiempo_variable_paquetes) / 3600
    
    # Cálculo de Capacidad Máxima (en guías, utilizando una proporción paquetes/guías)
    ratio_paquetes_guia = cant_paquetes / cant_guias if cant_guias > 0 else 1
    te_ponderado = te_guias + (te_paquetes * ratio_paquetes_guia)
    cap = int((t_disp_seg - t_fijo) / te_ponderado) if te_ponderado > 0 else 0
    
    return lt, cap

lt_previo, cap_previo = calc_kpi("Día previo al vuelo")
lt_vuelo, cap_vuelo = calc_kpi("Día del vuelo")
lt_sig, cap_sig = calc_kpi("Día siguiente al vuelo", factor_guias=pct_b) # Solo aplica a proporción Anexo B


# --- 4. DASHBOARD MINIMALISTA (UI) ---
st.markdown("### 📊 Indicadores Clave de Rendimiento (KPIs)")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("📦 **DÍA PREVIO AL VUELO**")
    st.metric("Lead Time Estimado", f"{lt_previo:.2f} hrs")
    st.metric("Capacidad Máxima", f"{cap_previo} guías")
    st.markdown(calcular_fin_estimado(hora_transferencia, lt_previo, horas_descanso, hora_fin), unsafe_allow_html=True)

with col2:
    st.warning("✈️ **DÍA DEL VUELO**")
    st.metric("Lead Time Estimado", f"{lt_vuelo:.2f} hrs")
    st.metric("Capacidad Máxima", f"{cap_vuelo} guías")
    st.markdown(calcular_fin_estimado(hora_vuelo, lt_vuelo, horas_descanso, hora_fin), unsafe_allow_html=True)

with col3:
    st.success("📄 **DÍA SIGUIENTE AL VUELO (Tipo B)**")
    st.metric("Lead Time Estimado", f"{lt_sig:.2f} hrs")
    st.metric("Capacidad Máxima", f"{cap_sig} guías")
    st.markdown(calcular_fin_estimado(hora_inicio, lt_sig, horas_descanso, hora_fin), unsafe_allow_html=True)

st.markdown("---")

# --- 5. GRÁFICO ---
st.markdown("### ⏱️ Proporción de Tiempo Dedicado por Etapa")
df_grafico = pd.DataFrame({"Etapa": ["Día Previo", "Día del Vuelo", "Día Siguiente"], "Lead Time (hrs)": [lt_previo, lt_vuelo, lt_sig]})

fig = px.pie(df_grafico, values='Lead Time (hrs)', names='Etapa', hole=0.5, color_discrete_sequence=['#4C78A8', '#F58518', '#54A24B'])
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- 6. TABLAS DE DATOS (Transparencia Total) ---
st.markdown("### 📑 Desglose Analítico de Tiempos")
with st.expander("Ver Capa 2: Tiempos Generales"):
    st.dataframe(df_gen.style.format({'Setup Real (s)': '{:.2f}', 'TE Real Acum (s)': '{:.3f}'}), use_container_width=True)

with st.expander("Ver Capa 1: Tiempos Específicos"):
    st.dataframe(df_esp.drop(columns=['Mod']).style.format({'Setup': '{:.2f}', 'TE_u': '{:.2f}', 'Setup Real (s)': '{:.2f}', 'TE Real (s)': '{:.3f}'}), use_container_width=True)

import streamlit as st
import pandas as pd

# Configuración de la página responsive
st.set_page_config(
    page_title="Copa Bazzini 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS eSports
st.markdown("""
    <style>
    .stApp { background-color: #0f1117; color: #f0f6fc; }
    .main-title { text-align: center; color: #d4af37; font-size: 2rem; font-weight: 800; }
    .sub-title { text-align: center; color: #8b949e; font-size: 0.9rem; margin-bottom: 20px; }
    .title-lib { color: #d4af37; font-weight: bold; font-size: 1.3rem; }
    .title-sud { color: #70d6ff; font-weight: bold; font-size: 1.3rem; }
    </style>
""", unsafe_allow_html=True)

# Estado global
if 'equipos' not in st.session_state:
    st.session_state.equipos = {
        'A': [f"Equipo A{i}" for i in range(1, 5)],
        'B': [f"Equipo B{i}" for i in range(1, 5)],
        'C': [f"Equipo C{i}" for i in range(1, 5)],
        'D': [f"Equipo D{i}" for i in range(1, 5)],
    }

if 'resultados' not in st.session_state:
    st.session_state.resultados = {}

if 'fase_actual' not in st.session_state:
    st.session_state.fase_actual = 'config'

st.markdown('<p class="main-title">🏆 COPA BAZZINI 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Official eSports Manager — Mobile Version</p>', unsafe_allow_html=True)

# PANTALLA CONFIGURACIÓN
if st.session_state.fase_actual == 'config':
    st.subheader("⚙️ Carga de Equipos")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Grupo A")
        for i in range(4):
            st.session_state.equipos['A'][i] = st.text_input(f"A{i+1}", st.session_state.equipos['A'][i], key=f"in_A_{i}")
        st.markdown("### Grupo B")
        for i in range(4):
            st.session_state.equipos['B'][i] = st.text_input(f"B{i+1}", st.session_state.equipos['B'][i], key=f"in_B_{i}")

    with col2:
        st.markdown("### Grupo C")
        for i in range(4):
            st.session_state.equipos['C'][i] = st.text_input(f"C{i+1}", st.session_state.equipos['C'][i], key=f"in_C_{i}")
        st.markdown("### Grupo D")
        for i in range(4):
            st.session_state.equipos['D'][i] = st.text_input(f"D{i+1}", st.session_state.equipos['D'][i], key=f"in_D_{i}")

    if st.button("🚀 INICIAR COPA BAZZINI 2026", use_container_width=True):
        st.session_state.fase_actual = 'torneo'
        st.rerun()

# PANTALLA TORNEO
else:
    tab_grupos, tab_lib, tab_sud = st.tabs(["📊 Grupos", "🏆 Libertadores", "🥈 Sudamericana"])

    tablas_datos = {g: {eq: {'PTS': 0, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0} 
                       for eq in st.session_state.equipos[g]} for g in ['A', 'B', 'C', 'D']}

    with tab_grupos:
        st.caption("Cargá los goles de cada partido y la tabla se actualiza al instante.")
        for g in ['A', 'B', 'C', 'D']:
            with st.expander(f"⚽ PARTIDOS GRUPO {g}", expanded=True):
                eqs = st.session_state.equipos[g]
                cruces = [
                    (eqs[0], eqs[1]), (eqs[2], eqs[3]),
                    (eqs[0], eqs[2]), (eqs[1], eqs[3]),
                    (eqs[0], eqs[3]), (eqs[1], eqs[2])
                ]
                for idx, (eq1, eq2) in enumerate(cruces):
                    c1, c2, c3, c4 = st.columns([4, 2, 2, 4])
                    c1.markdown(f"**{eq1}**")
                    g1 = c2.text_input("G1", key=f"G_{g}_{idx}_1", label_visibility="collapsed")
                    g2 = c3.text_input("G2", key=f"G_{g}_{idx}_2", label_visibility="collapsed")
                    c4.markdown(f"**{eq2}**")

                    if g1.isdigit() and g2.isdigit():
                        v1, v2 = int(g1), int(g2)
                        tablas_datos[g][eq1]['PJ'] += 1
                        tablas_datos[g][eq2]['PJ'] += 1
                        tablas_datos[g][eq1]['GF'] += v1
                        tablas_datos[g][eq1]['GC'] += v2
                        tablas_datos[g][eq2]['GF'] += v2
                        tablas_datos[g][eq2]['GC'] += v1

                        if v1 > v2:
                            tablas_datos[g][eq1]['PG'] += 1; tablas_datos[g][eq1]['PTS'] += 3; tablas_datos[g][eq2]['PP'] += 1
                        elif v2 > v1:
                            tablas_datos[g][eq2]['PG'] += 1; tablas_datos[g][eq2]['PTS'] += 3; tablas_datos[g][eq1]['PP'] += 1
                        else:
                            tablas_datos[g][eq1]['PE'] += 1; tablas_datos[g][eq1]['PTS'] += 1
                            tablas_datos[g][eq2]['PE'] += 1; tablas_datos[g][eq2]['PTS'] += 1

                        tablas_datos[g][eq1]['DG'] = tablas_datos[g][eq1]['GF'] - tablas_datos[g][eq1]['GC']
                        tablas_datos[g][eq2]['DG'] = tablas_datos[g][eq2]['GF'] - tablas_datos[g][eq2]['GC']

        st.markdown("---")
        st.subheader("📋 TABLAS DE POSICIONES")
        clasificados_lib, clasificados_sud = {}, {}

        for g in ['A', 'B', 'C', 'D']:
            st.markdown(f"**Grupo {g}**")
            df = pd.DataFrame.from_dict(tablas_datos[g], orient='index')
            df = df.sort_values(by=['PTS', 'DG', 'GF'], ascending=False)
            st.dataframe(df, use_container_width=True)

            clasificados_lib[g] = [df.index[0], df.index[1]]
            clasificados_sud[g] = [df.index[2], df.index[3]]

    with tab_lib:
        st.markdown('<p class="title-lib">🏆 COPA LIBERTADORES</p>', unsafe_allow_html=True)
        st.markdown("#### 🥇 Cuartos de Final")
        cruces_lib = [
            (clasificados_lib['A'][0], clasificados_lib['B'][1]),
            (clasificados_lib['C'][0], clasificados_lib['D'][1]),
            (clasificados_lib['B'][0], clasificados_lib['A'][1]),
            (clasificados_lib['D'][0], clasificados_lib['C'][1])
        ]
        ganadores_cuartos_lib = []
        for idx, (eq1, eq2) in enumerate(cruces_lib):
            st.markdown(f"**Llave {idx+1}:** {eq1} vs {eq2}")
            c1, c2, c3, c4 = st.columns(4)
            i1 = c1.text_input("Ida 1", key=f"L_C_{idx}_i1")
            i2 = c2.text_input("Ida 2", key=f"L_C_{idx}_i2")
            v1 = c3.text_input("Vue 1", key=f"L_C_{idx}_v1")
            v2 = c4.text_input("Vue 2", key=f"L_C_{idx}_v2")
            
            tot1 = (int(i1) if i1.isdigit() else 0) + (int(v1) if v1.isdigit() else 0)
            tot2 = (int(i2) if i2.isdigit() else 0) + (int(v2) if v2.isdigit() else 0)
            
            if tot1 > tot2: ganadores_cuartos_lib.append(eq1)
            elif tot2 > tot1: ganadores_cuartos_lib.append(eq2)
            else: ganadores_cuartos_lib.append("Por definir")

        st.markdown("#### 🔥 Semifinales")
        col_s1, col_s2 = st.columns(2)
        col_s1.info(f"**Semi 1:**\n{ganadores_cuartos_lib[0]} vs {ganadores_cuartos_lib[1]}")
        col_s2.info(f"**Semi 2:**\n{ganadores_cuartos_lib[2]} vs {ganadores_cuartos_lib[3]}")

    with tab_sud:
        st.markdown('<p class="title-sud">🥈 COPA SUDAMERICANA</p>', unsafe_allow_html=True)
        st.markdown("#### 🟦 Cuartos de Final")
        cruces_sud = [
            (clasificados_sud['A'][0], clasificados_sud['B'][1]),
            (clasificados_sud['C'][0], clasificados_sud['D'][1]),
            (clasificados_sud['B'][0], clasificados_sud['A'][1]),
            (clasificados_sud['D'][0], clasificados_sud['C'][1])
        ]
        ganadores_cuartos_sud = []
        for idx, (eq1, eq2) in enumerate(cruces_sud):
            st.markdown(f"**Llave {idx+1}:** {eq1} vs {eq2}")
            c1, c2, c3, c4 = st.columns(4)
            i1 = c1.text_input("Ida 1", key=f"S_C_{idx}_i1")
            i2 = c2.text_input("Ida 2", key=f"S_C_{idx}_i2")
            v1 = c3.text_input("Vue 1", key=f"S_C_{idx}_v1")
            v2 = c4.text_input("Vue 2", key=f"S_C_{idx}_v2")
            
            tot1 = (int(i1) if i1.isdigit() else 0) + (int(v1) if v1.isdigit() else 0)
            tot2 = (int(i2) if i2.isdigit() else 0) + (int(v2) if v2.isdigit() else 0)
            
            if tot1 > tot2: ganadores_cuartos_sud.append(eq1)
            elif tot2 > tot1: ganadores_cuartos_sud.append(eq2)
            else: ganadores_cuartos_sud.append("Por definir")

        st.markdown("#### 🔥 Semifinales")
        col_s1, col_s2 = st.columns(2)
        col_s1.success(f"**Semi 1:**\n{ganadores_cuartos_sud[0]} vs {ganadores_cuartos_sud[1]}")
        col_s2.success(f"**Semi 2:**\n{ganadores_cuartos_sud[2]} vs {ganadores_cuartos_sud[3]}")

    st.markdown("---")
    if st.button("⚙️ Volver a Configurar Equipos"):
        st.session_state.fase_actual = 'config'
        st.rerun()

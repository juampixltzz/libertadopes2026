import streamlit as st
import pandas as pd
import json

# Configuración Responsive Estricta
st.set_page_config(
    page_title="Copa Bazzini 2026",
    page_icon="🏆",
    layout="centered", # Centered funciona mucho mejor en móviles
    initial_sidebar_state="collapsed"
)

# CSS Custom de alta densidad para pantalla táctil
st.markdown("""
    <style>
    /* Fondo Dark eSports */
    .stApp { background-color: #0c0e14; color: #f0f6fc; }
    
    /* Header compacto */
    .title-box {
        text-align: center;
        padding: 5px 0px 10px 0px;
    }
    .main-title { color: #d4af37; font-size: 1.5rem; font-weight: 900; margin: 0; letter-spacing: 1px; }
    .sub-title { color: #6e7681; font-size: 0.75rem; margin-0; text-transform: uppercase; }

    /* Achicar espaciados por defecto de Streamlit en móviles */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.4rem !important; }
    
    /* Inputs de marcadores súper compactos y centrados */
    div[data-baseweb="input"] input {
        text-align: center !important;
        font-weight: bold !important;
        color: #d4af37 !important;
        background-color: #161b22 !important;
        font-size: 1rem !important;
        padding: 4px !important;
    }
    
    /* Pestañas reducidas para dedo */
    button[data-baseweb="tab"] {
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
        font-weight: bold !important;
    }

    /* Títulos de copas */
    .title-lib { color: #d4af37; font-weight: 800; font-size: 1.1rem; text-align: center; margin-bottom: 8px; }
    .title-sud { color: #70d6ff; font-weight: 800; font-size: 1.1rem; text-align: center; margin-bottom: 8px; }

    /* Tarjetas de partidos */
    .match-row {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 6px 10px;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Estado inicial
if 'equipos' not in st.session_state:
    st.session_state.equipos = {
        'A': [f"Equipo A{i}" for i in range(1, 5)],
        'B': [f"Equipo B{i}" for i in range(1, 5)],
        'C': [f"Equipo C{i}" for i in range(1, 5)],
        'D': [f"Equipo D{i}" for i in range(1, 5)],
    }

if 'fase_actual' not in st.session_state:
    st.session_state.fase_actual = 'config'

# Encabezado Móvil
st.markdown("""
    <div class="title-box">
        <p class="main-title">🏆 COPA BAZZINI 2026</p>
        <p class="sub-title">Mobile Tournament Manager</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# PANTALLA 1: CONFIGURACIÓN RÁPIDA DE EQUIPOS
# ==========================================
if st.session_state.fase_actual == 'config':
    st.subheader("⚙️ Equipos Participantes")
    st.caption("Cambiá los nombres de los 16 equipos:")

    for g in ['A', 'B', 'C', 'D']:
        with st.expander(f"📌 Grupo {g}", expanded=(g == 'A')):
            c1, c2 = st.columns(2)
            for i in range(4):
                col = c1 if i < 2 else c2
                st.session_state.equipos[g][i] = col.text_input(
                    f"Eq {i+1}", 
                    st.session_state.equipos[g][i], 
                    key=f"cfg_{g}_{i}",
                    label_visibility="collapsed"
                )

    st.markdown("---")
    if st.button("🚀 INICIAR TORNEO", use_container_width=True, type="primary"):
        st.session_state.fase_actual = 'torneo'
        st.rerun()

# ==========================================
# PANTALLA 2: DASHBOARD TORNEO (RESPONSIVE)
# ==========================================
else:
    tab_grupos, tab_lib, tab_sud = st.tabs(["📊 Grupos", "🏆 Libertadores", "🥈 Sudamericana"])

    # Estructura de almacenamiento de datos de la tabla
    tablas_datos = {g: {eq: {'PTS': 0, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0} 
                       for eq in st.session_state.equipos[g]} for g in ['A', 'B', 'C', 'D']}

    # ------------------------------------------
    # TAB 1: GRUPOS & CRUCES
    # ------------------------------------------
    with tab_grupos:
        for g in ['A', 'B', 'C', 'D']:
            with st.expander(f"⚽ Partidos - Grupo {g}", expanded=(g == 'A')):
                eqs = st.session_state.equipos[g]
                cruces = [
                    (eqs[0], eqs[1]), (eqs[2], eqs[3]),
                    (eqs[0], eqs[2]), (eqs[1], eqs[3]),
                    (eqs[0], eqs[3]), (eqs[1], eqs[2])
                ]
                for idx, (eq1, eq2) in enumerate(cruces):
                    c1, c2, c3, c4 = st.columns([4, 2, 2, 4])
                    c1.markdown(f"<div style='text-align:right; font-size:0.85rem; font-weight:bold;'>{eq1}</div>", unsafe_allow_html=True)
                    g1 = c2.text_input("G1", key=f"G_{g}_{idx}_1", label_visibility="collapsed")
                    g2 = c3.text_input("G2", key=f"G_{g}_{idx}_2", label_visibility="collapsed")
                    c4.markdown(f"<div style='font-size:0.85rem; font-weight:bold;'>{eq2}</div>", unsafe_allow_html=True)

                    if g1.isdigit() and g2.isdigit():
                        v1, v2 = int(g1), int(g2)
                        tablas_datos[g][eq1]['PJ'] += 1; tablas_datos[g][eq2]['PJ'] += 1
                        tablas_datos[g][eq1]['GF'] += v1; tablas_datos[g][eq1]['GC'] += v2
                        tablas_datos[g][eq2]['GF'] += v2; tablas_datos[g][eq2]['GC'] += v1

                        if v1 > v2:
                            tablas_datos[g][eq1]['PG'] += 1; tablas_datos[g][eq1]['PTS'] += 3; tablas_datos[g][eq2]['PP'] += 1
                        elif v2 > v1:
                            tablas_datos[g][eq2]['PG'] += 1; tablas_datos[g][eq2]['PTS'] += 3; tablas_datos[g][eq1]['PP'] += 1
                        else:
                            tablas_datos[g][eq1]['PE'] += 1; tablas_datos[g][eq1]['PTS'] += 1
                            tablas_datos[g][eq2]['PE'] += 1; tablas_datos[g][eq2]['PTS'] += 1

                        tablas_datos[g][eq1]['DG'] = tablas_datos[g][eq1]['GF'] - tablas_datos[g][eq1]['GC']
                        tablas_datos[g][eq2]['DG'] = tablas_datos[g][eq2]['GF'] - tablas_datos[g][eq2]['GC']

        st.markdown("<p style='font-weight:bold; margin-top:15px;'>📋 TABLAS EN VIVO</p>", unsafe_allow_html=True)
        clasificados_lib, clasificados_sud = {}, {}

        for g in ['A', 'B', 'C', 'D']:
            st.caption(f"Grupo {g}")
            df = pd.DataFrame.from_dict(tablas_datos[g], orient='index')
            df = df.sort_values(by=['PTS', 'DG', 'GF'], ascending=False)
            
            # Tabla optimizada sin columnas innecesarias en cel
            st.dataframe(df[['PTS', 'PJ', 'DG', 'GF', 'GC']], use_container_width=True)

            clasificados_lib[g] = [df.index[0], df.index[1]]
            clasificados_sud[g] = [df.index[2], df.index[3]]

    # ------------------------------------------
    # TAB 2: LIBERTADORES (LLAVES MÓVILES)
    # ------------------------------------------
    with tab_lib:
        st.markdown('<p class="title-lib">🏆 COPA LIBERTADORES</p>', unsafe_allow_html=True)
        cruces_lib = [
            (clasificados_lib['A'][0], clasificados_lib['B'][1]),
            (clasificados_lib['C'][0], clasificados_lib['D'][1]),
            (clasificados_lib['B'][0], clasificados_lib['A'][1]),
            (clasificados_lib['D'][0], clasificados_lib['C'][1])
        ]
        
        ganadores_cuartos_lib = []
        with st.expander("🥇 Cuartos de Final (Ida y Vuelta)", expanded=True):
            for idx, (eq1, eq2) in enumerate(cruces_lib):
                st.markdown(f"**Llave {idx+1}:** <span style='color:#d4af37'>{eq1}</span> vs <span style='color:#d4af37'>{eq2}</span>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                i1 = c1.text_input("I1", key=f"L_C_{idx}_i1", placeholder="Ida L", label_visibility="collapsed")
                i2 = c2.text_input("I2", key=f"L_C_{idx}_i2", placeholder="Ida V", label_visibility="collapsed")
                v1 = c3.text_input("V1", key=f"L_C_{idx}_v1", placeholder="Vue L", label_visibility="collapsed")
                v2 = c4.text_input("V2", key=f"L_C_{idx}_v2", placeholder="Vue V", label_visibility="collapsed")
                
                tot1 = (int(i1) if i1.isdigit() else 0) + (int(v1) if v1.isdigit() else 0)
                tot2 = (int(i2) if i2.isdigit() else 0) + (int(v2) if v2.isdigit() else 0)
                
                if tot1 > tot2: ganadores_cuartos_lib.append(eq1)
                elif tot2 > tot1: ganadores_cuartos_lib.append(eq2)
                else: ganadores_cuartos_lib.append("Por definir")
                st.markdown("<hr style='margin:4px 0px; border-color:#262a36;'>", unsafe_allow_html=True)

        st.markdown("#### 🔥 Semifinales")
        st.info(f"**Semi 1:** {ganadores_cuartos_lib[0]} vs {ganadores_cuartos_lib[1]}")
        st.info(f"**Semi 2:** {ganadores_cuartos_lib[2]} vs {ganadores_cuartos_lib[3]}")

    # ------------------------------------------
    # TAB 3: SUDAMERICANA (LLAVES MÓVILES)
    # ------------------------------------------
    with tab_sud:
        st.markdown('<p class="title-sud">🥈 COPA SUDAMERICANA</p>', unsafe_allow_html=True)
        cruces_sud = [
            (clasificados_sud['A'][0], clasificados_sud['B'][1]),
            (clasificados_sud['C'][0], clasificados_sud['D'][1]),
            (clasificados_sud['B'][0], clasificados_sud['A'][1]),
            (clasificados_sud['D'][0], clasificados_sud['C'][1])
        ]
        
        ganadores_cuartos_sud = []
        with st.expander("🟦 Cuartos de Final (Ida y Vuelta)", expanded=True):
            for idx, (eq1, eq2) in enumerate(cruces_sud):
                st.markdown(f"**Llave {idx+1}:** <span style='color:#70d6ff'>{eq1}</span> vs <span style='color:#70d6ff'>{eq2}</span>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                i1 = c1.text_input("I1", key=f"S_C_{idx}_i1", placeholder="Ida L", label_visibility="collapsed")
                i2 = c2.text_input("I2", key=f"S_C_{idx}_i2", placeholder="Ida V", label_visibility="collapsed")
                v1 = c3.text_input("V1", key=f"S_C_{idx}_v1", placeholder="Vue L", label_visibility="collapsed")
                v2 = c4.text_input("V2", key=f"S_C_{idx}_v2", placeholder="Vue V", label_visibility="collapsed")
                
                tot1 = (int(i1) if i1.isdigit() else 0) + (int(v1) if v1.isdigit() else 0)
                tot2 = (int(i2) if i2.isdigit() else 0) + (int(v2) if v2.isdigit() else 0)
                
                if tot1 > tot2: ganadores_cuartos_sud.append(eq1)
                elif tot2 > tot1: ganadores_cuartos_sud.append(eq2)
                else: ganadores_cuartos_sud.append("Por definir")
                st.markdown("<hr style='margin:4px 0px; border-color:#262a36;'>", unsafe_allow_html=True)

        st.markdown("#### 🔥 Semifinales")
        st.success(f"**Semi 1:** {ganadores_cuartos_sud[0]} vs {ganadores_cuartos_sud[1]}")
        st.success(f"**Semi 2:** {ganadores_cuartos_sud[2]} vs {ganadores_cuartos_sud[3]}")

    # ------------------------------------------
    # FOOTER Y ACCIONES MÓVILES
    # ------------------------------------------
    st.markdown("---")
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        if st.button("⚙️ Editar Equipos", use_container_width=True):
            st.session_state.fase_actual = 'config'
            st.rerun()
    with c_f2:
        if st.button("🔄 Reiniciar Todo", use_container_width=True):
            st.session_state.clear()
            st.rerun()

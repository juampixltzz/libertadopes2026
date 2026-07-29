import streamlit as st
import pandas as pd

# Configuración Responsive Centrada para Móviles
st.set_page_config(
    page_title="Copa Bazzini 2026",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS de Alta Densidad eSports
st.markdown("""
    <style>
    .stApp { background-color: #0c0e14; color: #f0f6fc; }
    
    .header-container {
        text-align: center;
        padding: 8px 0 12px 0;
        border-bottom: 2px solid #21262d;
        margin-bottom: 12px;
    }
    .app-title { color: #d4af37; font-size: 1.5rem; font-weight: 900; margin: 0; letter-spacing: 1px; }
    .app-subtitle { color: #8b949e; font-size: 0.7rem; margin-top: 2px; text-transform: uppercase; }

    .block-container { padding-top: 0.6rem !important; padding-bottom: 2rem !important; }
    
    /* Inputs de Marcador */
    div[data-baseweb="input"] input {
        text-align: center !important;
        font-weight: 800 !important;
        color: #d4af37 !important;
        background-color: #0d0f14 !important;
        border-radius: 6px !important;
        font-size: 1rem !important;
        padding: 2px 4px !important;
    }

    /* Badges de Títulos */
    .badge-lib { background-color: #d4af37; color: #000; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }
    .badge-sud { background-color: #70d6ff; color: #000; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }

    /* Tarjetas de Eliminatorias */
    .bracket-card-lib {
        background-color: #161b22;
        border-left: 4px solid #d4af37;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 10px;
    }
    .bracket-card-sud {
        background-color: #161b22;
        border-left: 4px solid #70d6ff;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 10px;
    }
    .global-badge {
        background-color: #21262d;
        color: #f0f6fc;
        font-size: 0.75rem;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
        float: right;
    }
    </style>
""", unsafe_allow_html=True)

# Estado de Equipos
if 'equipos' not in st.session_state:
    st.session_state.equipos = {
        'A': [f"Equipo A{i}" for i in range(1, 5)],
        'B': [f"Equipo B{i}" for i in range(1, 5)],
        'C': [f"Equipo C{i}" for i in range(1, 5)],
        'D': [f"Equipo D{i}" for i in range(1, 5)],
    }

if 'fase_actual' not in st.session_state:
    st.session_state.fase_actual = 'config'

# Header
st.markdown("""
    <div class="header-container">
        <div class="app-title">🏆 COPA BAZZINI 2026</div>
        <div class="app-subtitle">Mobile Tournament Manager</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 1. PANTALLA CONFIGURACIÓN
# ==========================================
if st.session_state.fase_actual == 'config':
    st.subheader("⚙️ Configuración de Equipos")
    grupo_sel = st.radio("Editar Grupo:", ["Grupo A", "Grupo B", "Grupo C", "Grupo D"], horizontal=True)
    g_key = grupo_sel[-1]

    for i in range(4):
        st.session_state.equipos[g_key][i] = st.text_input(
            f"Equipo {i+1}", 
            st.session_state.equipos[g_key][i], 
            key=f"cfg_{g_key}_{i}"
        )

    st.markdown("---")
    if st.button("🚀 EMPEZAR TORNEO", use_container_width=True, type="primary"):
        st.session_state.fase_actual = 'torneo'
        st.rerun()

# ==========================================
# 2. DASHBOARD TORNEO
# ==========================================
else:
    tab_grupos, tab_lib, tab_sud = st.tabs(["📊 Grupos", "🏆 Libertadores", "🥈 Sudamericana"])

    tablas_datos = {g: {eq: {'PTS': 0, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0} 
                       for eq in st.session_state.equipos[g]} for g in ['A', 'B', 'C', 'D']}

    # ------------------------------------------
    # TAB 1: GRUPOS & CRUCES
    # ------------------------------------------
    with tab_grupos:
        g_selected = st.selectbox("📌 Seleccionar Grupo:", ["Grupo A", "Grupo B", "Grupo C", "Grupo D"], key="sb_grupo")
        g = g_selected[-1]

        st.markdown(f"#### ⚽ Partidos del Grupo {g}")
        for g_code in ['A', 'B', 'C', 'D']:
            eqs_c = st.session_state.equipos[g_code]
            cruces_c = [
                (eqs_c[0], eqs_c[1]), (eqs_c[2], eqs_c[3]),
                (eqs_c[0], eqs_c[2]), (eqs_c[1], eqs_c[3]),
                (eqs_c[0], eqs_c[3]), (eqs_c[1], eqs_c[2])
            ]
            for idx_c, (eq1_c, eq2_c) in enumerate(cruces_c):
                if g_code == g:
                    col1, col2, col3, col4 = st.columns([4, 2, 2, 4])
                    col1.markdown(f"<div style='text-align:right; font-weight:bold; font-size:0.85rem;'>{eq1_c}</div>", unsafe_allow_html=True)
                    g1_in = col2.text_input("G1", key=f"G_{g_code}_{idx_c}_1", label_visibility="collapsed")
                    g2_in = col3.text_input("G2", key=f"G_{g_code}_{idx_c}_2", label_visibility="collapsed")
                    col4.markdown(f"<div style='font-weight:bold; font-size:0.85rem;'>{eq2_c}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:2px 0; border-color:#21262d;'>", unsafe_allow_html=True)
                else:
                    g1_in = st.session_state.get(f"G_{g_code}_{idx_c}_1", "")
                    g2_in = st.session_state.get(f"G_{g_code}_{idx_c}_2", "")

                if g1_in.isdigit() and g2_in.isdigit():
                    v1, v2 = int(g1_in), int(g2_in)
                    tablas_datos[g_code][eq1_c]['PJ'] += 1; tablas_datos[g_code][eq2_c]['PJ'] += 1
                    tablas_datos[g_code][eq1_c]['GF'] += v1; tablas_datos[g_code][eq1_c]['GC'] += v2
                    tablas_datos[g_code][eq2_c]['GF'] += v2; tablas_datos[g_code][eq2_c]['GC'] += v1

                    if v1 > v2:
                        tablas_datos[g_code][eq1_c]['PG'] += 1; tablas_datos[g_code][eq1_c]['PTS'] += 3; tablas_datos[g_code][eq2_c]['PP'] += 1
                    elif v2 > v1:
                        tablas_datos[g_code][eq2_c]['PG'] += 1; tablas_datos[g_code][eq2_c]['PTS'] += 3; tablas_datos[g_code][eq1_c]['PP'] += 1
                    else:
                        tablas_datos[g_code][eq1_c]['PE'] += 1; tablas_datos[g_code][eq1_c]['PTS'] += 1
                        tablas_datos[g_code][eq2_c]['PE'] += 1; tablas_datos[g_code][eq2_c]['PTS'] += 1

                    tablas_datos[g_code][eq1_c]['DG'] = tablas_datos[g_code][eq1_c]['GF'] - tablas_datos[g_code][eq1_c]['GC']
                    tablas_datos[g_code][eq2_c]['DG'] = tablas_datos[g_code][eq2_c]['GF'] - tablas_datos[g_code][eq2_c]['GC']

        st.markdown(f"#### 📋 Posiciones - Grupo {g}")
        df = pd.DataFrame.from_dict(tablas_datos[g], orient='index')
        df = df.sort_values(by=['PTS', 'DG', 'GF'], ascending=False)
        st.dataframe(df[['PTS', 'PJ', 'DG', 'GF', 'GC']], use_container_width=True)

        clasificados_lib, clasificados_sud = {}, {}
        for g_c in ['A', 'B', 'C', 'D']:
            df_c = pd.DataFrame.from_dict(tablas_datos[g_c], orient='index')
            df_c = df_c.sort_values(by=['PTS', 'DG', 'GF'], ascending=False)
            clasificados_lib[g_c] = [df_c.index[0], df_c.index[1]]
            clasificados_sud[g_c] = [df_c.index[2], df_c.index[3]]

    # Función auxiliar para renderizar cada llave súper clara
    def renderizar_llave(copa_prefix, idx, eq1, eq2, es_doble=True):
        st.markdown(f"<div class='bracket-card-{copa_prefix.lower()}'>", unsafe_allow_html=True)
        
        i1 = st.session_state.get(f"{copa_prefix}_{idx}_i1", "")
        i2 = st.session_state.get(f"{copa_prefix}_{idx}_i2", "")
        v1 = st.session_state.get(f"{copa_prefix}_{idx}_v1", "") if es_doble else "0"
        v2 = st.session_state.get(f"{copa_prefix}_{idx}_v2", "") if es_doble else "0"

        tot1 = (int(i1) if i1.isdigit() else 0) + (int(v1) if v1.isdigit() else 0)
        tot2 = (int(i2) if i2.isdigit() else 0) + (int(v2) if v2.isdigit() else 0)

        ganador = "Por definir"
        if (i1.isdigit() and i2.isdigit()) and (not es_doble or (v1.isdigit() and v2.isdigit())):
            if tot1 > tot2: ganador = eq1
            elif tot2 > tot1: ganador = eq2
            else: ganador = f"{eq1} (Penalties)"

        # Estilos de ganadores
        st1 = "color:#2ea44f; font-weight:bold;" if ganador == eq1 else "font-weight:bold;"
        st2 = "color:#2ea44f; font-weight:bold;" if ganador == eq2 else "font-weight:bold;"

        st.markdown(f"""
            <div style='margin-bottom:6px;'>
                <span style='font-size:0.8rem; color:#8b949e;'>Llave {idx+1}</span>
                <span class='global-badge'>Global: {tot1} - {tot2}</span>
            </div>
            <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
                <span style='{st1}'>{eq1}</span>
                <span style='{st2}'>{eq2}</span>
            </div>
        """, unsafe_allow_html=True)

        if es_doble:
            c1, c2, c3, c4 = st.columns(4)
            c1.text_input("I1", key=f"{copa_prefix}_{idx}_i1", placeholder="Ida 1", label_visibility="collapsed")
            c2.text_input("I2", key=f"{copa_prefix}_{idx}_i2", placeholder="Ida 2", label_visibility="collapsed")
            c3.text_input("V1", key=f"{copa_prefix}_{idx}_v1", placeholder="Vue 1", label_visibility="collapsed")
            c4.text_input("V2", key=f"{copa_prefix}_{idx}_v2", placeholder="Vue 2", label_visibility="collapsed")
        else:
            c1, c2 = st.columns(2)
            c1.text_input("I1", key=f"{copa_prefix}_{idx}_i1", placeholder="Final 1", label_visibility="collapsed")
            c2.text_input("I2", key=f"{copa_prefix}_{idx}_i2", placeholder="Final 2", label_visibility="collapsed")

        st.markdown("</div>", unsafe_allow_html=True)
        return ganador

    # ------------------------------------------
    # TAB 2: COPA LIBERTADORES
    # ------------------------------------------
    with tab_lib:
        st.markdown('<span class="badge-lib">🏆 COPA LIBERTADORES</span>', unsafe_allow_html=True)
        st.write("")
        
        sub_lib_c, sub_lib_s, sub_lib_f = st.tabs(["🥇 Cuartos", "🔥 Semis", "👑 Final"])

        cruces_lib = [
            (clasificados_lib['A'][0], clasificados_lib['B'][1]),
            (clasificados_lib['C'][0], clasificados_lib['D'][1]),
            (clasificados_lib['B'][0], clasificados_lib['A'][1]),
            (clasificados_lib['D'][0], clasificados_lib['C'][1])
        ]
        
        ganadores_cuartos_lib = []
        with sub_lib_c:
            for idx, (eq1, eq2) in enumerate(cruces_lib):
                g = renderizar_llave("LIB_C", idx, eq1, eq2, es_doble=True)
                ganadores_cuartos_lib.append(g)

        ganadores_semis_lib = []
        with sub_lib_s:
            s_eq1, s_eq2 = ganadores_cuartos_lib[0], ganadores_cuartos_lib[1]
            s_eq3, s_eq4 = ganadores_cuartos_lib[2], ganadores_cuartos_lib[3]
            
            g1 = renderizar_llave("LIB_S", 0, s_eq1, s_eq2, es_doble=True)
            g2 = renderizar_llave("LIB_S", 1, s_eq3, s_eq4, es_doble=True)
            ganadores_semis_lib.extend([g1, g2])

        with sub_lib_f:
            f_eq1, f_eq2 = ganadores_semis_lib[0], ganadores_semis_lib[1]
            campeon = renderizar_llave("LIB_F", 0, f_eq1, f_eq2, es_doble=False)
            if campeon != "Por definir":
                st.balloons()
                st.success(f"🏆 ¡CAMPEÓN COPA LIBERTADORES 2026: {campeon}! 🏆")

    # ------------------------------------------
    # TAB 3: COPA SUDAMERICANA
    # ------------------------------------------
    with tab_sud:
        st.markdown('<span class="badge-sud">🥈 COPA SUDAMERICANA</span>', unsafe_allow_html=True)
        st.write("")

        sub_sud_c, sub_sud_s, sub_sud_f = st.tabs(["🟦 Cuartos", "🔥 Semis", "👑 Final"])

        cruces_sud = [
            (clasificados_sud['A'][2], clasificados_sud['B'][3]),
            (clasificados_sud['C'][2], clasificados_sud['D'][3]),
            (clasificados_sud['B'][2], clasificados_sud['A'][3]),
            (clasificados_sud['D'][2], clasificados_sud['C'][3])
        ]
        
        ganadores_cuartos_sud = []
        with sub_sud_c:
            for idx, (eq1, eq2) in enumerate(cruces_sud):
                g = renderizar_llave("SUD_C", idx, eq1, eq2, es_doble=True)
                ganadores_cuartos_sud.append(g)

        ganadores_semis_sud = []
        with sub_sud_s:
            s_eq1, s_eq2 = ganadores_cuartos_sud[0], ganadores_cuartos_sud[1]
            s_eq3, s_eq4 = ganadores_cuartos_sud[2], ganadores_cuartos_sud[3]
            
            g1 = renderizar_llave("SUD_S", 0, s_eq1, s_eq2, es_doble=True)
            g2 = renderizar_llave("SUD_S", 1, s_eq3, s_eq4, es_doble=True)
            ganadores_semis_sud.extend([g1, g2])

        with sub_sud_f:
            f_eq1, f_eq2 = ganadores_semis_sud[0], ganadores_semis_sud[1]
            campeon_sud = renderizar_llave("SUD_F", 0, f_eq1, f_eq2, es_doble=False)
            if campeon_sud != "Por definir":
                st.balloons()
                st.info(f"🥈 ¡CAMPEÓN COPA SUDAMERICANA 2026: {campeon_sud}! 🥈")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("⚙️ Editar Equipos", use_container_width=True):
            st.session_state.fase_actual = 'config'
            st.rerun()
    with col_b:
        if st.button("🔄 Reiniciar Torneo", use_container_width=True):
            st.session_state.clear()
            st.rerun()

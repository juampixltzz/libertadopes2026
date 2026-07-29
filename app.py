import streamlit as st
import pandas as pd

# Configuración Responsive Centrada para Móviles
st.set_page_config(
    page_title="Copa Bazzini 2026",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Custom de Alta Densidad y Estética eSports Móvil
st.markdown("""
    <style>
    /* Fondo General */
    .stApp { background-color: #0d0f14; color: #f0f6fc; }
    
    /* Header principal */
    .header-container {
        text-align: center;
        padding: 10px 0 15px 0;
        border-bottom: 2px solid #21262d;
        margin-bottom: 15px;
    }
    .app-title {
        color: #d4af37;
        font-size: 1.6rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: 1px;
    }
    .app-subtitle {
        color: #8b949e;
        font-size: 0.75rem;
        margin-top: 2px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Reducción de espacios muertos en celulares */
    .block-container { padding-top: 0.8rem !important; padding-bottom: 2rem !important; }
    
    /* Estilo de Tarjetas de Partido (Match Card) */
    .match-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* Inputs de Marcador */
    div[data-baseweb="input"] input {
        text-align: center !important;
        font-weight: 800 !important;
        color: #d4af37 !important;
        background-color: #0d0f14 !important;
        border-radius: 6px !important;
        font-size: 1.1rem !important;
        padding: 2px 4px !important;
    }

    /* Títulos de sección */
    .badge-lib {
        background-color: #d4af37;
        color: #000;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .badge-sud {
        background-color: #70d6ff;
        color: #000;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar Estado de Equipos
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
        <div class="app-subtitle">Official eSports Manager</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 1. PANTALLA CONFIGURACIÓN
# ==========================================
if st.session_state.fase_actual == 'config':
    st.subheader("⚙️ Configuración de Equipos")
    st.caption("Ingresá los nombres de los 16 participantes:")

    grupo_sel = st.radio("Seleccionar Grupo a editar:", ["Grupo A", "Grupo B", "Grupo C", "Grupo D"], horizontal=True)
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
        g_selected = st.selectbox("📌 Ver Grupo:", ["Grupo A", "Grupo B", "Grupo C", "Grupo D"], key="sb_grupo")
        g = g_selected[-1]

        st.markdown(f"#### ⚽ Partidos del Grupo {g}")
        eqs = st.session_state.equipos[g]
        cruces = [
            (eqs[0], eqs[1]), (eqs[2], eqs[3]),
            (eqs[0], eqs[2]), (eqs[1], eqs[3]),
            (eqs[0], eqs[3]), (eqs[1], eqs[2])
        ]

        # Calcular todos los partidos en segundo plano para actualizar tablas
        for g_code in ['A', 'B', 'C', 'D']:
            eqs_c = st.session_state.equipos[g_code]
            cruces_c = [
                (eqs_c[0], eqs_c[1]), (eqs_c[2], eqs_c[3]),
                (eqs_c[0], eqs_c[2]), (eqs_c[1], eqs_c[3]),
                (eqs_c[0], eqs_c[3]), (eqs_c[1], eqs_c[2])
            ]
            for idx_c, (eq1_c, eq2_c) in enumerate(cruces_c):
                # Renderizar controles visuales solo para el grupo seleccionado
                if g_code == g:
                    st.markdown(f"**Fecha {idx_c//2 + 1}**")
                    col1, col2, col3, col4 = st.columns([4, 2, 2, 4])
                    col1.markdown(f"<div style='text-align:right; font-weight:bold; font-size:0.9rem;'>{eq1_c}</div>", unsafe_allow_html=True)
                    g1_in = col2.text_input("G1", key=f"G_{g_code}_{idx_c}_1", label_visibility="collapsed")
                    g2_in = col3.text_input("G2", key=f"G_{g_code}_{idx_c}_2", label_visibility="collapsed")
                    col4.markdown(f"<div style='font-weight:bold; font-size:0.9rem;'>{eq2_c}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:4px 0; border-color:#21262d;'>", unsafe_allow_html=True)
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

    # ------------------------------------------
    # TAB 2: COPA LIBERTADORES
    # ------------------------------------------
    with tab_lib:
        st.markdown('<span class="badge-lib">🏆 COPA LIBERTADORES</span>', unsafe_allow_html=True)
        st.markdown("#### 🥇 Cuartos de Final (Ida y Vuelta)")
        
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
            i1 = c1.text_input("Ida L", key=f"L_C_{idx}_i1", placeholder="Ida 1")
            i2 = c2.text_input("Ida V", key=f"L_C_{idx}_i2", placeholder="Ida 2")
            v1 = c3.text_input("Vue L", key=f"L_C_{idx}_v1", placeholder="Vue 1")
            v2 = c4.text_input("Vue V", key=f"L_C_{idx}_v2", placeholder="Vue 2")
            
            tot1 = (int(i1) if i1.isdigit() else 0) + (int(v1) if v1.isdigit() else 0)
            tot2 = (int(i2) if i2.isdigit() else 0) + (int(v2) if v2.isdigit() else 0)
            
            if tot1 > tot2: ganadores_cuartos_lib.append(eq1)
            elif tot2 > tot1: ganadores_cuartos_lib.append(eq2)
            else: ganadores_cuartos_lib.append("Por definir")
            st.markdown("<hr style='margin:4px 0; border-color:#21262d;'>", unsafe_allow_html=True)

        st.markdown("#### 🔥 Semifinales")
        st.info(f"**Semi 1:** {ganadores_cuartos_lib[0]} vs {ganadores_cuartos_lib[1]}")
        st.info(f"**Semi 2:** {ganadores_cuartos_lib[2]} vs {ganadores_cuartos_lib[3]}")

    # ------------------------------------------
    # TAB 3: COPA SUDAMERICANA
    # ------------------------------------------
    with tab_sud:
        st.markdown('<span class="badge-sud">🥈 COPA SUDAMERICANA</span>', unsafe_allow_html=True)
        st.markdown("#### 🟦 Cuartos de Final (Ida y Vuelta)")
        
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
            i1 = c1.text_input("Ida L", key=f"S_C_{idx}_i1", placeholder="Ida 1")
            i2 = c2.text_input("Ida V", key=f"S_C_{idx}_i2", placeholder="Ida 2")
            v1 = c3.text_input("Vue L", key=f"S_C_{idx}_v1", placeholder="Vue 1")
            v2 = c4.text_input("Vue V", key=f"S_C_{idx}_v2", placeholder="Vue 2")
            
            tot1 = (int(i1) if i1.isdigit() else 0) + (int(v1) if v1.isdigit() else 0)
            tot2 = (int(i2) if i2.isdigit() else 0) + (int(v2) if v2.isdigit() else 0)
            
            if tot1 > tot2: ganadores_cuartos_sud.append(eq1)
            elif tot2 > tot1: ganadores_cuartos_sud.append(eq2)
            else: ganadores_cuartos_sud.append("Por definir")
            st.markdown("<hr style='margin:4px 0; border-color:#21262d;'>", unsafe_allow_html=True)

        st.markdown("#### 🔥 Semifinales")
        st.success(f"**Semi 1:** {ganadores_cuartos_sud[0]} vs {ganadores_cuartos_sud[1]}")
        st.success(f"**Semi 2:** {ganadores_cuartos_sud[2]} vs {ganadores_cuartos_sud[3]}")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("⚙️ Configurar Equipos", use_container_width=True):
            st.session_state.fase_actual = 'config'
            st.rerun()
    with col_b:
        if st.button("🔄 Reiniciar Todo", use_container_width=True):
            st.session_state.clear()
            st.rerun()

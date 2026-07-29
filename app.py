import streamlit as st
import pandas as pd
import json
import os
from itertools import groupby

# Configuración Móvil Estricta
st.set_page_config(
    page_title="Copa Bazzini 2026",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS Optimizado para Móviles Táctiles
st.markdown("""
    <style>
    .stApp { background-color: #0c0e14; color: #f0f6fc; }
    
    .header-container {
        text-align: center;
        padding: 6px 0 10px 0;
        border-bottom: 2px solid #21262d;
        margin-bottom: 12px;
    }
    .app-title { color: #d4af37; font-size: 1.4rem; font-weight: 900; margin: 0; }
    .app-subtitle { color: #8b949e; font-size: 0.7rem; margin-top: 2px; text-transform: uppercase; }

    .block-container { padding-top: 0.5rem !important; padding-bottom: 2rem !important; }
    
    /* Inputs de Marcador - Optimizados para numérico corto */
    div[data-baseweb="input"] input {
        text-align: center !important;
        font-weight: 800 !important;
        color: #d4af37 !important;
        background-color: #0d0f14 !important;
        border-radius: 6px !important;
        font-size: 1rem !important;
        padding: 4px !important;
    }

    /* Ocultar flechas numéricas en móviles/navegadores */
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none; 
        margin: 0; 
    }

    /* Badges de Títulos */
    .badge-lib { background-color: #d4af37; color: #000; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }
    .badge-sud { background-color: #70d6ff; color: #000; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }

    /* Tarjetas de Eliminatorias */
    .match-card-lib {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 5px solid #d4af37;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 15px;
    }
    .match-card-sud {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 5px solid #70d6ff;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 15px;
    }

    .global-badge {
        background-color: #21262d;
        color: #d4af37;
        font-size: 0.8rem;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 4px;
    }
    
    .fecha-header {
        color: #8b949e;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 10px;
        margin-bottom: 6px;
        border-bottom: 1px solid #21262d;
    }

    .input-label-row {
        font-size: 0.75rem;
        color: #8b949e;
        font-weight: bold;
        margin-top: 6px;
        margin-bottom: 2px;
    }
    .role-badge {
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: bold;
    }
    .role-editor { background-color: #238636; color: white; }
    .role-viewer { background-color: #30363d; color: #8b949e; }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------
# MANEJO DE ARCHIVO PERSISTENTE JSON
# ------------------------------------------
DATA_FILE = "datos_torneo.json"

def cargar_datos_disco():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if "prodes" not in data:
                    data["prodes"] = {}
                return data
        except Exception:
            pass
    return {
        "equipos": {
            'A': [f"Equipo A{i}" for i in range(1, 5)],
            'B': [f"Equipo B{i}" for i in range(1, 5)],
            'C': [f"Equipo C{i}" for i in range(1, 5)],
            'D': [f"Equipo D{i}" for i in range(1, 5)],
        },
        "partidos": {},
        "prodes": {}
    }

def guardar_datos_disco(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error al guardar datos: {e}")

# Validación estricta de goles: solo números de 1 o 2 cifras
def es_gol_valido(val):
    return val == "" or (val.isdigit() and 1 <= len(val) <= 2)

# Cargar datos al iniciar la app
if 'torneo_data' not in st.session_state:
    st.session_state.torneo_data = cargar_datos_disco()

if 'es_editor' not in st.session_state:
    st.session_state.es_editor = False

if 'fase_actual' not in st.session_state:
    st.session_state.fase_actual = 'login'

equipos = st.session_state.torneo_data["equipos"]
datos_db = st.session_state.torneo_data["partidos"]

# Header Principal
role_class = "role-editor" if st.session_state.es_editor else "role-viewer"
role_text = f"ADMIN: {st.session_state.get('usuario_admin', '')}" if st.session_state.es_editor else "MODO ESPECTADOR"

st.markdown(f"""
    <div class="header-container">
        <div class="app-title">🏆 COPA BAZZINI 2026</div>
        <div class="app-subtitle">eSports Manager — <span class="role-badge {role_class}">{role_text}</span></div>
    </div>
""", unsafe_allow_html=True)

# ------------------------------------------
# CÁLCULO DE PUNTUACIÓN DEL PRODE (AVANZADO)
# ------------------------------------------
def calcular_puntuacion_prodes():
    resultados_reales = st.session_state.torneo_data["partidos"]
    prodes_guardados = st.session_state.torneo_data.get("prodes", {})
    ranking = []

    for participante, preds in prodes_guardados.items():
        total_pts = 0
        for g_code in ['A', 'B', 'C', 'D']:
            for m_idx in range(6):
                k1 = f"G_{g_code}_{m_idx}_1"
                k2 = f"G_{g_code}_{m_idx}_2"
                
                p1 = preds.get(k1, "")
                p2 = preds.get(k2, "")
                r1 = resultados_reales.get(k1, "")
                r2 = resultados_reales.get(k2, "")
                
                if p1.isdigit() and p2.isdigit() and r1.isdigit() and r2.isdigit():
                    p_g1, p_g2 = int(p1), int(p2)
                    r_g1, r_g2 = int(r1), int(r2)
                    
                    p_res = 1 if p_g1 > p_g2 else (-1 if p_g1 < p_g2 else 0)
                    r_res = 1 if r_g1 > r_g2 else (-1 if r_g1 < r_g2 else 0)
                    
                    p_btts = (p_g1 > 0 and p_g2 > 0)
                    r_btts = (r_g1 > 0 and r_g2 > 0)
                    
                    # 1. Resultado Exacto (6 puntos)
                    if p_g1 == r_g1 and p_g2 == r_g2:
                        total_pts += 6
                    else:
                        # 2. Ganador o Empate correcto
                        if p_res == r_res:
                            # Si además acierta la diferencia de goles exacta (4 pts), sino gana 2 pts
                            if (p_g1 - p_g2) == (r_g1 - r_g2):
                                total_pts += 4
                            else:
                                total_pts += 2
                        
                        # 3. Bono "Ambos Marcan" (+1 punto extra si adivinó si ambos metían gol)
                        if p_btts == r_btts:
                            total_pts += 1
                            
        ranking.append({"Participante": participante, "Puntos": total_pts})
    
    df_ranking = pd.DataFrame(ranking)
    if not df_ranking.empty:
        df_ranking = df_ranking.sort_values(by="Puntos", ascending=False).reset_index(drop=True)
    return df_ranking

# ------------------------------------------
# 0. PANTALLA INICIAL: INICIO DE SESIÓN Y PRODE
# ------------------------------------------
if st.session_state.fase_actual == 'login':
    st.markdown("<h4 style='text-align: center; color: #d4af37; margin-top: 10px;'>Menú Principal</h4>", unsafe_allow_html=True)
    
    tab_invitado, tab_prode, tab_admin = st.tabs(["👁️ Invitado", "🔮 Prode", "🔐 Admin"])

    with tab_invitado:
        st.info("Ingresá para ver las tablas de posiciones y los partidos actualizados en tiempo real.")
        if st.button("🚀 Entrar al Torneo", use_container_width=True, type="primary"):
            st.session_state.es_editor = False
            st.session_state.usuario_admin = None
            st.session_state.fase_actual = 'torneo'
            st.rerun()

    with tab_prode:
        st.markdown("#### 🔮 Simulador Prode")
        
        # Instrucciones de Puntaje Detalladas
        st.markdown("""
            > 📌 **Sistema de Puntos del Prode:**
            > * 🎯 **Resultado Exacto:** **6 puntos** (¡Marcador perfecto!).
            > * ⚽ **Ganador + Diferencia de Gol:** **4 puntos** (Acertaste el ganador y por cuántos goles de diferencia, ej: pronosticaste 2-0 y salió 3-1).
            > * ✅ **Ganador o Empate Correcto:** **2 puntos** (Adivinaste qué equipo ganaba o si empataban).
            > * 🔥 **Bono "Ambos Marcan":** **+1 punto extra** si acertaste si ambos equipos convertían goles (o si alguno terminaba con el arco en cero).
        """)
        
        nombre_prode = st.text_input("Tu Nombre / Apodo:", key="input_nombre_prode", placeholder="Ej. JuanB")
        
        if nombre_prode.strip() != "":
            user_preds = st.session_state.torneo_data.get("prodes", {}).get(nombre_prode.strip(), {}).copy()
            
            st.markdown("---")
            st.markdown("<div style='font-size:0.85rem; color:#d4af37; font-weight:bold;'>Pronósticos Fase de Grupos:</div>", unsafe_allow_html=True)
            
            nuevas_preds = user_preds.copy()
            for g_code in ['A', 'B', 'C', 'D']:
                with st.expander(f"Grupo {g_code}"):
                    eqs_c = equipos[g_code]
                    fechas_cruces = [
                        ("Fecha 1", [(eqs_c[0], eqs_c[1]), (eqs_c[2], eqs_c[3])]),
                        ("Fecha 2", [(eqs_c[0], eqs_c[2]), (eqs_c[1], eqs_c[3])]),
                        ("Fecha 3", [(eqs_c[0], eqs_c[3]), (eqs_c[1], eqs_c[2])])
                    ]
                    m_counter = 0
                    for f_nombre, cruces in fechas_cruces:
                        st.markdown(f"<div class='fecha-header'>{f_nombre}</div>", unsafe_allow_html=True)
                        for eq1_c, eq2_c in cruces:
                            k1 = f"G_{g_code}_{m_counter}_1"
                            k2 = f"G_{g_code}_{m_counter}_2"
                            v1_p = nuevas_preds.get(k1, "")
                            v2_p = nuevas_preds.get(k2, "")
                            
                            st.markdown(f"<div style='font-size:0.85rem; font-weight:bold; margin-bottom:2px;'>{eq1_c} vs {eq2_c}</div>", unsafe_allow_html=True)
                            c1, c2 = st.columns(2)
                            p1 = c1.text_input("P1", value=v1_p, key=f"prode_{k1}", max_chars=2, placeholder="-", label_visibility="collapsed")
                            p2 = c2.text_input("P2", value=v2_p, key=f"prode_{k2}", max_chars=2, placeholder="-", label_visibility="collapsed")
                            
                            if es_gol_valido(p1): nuevas_preds[k1] = p1
                            if es_gol_valido(p2): nuevas_preds[k2] = p2
                            
                            m_counter += 1
            
            if st.button("💾 Guardar Mis Pronósticos", use_container_width=True, type="primary"):
                if "prodes" not in st.session_state.torneo_data:
                    st.session_state.torneo_data["prodes"] = {}
                st.session_state.torneo_data["prodes"][nombre_prode.strip()] = nuevas_preds
                guardar_datos_disco(st.session_state.torneo_data)
                st.success(f"¡Pronósticos guardados correctamente para {nombre_prode.strip()}!")
        
        st.markdown("---")
        st.markdown("##### 🏆 Tabla de Posiciones del Prode")
        df_ranking = calcular_puntuacion_prodes()
        if not df_ranking.empty:
            st.dataframe(df_ranking, use_container_width=True)
        else:
            st.info("Aún no hay participantes registrados con pronósticos.")

    with tab_admin:
        user_select = st.selectbox(
            "Seleccioná tu Usuario Admin:",
            ["admin", "adminpausa", "adminchaca"]
        )
        pin_input = st.text_input(f"Contraseña de {user_select}:", type="password")
        
        if st.button("🔑 Iniciar Sesión como Admin", use_container_width=True, type="primary"):
            pins = {
                "admin": st.secrets.get("ADMIN_PIN", "admin123"),
                "adminpausa": st.secrets.get("ADMIN_PAUSA_PIN", "pausa123"),
                "adminchaca": st.secrets.get("ADMIN_CHACA_PIN", "chaca123")
            }
            
            if pin_input == pins.get(user_select):
                st.session_state.es_editor = True
                st.session_state.usuario_admin = user_select
                st.session_state.fase_actual = 'torneo'
                st.success(f"¡Bienvenido, {user_select}!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta")

# ------------------------------------------
# 1. PANTALLA CONFIGURACIÓN DE EQUIPOS
# ------------------------------------------
elif st.session_state.fase_actual == 'config' and st.session_state.es_editor:
    st.subheader("⚙️ Configuración de Equipos")
    grupo_sel = st.radio("Editar Grupo:", ["Grupo A", "Grupo B", "Grupo C", "Grupo D"], horizontal=True)
    g_key = grupo_sel[-1]

    for i in range(4):
        nuevo_nombre = st.text_input(
            f"Equipo {i+1}", 
            equipos[g_key][i], 
            key=f"cfg_{g_key}_{i}"
        )
        if nuevo_nombre != equipos[g_key][i]:
            st.session_state.torneo_data["equipos"][g_key][i] = nuevo_nombre
            guardar_datos_disco(st.session_state.torneo_data)

    st.markdown("---")
    if st.button("🚀 GUARDAR Y VOLVER AL TORNEO", use_container_width=True, type="primary"):
        st.session_state.fase_actual = 'torneo'
        st.rerun()

# ------------------------------------------
# 2. DASHBOARD TORNEO (GRUPOS & LLAVES)
# ------------------------------------------
else:
    c_ref1, c_ref2 = st.columns([7, 3])
    with c_ref2:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.session_state.torneo_data = cargar_datos_disco()
            st.rerun()

    tab_grupos, tab_lib, tab_sud = st.tabs(["📊 Grupos", "🏆 Libertadores", "🥈 Sudamericana"])

    tablas_datos = {g: {eq: {'PTS': 0, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0} 
                       for eq in equipos[g]} for g in ['A', 'B', 'C', 'D']}

    # Función de ordenamiento con Criterio de Desempate Olímpico (Duelo entre sí)
    def obtener_equipos_ordenados(g_code, tablas_dict, datos_partidos, equipos_dict):
        eqs = equipos_dict[g_code]
        match_pairs = [
            (eqs[0], eqs[1], 0),
            (eqs[2], eqs[3], 1),
            (eqs[0], eqs[2], 2),
            (eqs[1], eqs[3], 3),
            (eqs[0], eqs[3], 4),
            (eqs[1], eqs[2], 5),
        ]
        
        def obtener_resultado_match(m_idx):
            k1 = f"G_{g_code}_{m_idx}_1"
            k2 = f"G_{g_code}_{m_idx}_2"
            v1 = datos_partidos.get(k1, "")
            v2 = datos_partidos.get(k2, "")
            if v1.isdigit() and v2.isdigit():
                return int(v1), int(v2)
            return None, None

        initial_sorted = sorted(eqs, key=lambda eq: tablas_dict[g_code][eq]['PTS'], reverse=True)
        
        final_sorted = []
        for pts, group in groupby(initial_sorted, key=lambda eq: tablas_dict[g_code][eq]['PTS']):
            tied_teams = list(group)
            if len(tied_teams) > 1:
                mini_stats = {eq: {'PTS': 0, 'DG': 0, 'GF': 0, 'GC': 0} for eq in tied_teams}
                for teamA, teamB, m_idx in match_pairs:
                    if teamA in tied_teams and teamB in tied_teams:
                        gA, gB = obtener_resultado_match(m_idx)
                        if gA is not None and gB is not None:
                            mini_stats[teamA]['GF'] += gA
                            mini_stats[teamA]['GC'] += gB
                            mini_stats[teamB]['GF'] += gB
                            mini_stats[teamB]['GC'] += gA
                            mini_stats[teamA]['DG'] = mini_stats[teamA]['GF'] - mini_stats[teamA]['GC']
                            mini_stats[teamB]['DG'] = mini_stats[teamB]['GF'] - mini_stats[teamB]['GC']
                            if gA > gB:
                                mini_stats[teamA]['PTS'] += 3
                            elif gB > gA:
                                mini_stats[teamB]['PTS'] += 3
                            else:
                                mini_stats[teamA]['PTS'] += 1
                                mini_stats[teamB]['PTS'] += 1
                
                tied_sorted = sorted(
                    tied_teams,
                    key=lambda eq: (
                        mini_stats[eq]['PTS'],
                        mini_stats[eq]['DG'],
                        mini_stats[eq]['GF'],
                        tablas_dict[g_code][eq]['DG'],
                        tablas_dict[g_code][eq]['GF']
                    ),
                    reverse=True
                )
                final_sorted.extend(tied_sorted)
            else:
                final_sorted.extend(tied_teams)
        return final_sorted

    with tab_grupos:
        g_selected = st.radio("📌 Seleccionar Grupo:", ["Grupo A", "Grupo B", "Grupo C", "Grupo D"], horizontal=True, key="radio_grupo")
        g = g_selected[-1]

        for g_code in ['A', 'B', 'C', 'D']:
            eqs_c = equipos[g_code]
            fechas_cruces = [
                ("Fecha 1", [(eqs_c[0], eqs_c[1]), (eqs_c[2], eqs_c[3])]),
                ("Fecha 2", [(eqs_c[0], eqs_c[2]), (eqs_c[1], eqs_c[3])]),
                ("Fecha 3", [(eqs_c[0], eqs_c[3]), (eqs_c[1], eqs_c[2])])
            ]
            
            match_counter = 0
            for f_nombre, cruces in fechas_cruces:
                if g_code == g:
                    st.markdown(f"<div class='fecha-header'>📌 {f_nombre}</div>", unsafe_allow_html=True)
                
                for eq1_c, eq2_c in cruces:
                    key_g1, key_g2 = f"G_{g_code}_{match_counter}_1", f"G_{g_code}_{match_counter}_2"
                    val_g1, val_g2 = datos_db.get(key_g1, ""), datos_db.get(key_g2, "")

                    if g_code == g:
                        st.markdown(f"<div style='font-size:0.85rem; font-weight:bold; margin-bottom:2px;'>{eq1_c} vs {eq2_c}</div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        
                        in_g1 = c1.text_input("G1", value=val_g1, key=f"ui_{key_g1}", max_chars=2, placeholder="-", label_visibility="collapsed", disabled=not st.session_state.es_editor)
                        in_g2 = c2.text_input("G2", value=val_g2, key=f"ui_{key_g2}", max_chars=2, placeholder="-", label_visibility="collapsed", disabled=not st.session_state.es_editor)

                        if st.session_state.es_editor:
                            hubo_cambio = False
                            if in_g1 != val_g1 and es_gol_valido(in_g1):
                                st.session_state.torneo_data["partidos"][key_g1] = in_g1
                                hubo_cambio = True
                            if in_g2 != val_g2 and es_gol_valido(in_g2):
                                st.session_state.torneo_data["partidos"][key_g2] = in_g2
                                hubo_cambio = True
                            if hubo_cambio:
                                guardar_datos_disco(st.session_state.torneo_data)
                                st.rerun()

                        g1_in, g2_in = in_g1, in_g2
                    else:
                        g1_in, g2_in = val_g1, val_g2

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
                    
                    match_counter += 1

        st.markdown(f"#### 📋 Tabla de Posiciones - Grupo {g}")
        df = pd.DataFrame.from_dict(tablas_datos[g], orient='index')
        orden_grupo_actual = obtener_equipos_ordenados(g, tablas_datos, datos_db, equipos)
        df = df.reindex(orden_grupo_actual)
        st.dataframe(df[['PTS', 'PJ', 'DG', 'GF', 'GC']], use_container_width=True)

        clasificados_lib, clasificados_sud = {}, {}
        for g_c in ['A', 'B', 'C', 'D']:
            equipos_ordenados = obtener_equipos_ordenados(g_c, tablas_datos, datos_db, equipos)
            clasificados_lib[g_c] = [equipos_ordenados[0], equipos_ordenados[1]]
            clasificados_sud[g_c] = [equipos_ordenados[2], equipos_ordenados[3]]

    # Función para renderizar cruces de eliminatoria
    def renderizar_llave_movil(copa_prefix, idx, eq1, eq2, es_doble=True):
        css_class = "match-card-lib" if "LIB" in copa_prefix else "match-card-sud"
        
        k_i1, k_i2 = f"{copa_prefix}_{idx}_i1", f"{copa_prefix}_{idx}_i2"
        k_v1, k_v2 = f"{copa_prefix}_{idx}_v1", f"{copa_prefix}_{idx}_v2"

        i1, i2 = datos_db.get(k_i1, ""), datos_db.get(k_i2, "")
        v1 = datos_db.get(k_v1, "") if es_doble else "0"
        v2 = datos_db.get(k_v2, "") if es_doble else "0"

        tot1 = (int(i1) if i1.isdigit() else 0) + (int(v1) if v1.isdigit() else 0)
        tot2 = (int(i2) if i2.isdigit() else 0) + (int(v2) if v2.isdigit() else 0)

        ganador = "Por definir"
        if (i1.isdigit() and i2.isdigit()) and (not es_doble or (v1.isdigit() and v2.isdigit())):
            if tot1 > tot2: ganador = eq1
            elif tot2 > tot1: ganador = eq2
            else: ganador = f"{eq1} (Pen)"

        st1 = "color:#2ea44f; font-weight:bold;" if ganador == eq1 else "font-weight:bold;"
        st2 = "color:#2ea44f; font-weight:bold;" if ganador == eq2 else "font-weight:bold;"

        with st.container():
            st.markdown(f"""
                <div class='{css_class}'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                        <span style='font-size:0.8rem; color:#8b949e; font-weight:bold;'>LLAVE {idx+1}</span>
                        <span class='global-badge'>GLOBAL: {tot1} - {tot2}</span>
                    </div>
                    <div style='font-size:1rem; margin-bottom:10px;'>
                        <span style='{st1}'>{eq1}</span> <span style='color:#8b949e;'>vs</span> <span style='{st2}'>{eq2}</span>
                    </div>
            """, unsafe_allow_html=True)

            if es_doble:
                st.markdown("<div class='input-label-row'>⚽ Partido de Ida</div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                ui_i1 = c1.text_input("I1", value=i1, key=f"ui_{k_i1}", max_chars=2, placeholder="-", label_visibility="collapsed", disabled=not st.session_state.es_editor)
                ui_i2 = c2.text_input("I2", value=i2, key=f"ui_{k_i2}", max_chars=2, placeholder="-", label_visibility="collapsed", disabled=not st.session_state.es_editor)

                st.markdown("<div class='input-label-row'>⚽ Partido de Vuelta</div>", unsafe_allow_html=True)
                c3, c4 = st.columns(2)
                ui_v1 = c3.text_input("V1", value=v1, key=f"ui_{k_v1}", max_chars=2, placeholder="-", label_visibility="collapsed", disabled=not st.session_state.es_editor)
                ui_v2 = c4.text_input("V2", value=v2, key=f"ui_{k_v2}", max_chars=2, placeholder="-", label_visibility="collapsed", disabled=not st.session_state.es_editor)

                if st.session_state.es_editor:
                    hubo_cambio = False
                    if ui_i1 != i1 and es_gol_valido(ui_i1): st.session_state.torneo_data["partidos"][k_i1] = ui_i1; hubo_cambio = True
                    if ui_i2 != i2 and es_gol_valido(ui_i2): st.session_state.torneo_data["partidos"][k_i2] = ui_i2; hubo_cambio = True
                    if ui_v1 != v1 and es_gol_valido(ui_v1): st.session_state.torneo_data["partidos"][k_v1] = ui_v1; hubo_cambio = True
                    if ui_v2 != v2 and es_gol_valido(ui_v2): st.session_state.torneo_data["partidos"][k_v2] = ui_v2; hubo_cambio = True
                    if hubo_cambio:
                        guardar_datos_disco(st.session_state.torneo_data)
                        st.rerun()

            else:
                st.markdown("<div class='input-label-row'>👑 Gran Final Única</div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                ui_i1 = c1.text_input("I1", value=i1, key=f"ui_{k_i1}", max_chars=2, placeholder="-", label_visibility="collapsed", disabled=not st.session_state.es_editor)
                ui_i2 = c2.text_input("I2", value=i2, key=f"ui_{k_i2}", max_chars=2, placeholder="-", label_visibility="collapsed", disabled=not st.session_state.es_editor)

                if st.session_state.es_editor:
                    hubo_cambio = False
                    if ui_i1 != i1 and es_gol_valido(ui_i1): st.session_state.torneo_data["partidos"][k_i1] = ui_i1; hubo_cambio = True
                    if ui_i2 != i2 and es_gol_valido(ui_i2): st.session_state.torneo_data["partidos"][k_i2] = ui_i2; hubo_cambio = True
                    if hubo_cambio:
                        guardar_datos_disco(st.session_state.torneo_data)
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
        
        return ganador

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
                g = renderizar_llave_movil("LIB_C", idx, eq1, eq2, es_doble=True)
                ganadores_cuartos_lib.append(g)

        ganadores_semis_lib = []
        with sub_lib_s:
            s_eq1, s_eq2 = ganadores_cuartos_lib[0], ganadores_cuartos_lib[1]
            s_eq3, s_eq4 = ganadores_cuartos_lib[2], ganadores_cuartos_lib[3]
            
            g1 = renderizar_llave_movil("LIB_S", 0, s_eq1, s_eq2, es_doble=True)
            g2 = renderizar_llave_movil("LIB_S", 1, s_eq3, s_eq4, es_doble=True)
            ganadores_semis_lib.extend([g1, g2])

        with sub_lib_f:
            f_eq1, f_eq2 = ganadores_semis_lib[0], ganadores_semis_lib[1]
            campeon = renderizar_llave_movil("LIB_F", 0, f_eq1, f_eq2, es_doble=False)
            if campeon != "Por definir":
                st.balloons()
                st.success(f"🏆 ¡CAMPEÓN COPA LIBERTADORES 2026: {campeon}! 🏆")

    with tab_sud:
        st.markdown('<span class="badge-sud">🥈 COPA SUDAMERICANA</span>', unsafe_allow_html=True)
        st.write("")

        sub_sud_c, sub_sud_s, sub_sud_f = st.tabs(["🟦 Cuartos", "🔥 Semis", "👑 Final"])

        cruces_sud = [
            (clasificados_sud['A'][0], clasificados_sud['B'][1]),
            (clasificados_sud['C'][0], clasificados_sud['D'][1]),
            (clasificados_sud['B'][0], clasificados_sud['A'][1]),
            (clasificados_sud['D'][0], clasificados_sud['C'][1])
        ]
        
        ganadores_cuartos_sud = []
        with sub_sud_c:
            for idx, (eq1, eq2) in enumerate(cruces_sud):
                g = renderizar_llave_movil("SUD_C", idx, eq1, eq2, es_doble=True)
                ganadores_cuartos_sud.append(g)

        ganadores_semis_sud = []
        with sub_sud_s:
            s_eq1, s_eq2 = ganadores_cuartos_sud[0], ganadores_cuartos_sud[1]
            s_eq3, s_eq4 = ganadores_cuartos_sud[2], ganadores_cuartos_sud[3]
            
            g1 = renderizar_llave_movil("SUD_S", 0, s_eq1, s_eq2, es_doble=True)
            g2 = renderizar_llave_movil("SUD_S", 1, s_eq3, s_eq4, es_doble=True)
            ganadores_semis_sud.extend([g1, g2])

        with sub_sud_f:
            f_eq1, f_eq2 = ganadores_semis_sud[0], ganadores_semis_sud[1]
            campeon_sud = renderizar_llave_movil("SUD_F", 0, f_eq1, f_eq2, es_doble=False)
            if campeon_sud != "Por definir":
                st.balloons()
                st.info(f"🥈 ¡CAMPEÓN COPA SUDAMERICANA 2026: {campeon_sud}! 🥈")

    # ------------------------------------------
    # FOOTER DE SESIÓN Y CONTROLES ADMIN
    # ------------------------------------------
    st.markdown("---")
    with st.expander("🔐 Gestión de Sesión y Acceso"):
        if st.session_state.es_editor:
            st.info(f"👤 Sesión de Editor activa: **{st.session_state.get('usuario_admin', 'Admin')}**")
            col_ad1, col_ad2 = st.columns(2)
            with col_ad1:
                if st.button("⚙️ Editar Equipos", use_container_width=True):
                    st.session_state.fase_actual = 'config'
                    st.rerun()
            with col_ad2:
                if st.button("🔒 Cerrar Sesión", use_container_width=True):
                    st.session_state.es_editor = False
                    st.session_state.usuario_admin = None
                    st.session_state.fase_actual = 'login'
                    st.rerun()
        else:
            st.info("👤 Estás navegando como **Invitado**.")
            if st.button("🔄 Volver al Menú Principal / Prode", use_container_width=True):
                st.session_state.fase_actual = 'login'
                st.rerun()

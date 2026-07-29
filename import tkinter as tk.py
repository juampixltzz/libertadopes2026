import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import json

class CopaBazziniDefinitiva:
    def __init__(self, root):
        self.root = root
        self.root.title("COPA BAZZINI 2026 — Official Tournament Manager")
        self.root.geometry("1350x850")
        self.root.configure(bg="#0f1117")

        self.setup_styles()

        # Datos
        self.grupos = {'A': [], 'B': [], 'C': [], 'D': []}
        self.tablas = {}
        self.partidos_grupos = []
        
        self.bracket_widgets = {
            'libertadores': {'cuartos': [], 'semis': [], 'final': []},
            'sudamericana': {'cuartos': [], 'semis': [], 'final': []}
        }

        self.crear_pantalla_carga()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        BG_DARK = "#0f1117"
        BG_CARD = "#1a1d26"
        FG_GOLD = "#d4af37"
        FG_BLUE = "#70d6ff"
        FG_WHITE = "#f0f6fc"
        
        disponibles = font.families(self.root)
        FONT_FAMILY = "Roboto" if "Roboto" in disponibles else "Helvetica"

        self.style.configure("TFrame", background=BG_DARK)
        self.style.configure("Card.TFrame", background=BG_CARD)

        self.style.configure("TLabel", background=BG_DARK, foreground=FG_WHITE, font=(FONT_FAMILY, 10))
        self.style.configure("Card.TLabel", background=BG_CARD, foreground=FG_WHITE, font=(FONT_FAMILY, 10))
        
        self.style.configure("Title.TLabel", background=BG_DARK, foreground=FG_GOLD, font=(FONT_FAMILY, 20, "bold"))
        self.style.configure("SubHeader.TLabel", background=BG_DARK, foreground=FG_GOLD, font=(FONT_FAMILY, 12, "bold"))

        self.style.configure("TLabelframe", background=BG_CARD, foreground=FG_GOLD, bordercolor="#262a36")
        self.style.configure("TLabelframe.Label", background=BG_CARD, foreground=FG_GOLD, font=(FONT_FAMILY, 11, "bold"))

        self.style.configure("Sud.TLabelframe", background=BG_CARD, foreground=FG_BLUE, bordercolor="#262a36")
        self.style.configure("Sud.TLabelframe.Label", background=BG_CARD, foreground=FG_BLUE, font=(FONT_FAMILY, 11, "bold"))

        self.style.configure("Gold.TButton", background=FG_GOLD, foreground="#000000", font=(FONT_FAMILY, 10, "bold"), borderwidth=0)
        self.style.map("Gold.TButton", background=[("active", "#b59226")])

        self.style.configure("Dark.TButton", background="#262a36", foreground=FG_WHITE, font=(FONT_FAMILY, 9, "bold"), borderwidth=0)
        self.style.map("Dark.TButton", background=[("active", "#323747")])

        self.style.configure("Treeview", background="#151720", foreground=FG_WHITE, fieldbackground="#151720", rowheight=28, font=(FONT_FAMILY, 9))
        self.style.configure("Treeview.Heading", background="#262a36", foreground=FG_GOLD, font=(FONT_FAMILY, 9, "bold"))

    # ==========================================
    # CARGA DE EQUIPOS
    # ==========================================
    def crear_pantalla_carga(self):
        self.frame_carga = ttk.Frame(self.root, padding=30)
        self.frame_carga.pack(fill="both", expand=True)

        ttk.Label(self.frame_carga, text="🏆 COPA BAZZINI 2026", style="Title.TLabel").pack(pady=(0, 5))
        ttk.Label(self.frame_carga, text="Gestor Oficial de Competición eFootball", font=("Helvetica", 11)).pack(pady=(0, 25))

        grid_frame = ttk.Frame(self.frame_carga)
        grid_frame.pack(fill="both", expand=True)

        self.entries_equipos = {'A': [], 'B': [], 'C': [], 'D': []}

        for i, g in enumerate(['A', 'B', 'C', 'D']):
            col = ttk.LabelFrame(grid_frame, text=f" GRUPO {g} ", padding=15)
            col.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            grid_frame.columnconfigure(i, weight=1)

            for j in range(4):
                ttk.Label(col, text=f"Equipo {j+1}:", style="Card.TLabel").pack(anchor="w", pady=(4, 0))
                entry = tk.Entry(col, bg="#151720", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightthickness=1, highlightbackground="#262a36")
                entry.insert(0, f"Equipo {g}{j+1}")
                entry.pack(fill="x", pady=(2, 10), ipady=5)
                self.entries_equipos[g].append(entry)

        btn_iniciar = ttk.Button(self.frame_carga, text="INICIAR TORNEO", style="Gold.TButton", command=self.iniciar_torneo)
        btn_iniciar.pack(pady=20, ipadx=25, ipady=10)

    def iniciar_torneo(self):
        for g, entries in self.entries_equipos.items():
            nombres = [e.get().strip() for e in entries if e.get().strip()]
            if len(nombres) < 4:
                messagebox.showerror("Error", f"Faltan equipos en el Grupo {g}.")
                return
            self.grupos[g] = nombres

        for g, equipos in self.grupos.items():
            self.tablas[g] = {eq: {'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'PTS': 0} for eq in equipos}

        self.frame_carga.destroy()
        self.crear_pantalla_principal()

    # ==========================================
    # DASHBOARD PRINCIPAL (SIN CANVAS PROPENSOS A COLLAPSE)
    # ==========================================
    def crear_pantalla_principal(self):
        # Top Bar
        top_bar = ttk.Frame(self.root, padding=10, style="Card.TFrame")
        top_bar.pack(fill="x")

        ttk.Label(top_bar, text="🏆 COPA BAZZINI 2026", style="SubHeader.TLabel").pack(side="left", padx=10)
        
        ttk.Button(top_bar, text="💾 Guardar Estado", style="Dark.TButton", command=self.guardar_estado).pack(side="right", padx=5)
        ttk.Button(top_bar, text="📂 Cargar Estado", style="Dark.TButton", command=self.cargar_estado).pack(side="right", padx=5)
        ttk.Button(top_bar, text="📋 Exportar Tablas (.txt)", style="Dark.TButton", command=self.exportar_reporte).pack(side="right", padx=5)

        # Nav Bar
        nav_bar = tk.Frame(self.root, bg="#151720", height=45)
        nav_bar.pack(fill="x", pady=(2, 0))

        self.btn_nav_grupos = tk.Button(nav_bar, text="📊 Fase de Grupos", bg="#d4af37", fg="#000000", font=("Helvetica", 10, "bold"), relief="flat", padx=15, pady=6, command=lambda: self.cambiar_vista("grupos"))
        self.btn_nav_grupos.pack(side="left", padx=(10, 2), pady=5)

        self.btn_nav_lib = tk.Button(nav_bar, text="🏆 Copa Libertadores", bg="#262a36", fg="#ffffff", font=("Helvetica", 10, "bold"), relief="flat", padx=15, pady=6, command=lambda: self.cambiar_vista("libertadores"))
        self.btn_nav_lib.pack(side="left", padx=2, pady=5)

        self.btn_nav_sud = tk.Button(nav_bar, text="🥈 Copa Sudamericana", bg="#262a36", fg="#ffffff", font=("Helvetica", 10, "bold"), relief="flat", padx=15, pady=6, command=lambda: self.cambiar_vista("sudamericana"))
        self.btn_nav_sud.pack(side="left", padx=2, pady=5)

        # Contenedor Vistas
        self.container_vistas = tk.Frame(self.root, bg="#0f1117")
        self.container_vistas.pack(fill="both", expand=True)

        self.vistas = {}
        self.vistas["grupos"] = tk.Frame(self.container_vistas, bg="#0f1117")
        self.vistas["libertadores"] = tk.Frame(self.container_vistas, bg="#0f1117")
        self.vistas["sudamericana"] = tk.Frame(self.container_vistas, bg="#0f1117")

        self.setup_tab_grupos(self.vistas["grupos"])
        self.setup_cuadro_eliminatoria(self.vistas["libertadores"], 'libertadores')
        self.setup_cuadro_eliminatoria(self.vistas["sudamericana"], 'sudamericana')

        self.cambiar_vista("grupos")
        self.recalcular_grupos()

    def cambiar_vista(self, nombre):
        for key, f in self.vistas.items():
            f.pack_forget()

        self.btn_nav_grupos.config(bg="#262a36", fg="#ffffff")
        self.btn_nav_lib.config(bg="#262a36", fg="#ffffff")
        self.btn_nav_sud.config(bg="#262a36", fg="#ffffff")

        if nombre == "grupos":
            self.btn_nav_grupos.config(bg="#d4af37", fg="#000000")
        elif nombre == "libertadores":
            self.btn_nav_lib.config(bg="#d4af37", fg="#000000")
        elif nombre == "sudamericana":
            self.btn_nav_sud.config(bg="#70d6ff", fg="#000000")

        self.vistas[nombre].pack(fill="both", expand=True, padx=15, pady=15)

    # ==========================================
    # FASE DE GRUPOS
    # ==========================================
    def setup_tab_grupos(self, parent):
        frame_tablas = ttk.Frame(parent)
        frame_tablas.pack(fill="x", expand=True)

        self.tree_views = {}
        for i, g in enumerate(['A', 'B', 'C', 'D']):
            sub_frame = ttk.LabelFrame(frame_tablas, text=f" GRUPO {g} ", padding=8)
            sub_frame.grid(row=i//2, column=i%2, padx=8, pady=8, sticky="nsew")

            columns = ('EQ', 'PTS', 'PJ', 'PG', 'PE', 'PP', 'GF', 'GC', 'DG')
            tree = ttk.Treeview(sub_frame, columns=columns, show='headings', height=4)

            tree.tag_configure('libertadores', background='#d4af37', foreground='#000000')
            tree.tag_configure('sudamericana', background='#70d6ff', foreground='#000000')

            tree.column('EQ', width=120, anchor='w')
            for col in columns[1:]:
                tree.column(col, width=35, anchor='center')
                tree.heading(col, text=col)
            tree.heading('EQ', text='Equipo')

            tree.pack(fill="both", expand=True)
            self.tree_views[g] = tree

        ttk.Label(parent, text="⚽ ENCUENTROS DE FASE DE GRUPOS", style="Title.TLabel").pack(pady=(15, 10))

        frame_partidos = ttk.Frame(parent)
        frame_partidos.pack(fill="x", expand=True)

        for i, g in enumerate(['A', 'B', 'C', 'D']):
            box_grupo = ttk.LabelFrame(frame_partidos, text=f" Partidos Grupo {g} ", padding=10)
            box_grupo.grid(row=i//2, column=i%2, padx=8, pady=8, sticky="nsew")

            equipos = self.grupos[g]
            cruces = [
                (equipos[0], equipos[1]), (equipos[2], equipos[3]),
                (equipos[0], equipos[2]), (equipos[1], equipos[3]),
                (equipos[0], equipos[3]), (equipos[1], equipos[2])
            ]

            for eq1, eq2 in cruces:
                f_p = ttk.Frame(box_grupo, style="Card.TFrame")
                f_p.pack(fill="x", pady=3)

                lbl1 = ttk.Label(f_p, text=eq1, width=13, anchor="e", style="Card.TLabel", font=("Helvetica", 9, "bold"))
                lbl1.pack(side="left")

                in1 = tk.Entry(f_p, width=3, justify="center", bg="#151720", fg="#d4af37", insertbackground="#ffffff", relief="flat", highlightthickness=1, highlightbackground="#262a36", font=("Helvetica", 10, "bold"))
                in1.pack(side="left", padx=4)

                ttk.Label(f_p, text="vs", style="Card.TLabel").pack(side="left")

                in2 = tk.Entry(f_p, width=3, justify="center", bg="#151720", fg="#d4af37", insertbackground="#ffffff", relief="flat", highlightthickness=1, highlightbackground="#262a36", font=("Helvetica", 10, "bold"))
                in2.pack(side="left", padx=4)

                lbl2 = ttk.Label(f_p, text=eq2, width=13, anchor="w", style="Card.TLabel", font=("Helvetica", 9, "bold"))
                lbl2.pack(side="left")

                p_data = {'grupo': g, 'eq1': eq1, 'eq2': eq2, 'input1': in1, 'input2': in2}
                self.partidos_grupos.append(p_data)

                in1.bind("<FocusOut>", lambda ev: self.recalcular_grupos())
                in2.bind("<FocusOut>", lambda ev: self.recalcular_grupos())
                in1.bind("<Return>", lambda ev: self.recalcular_grupos())
                in2.bind("<Return>", lambda ev: self.recalcular_grupos())

    # ==========================================
    # LÓGICA DE CÁLCULO
    # ==========================================
    def recalcular_grupos(self):
        for g in self.tablas:
            for eq in self.tablas[g]:
                self.tablas[g][eq] = {'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'PTS': 0}

        for p in self.partidos_grupos:
            g1_s, g2_s = p['input1'].get().strip(), p['input2'].get().strip()
            if g1_s.isdigit() and g2_s.isdigit():
                g1, g2 = int(g1_s), int(g2_s)
                g, eq1, eq2 = p['grupo'], p['eq1'], p['eq2']

                self.tablas[g][eq1]['PJ'] += 1
                self.tablas[g][eq2]['PJ'] += 1
                self.tablas[g][eq1]['GF'] += g1
                self.tablas[g][eq1]['GC'] += g2
                self.tablas[g][eq2]['GF'] += g2
                self.tablas[g][eq2]['GC'] += g1

                if g1 > g2:
                    self.tablas[g][eq1]['PG'] += 1
                    self.tablas[g][eq1]['PTS'] += 3
                    self.tablas[g][eq2]['PP'] += 1
                elif g2 > g1:
                    self.tablas[g][eq2]['PG'] += 1
                    self.tablas[g][eq2]['PTS'] += 3
                    self.tablas[g][eq1]['PP'] += 1
                else:
                    self.tablas[g][eq1]['PE'] += 1
                    self.tablas[g][eq1]['PTS'] += 1
                    self.tablas[g][eq2]['PE'] += 1
                    self.tablas[g][eq2]['PTS'] += 1

                self.tablas[g][eq1]['DG'] = self.tablas[g][eq1]['GF'] - self.tablas[g][eq1]['GC']
                self.tablas[g][eq2]['DG'] = self.tablas[g][eq2]['GF'] - self.tablas[g][eq2]['GC']

        clasificados_lib = {}
        clasificados_sud = {}

        for g, tree in self.tree_views.items():
            for item in tree.get_children():
                tree.delete(item)

            ordenados = sorted(
                self.tablas[g].items(),
                key=lambda x: (x[1]['PTS'], x[1]['DG'], x[1]['GF']),
                reverse=True
            )

            for pos, (eq, stats) in enumerate(ordenados):
                tag = 'libertadores' if pos < 2 else 'sudamericana'
                tree.insert('', 'end', values=(
                    eq, stats['PTS'], stats['PJ'], stats['PG'],
                    stats['PE'], stats['PP'], stats['GF'], stats['GC'], stats['DG']
                ), tags=(tag,))

            clasificados_lib[g] = [ordenados[0][0], ordenados[1][0]]
            clasificados_sud[g] = [ordenados[2][0], ordenados[3][0]]

        self.actualizar_nombres_cuartos('libertadores', clasificados_lib)
        self.actualizar_nombres_cuartos('sudamericana', clasificados_sud)

    # ==========================================
    # ELIMINATORIAS (CUADRO VISUAL BRACKET)
    # ==========================================
    def setup_cuadro_eliminatoria(self, parent, copa):
        color_theme = "#d4af37" if copa == 'libertadores' else "#70d6ff"
        title_text = "🏆 COPA LIBERTADORES — CUADRO OFICIAL" if copa == 'libertadores' else "🥈 COPA SUDAMERICANA — CUADRO OFICIAL"

        tk.Label(parent, text=title_text, bg="#0f1117", fg=color_theme, font=("Helvetica", 16, "bold")).pack(pady=(0, 15))

        bracket_grid = tk.Frame(parent, bg="#0f1117")
        bracket_grid.pack(fill="both", expand=True)

        col_style = "TLabelframe" if copa == 'libertadores' else "Sud.TLabelframe"

        col_cuartos = ttk.LabelFrame(bracket_grid, text=" CUARTOS DE FINAL (Ida/Vuelta) ", padding=10, style=col_style)
        col_cuartos.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        col_semis = ttk.LabelFrame(bracket_grid, text=" SEMIFINALES (Ida/Vuelta) ", padding=10, style=col_style)
        col_semis.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        col_final = ttk.LabelFrame(bracket_grid, text=" GRAN FINAL (Único) ", padding=10, style=col_style)
        col_final.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")

        bracket_grid.columnconfigure(0, weight=1)
        bracket_grid.columnconfigure(1, weight=1)
        bracket_grid.columnconfigure(2, weight=1)

        # Cuartos
        self.bracket_widgets[copa]['cuartos'] = []
        for i in range(4):
            card = self.crear_card_partido(col_cuartos, color_theme, es_doble=True)
            card['frame'].pack(fill="x", pady=6)
            self.bracket_widgets[copa]['cuartos'].append(card)

        # Semis
        self.bracket_widgets[copa]['semis'] = []
        for i in range(2):
            card = self.crear_card_partido(col_semis, color_theme, es_doble=True)
            card['frame'].pack(fill="x", pady=35)
            self.bracket_widgets[copa]['semis'].append(card)

        # Final
        self.bracket_widgets[copa]['final'] = []
        card_final = self.crear_card_partido(col_final, color_theme, es_doble=False)
        card_final['frame'].pack(fill="x", pady=90)
        self.bracket_widgets[copa]['final'].append(card_final)

    def crear_card_partido(self, parent, color_accent, es_doble=True):
        f = tk.Frame(parent, bg="#1a1d26", highlightthickness=1, highlightbackground="#262a36", bd=0)
        
        # EQ 1
        f1 = tk.Frame(f, bg="#1a1d26")
        f1.pack(fill="x", padx=5, pady=3)

        lbl_eq1 = tk.Label(f1, text="Por definir", width=14, anchor="w", bg="#1a1d26", fg="#ffffff", font=("Helvetica", 9, "bold"))
        lbl_eq1.pack(side="left")

        e_ida1 = tk.Entry(f1, width=3, bg="#151720", fg=color_accent, justify="center", relief="flat", highlightthickness=1, highlightbackground="#262a36", font=("Helvetica", 9, "bold"))
        e_ida1.pack(side="left", padx=2)

        e_vue1 = None
        if es_doble:
            e_vue1 = tk.Entry(f1, width=3, bg="#151720", fg=color_accent, justify="center", relief="flat", highlightthickness=1, highlightbackground="#262a36", font=("Helvetica", 9, "bold"))
            e_vue1.pack(side="left", padx=2)

        tk.Frame(f, bg="#262a36", height=1).pack(fill="x", pady=2)

        # EQ 2
        f2 = tk.Frame(f, bg="#1a1d26")
        f2.pack(fill="x", padx=5, pady=3)

        lbl_eq2 = tk.Label(f2, text="Por definir", width=14, anchor="w", bg="#1a1d26", fg="#ffffff", font=("Helvetica", 9, "bold"))
        lbl_eq2.pack(side="left")

        e_ida2 = tk.Entry(f2, width=3, bg="#151720", fg=color_accent, justify="center", relief="flat", highlightthickness=1, highlightbackground="#262a36", font=("Helvetica", 9, "bold"))
        e_ida2.pack(side="left", padx=2)

        e_vue2 = None
        if es_doble:
            e_vue2 = tk.Entry(f2, width=3, bg="#151720", fg=color_accent, justify="center", relief="flat", highlightthickness=1, highlightbackground="#262a36", font=("Helvetica", 9, "bold"))
            e_vue2.pack(side="left", padx=2)

        inputs = [e_ida1, e_ida2]
        if es_doble:
            inputs.extend([e_vue1, e_vue2])

        for inp in inputs:
            inp.bind("<FocusOut>", lambda ev: self.procesar_avance_llaves())
            inp.bind("<Return>", lambda ev: self.procesar_avance_llaves())

        return {
            'frame': f,
            'eq1': lbl_eq1, 'eq2': lbl_eq2,
            'ida1': e_ida1, 'ida2': e_ida2,
            'vue1': e_vue1, 'vue2': e_vue2
        }

    # ==========================================
    # AVANCE DE LLAVES
    # ==========================================
    def actualizar_nombres_cuartos(self, copa, clasificados):
        if copa == 'libertadores':
            cruces = [
                (clasificados['A'][0], clasificados['B'][1]),
                (clasificados['C'][0], clasificados['D'][1]),
                (clasificados['B'][0], clasificados['A'][1]),
                (clasificados['D'][0], clasificados['C'][1]),
            ]
        else:
            cruces = [
                (clasificados['A'][2], clasificados['B'][3]),
                (clasificados['C'][2], clasificados['D'][3]),
                (clasificados['B'][2], clasificados['A'][3]),
                (clasificados['D'][2], clasificados['C'][3]),
            ]

        for idx, (eq1, eq2) in enumerate(cruces):
            card = self.bracket_widgets[copa]['cuartos'][idx]
            card['eq1'].config(text=eq1)
            card['eq2'].config(text=eq2)

        self.procesar_avance_llaves()

    def procesar_avance_llaves(self):
        for copa in ['libertadores', 'sudamericana']:
            ganadores_cuartos = []
            for card in self.bracket_widgets[copa]['cuartos']:
                eq1 = card['eq1'].cget("text")
                eq2 = card['eq2'].cget("text")
                ganador = self.calcular_ganador_serie(eq1, eq2, card['ida1'], card['ida2'], card['vue1'], card['vue2'])
                ganadores_cuartos.append(ganador)

            self.bracket_widgets[copa]['semis'][0]['eq1'].config(text=ganadores_cuartos[0])
            self.bracket_widgets[copa]['semis'][0]['eq2'].config(text=ganadores_cuartos[1])
            self.bracket_widgets[copa]['semis'][1]['eq1'].config(text=ganadores_cuartos[2])
            self.bracket_widgets[copa]['semis'][1]['eq2'].config(text=ganadores_cuartos[3])

            ganadores_semis = []
            for card in self.bracket_widgets[copa]['semis']:
                eq1 = card['eq1'].cget("text")
                eq2 = card['eq2'].cget("text")
                ganador = self.calcular_ganador_serie(eq1, eq2, card['ida1'], card['ida2'], card['vue1'], card['vue2'])
                ganadores_semis.append(ganador)

            self.bracket_widgets[copa]['final'][0]['eq1'].config(text=ganadores_semis[0])
            self.bracket_widgets[copa]['final'][0]['eq2'].config(text=ganadores_semis[1])

    def calcular_ganador_serie(self, eq1, eq2, e_i1, e_i2, e_v1=None, e_v2=None):
        if "Por definir" in [eq1, eq2]:
            return "Por definir"

        i1, i2 = e_i1.get().strip(), e_i2.get().strip()
        if not (i1.isdigit() and i2.isdigit()):
            return "Por definir"

        tot1, tot2 = int(i1), int(i2)

        if e_v1 and e_v2:
            v1, v2 = e_v1.get().strip(), e_v2.get().strip()
            if not (v1.isdigit() and v2.isdigit()):
                return "Por definir"
            tot1 += int(v1)
            tot2 += int(v2)

        if tot1 > tot2:
            return eq1
        elif tot2 > tot1:
            return eq2
        else:
            return f"{eq1} (Pen)"

    # ==========================================
    # GUARDAR / CARGAR / EXPORTAR
    # ==========================================
    def guardar_estado(self):
        data = {'grupos': self.grupos, 'partidos': []}
        for p in self.partidos_grupos:
            data['partidos'].append({
                'grupo': p['grupo'], 'eq1': p['eq1'], 'eq2': p['eq2'],
                'g1': p['input1'].get(), 'g2': p['input2'].get()
            })
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Éxito", "Estado guardado correctamente.")

    def cargar_estado(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.grupos = data['grupos']
            for p_saved in data['partidos']:
                for p_ui in self.partidos_grupos:
                    if p_ui['grupo'] == p_saved['grupo'] and p_ui['eq1'] == p_saved['eq1'] and p_ui['eq2'] == p_saved['eq2']:
                        p_ui['input1'].delete(0, tk.END)
                        p_ui['input1'].insert(0, p_saved['g1'])
                        p_ui['input2'].delete(0, tk.END)
                        p_ui['input2'].insert(0, p_saved['g2'])
            self.recalcular_grupos()
            messagebox.showinfo("Éxito", "Estado cargado con éxito.")

    def exportar_reporte(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=========================================\n")
                f.write("         COPA BAZZINI 2026 - REPORTE     \n")
                f.write("=========================================\n\n")
                for g, stats_eq in self.tablas.items():
                    f.write(f"--- GRUPO {g} ---\n")
                    f.write(f"{'Equipo':<15} | PTS | PJ | PG | PE | PP | GF | GC | DG\n")
                    f.write("-" * 50 + "\n")
                    ordenados = sorted(stats_eq.items(), key=lambda x: (x[1]['PTS'], x[1]['DG'], x[1]['GF']), reverse=True)
                    for eq, s in ordenados:
                        f.write(f"{eq:<15} | {s['PTS']:<3} | {s['PJ']:<2} | {s['PG']:<2} | {s['PE']:<2} | {s['PP']:<2} | {s['GF']:<2} | {s['GC']:<2} | {s['DG']:<3}\n")
                    f.write("\n")
            messagebox.showinfo("Exportado", "Reporte generado en texto plano.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CopaBazziniDefinitiva(root)
    root.mainloop()
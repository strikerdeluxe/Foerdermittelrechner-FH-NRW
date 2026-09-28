import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
import pandas as pd
from foerdermittel_rechner import FoerdermittelRechner
import threading
from datetime import datetime
import os
import sys

# Programmverzeichnis (auch für die mit PyInstaller gepackte Version)
APP_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Segoe UI und Consolas gibt es nur unter Windows. Auf anderen Systemen wird die
# erste installierte Alternative verwendet, notfalls die Standardschrift von Tk.
UI_FONT_CANDIDATES = ('Segoe UI', 'Inter', 'Ubuntu', 'Noto Sans', 'Cantarell', 'DejaVu Sans')
MONO_FONT_CANDIDATES = ('Consolas', 'Ubuntu Mono', 'Noto Sans Mono', 'DejaVu Sans Mono', 'Liberation Mono')


def pick_font(candidates, fallback):
    """Liefert die erste installierte Schriftfamilie aus candidates."""
    available = set(tkfont.families())
    for family in candidates:
        if family in available:
            return family
    return tkfont.nametofont(fallback).actual('family')


class FoerdermittelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fördermittel-Verteilungsrechner")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        self.ui_font = pick_font(UI_FONT_CANDIDATES, 'TkDefaultFont')
        self.mono_font = pick_font(MONO_FONT_CANDIDATES, 'TkFixedFont')

        # Moderne Farben und Styles
        self.colors = {
            'primary': '#E3F2FD',  # Helles Blau für dunkle Schrift
            'secondary': '#A23B72',
            'success': '#FFF3E0',  # Helles Orange für dunkle Schrift
            'background': '#F8F9FA',
            'surface': '#FFFFFF',
            'text': '#212529',
            'text_secondary': '#6C757D',
            # Schriftfarben: primary/success sind Hintergrundfarben und als
            # Schrift auf hellem Grund kaum lesbar
            'accent': '#1565C0',   # Dunkelblau für Überschriften und Kennzahlen
            'ok': '#2E7D32'        # Dunkelgrün für Erfolgsmeldungen
        }

        # Rechner-Instanz
        self.rechner = None
        self.kommunen_data = []

        # Mausrad-Scrollen für scrollbare Bereiche (Windows, macOS und Linux)
        self._scroll_canvases = set()
        for sequence in ('<MouseWheel>', '<Button-4>', '<Button-5>'):
            self.root.bind_all(sequence, self._on_mousewheel, add='+')

        # GUI Setup
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        
        # Keyboard shortcuts
        self.setup_shortcuts()
        
    def setup_styles(self):
        """Konfiguriert moderne Styles für die GUI"""
        style = ttk.Style()

        # Unter Linux startet Tk mit dem alten Theme 'default', das die Farben
        # uneinheitlich darstellt. 'clam' wirkt moderner und übernimmt die
        # Farbangaben zuverlässig. Unter Windows bleibt das native Theme aktiv.
        if style.theme_use() == 'default' and 'clam' in style.theme_names():
            style.theme_use('clam')
            style.configure('.', background=self.colors['background'])
            # clam zeichnet Knöpfe breiter als die übrigen Themes – kompakter halten,
            # damit die Knopfzeile der Kommunen-Verwaltung ins Fenster passt
            style.configure('TButton', padding=(6, 3), width=-8)
            style.map('Custom.TNotebook.Tab',
                     background=[('selected', self.colors['surface']),
                                 ('!selected', '#E9ECEF')])
            self.root.configure(background=self.colors['background'])
            self.root.option_add('*Toplevel.background', self.colors['background'])

        # Notebook Style
        style.configure('Custom.TNotebook', background=self.colors['background'])
        style.configure('Custom.TNotebook.Tab', 
                       padding=[20, 10],
                       font=(self.ui_font, 10, 'bold'))
        
        # Button Styles
        style.configure('Primary.TButton',
                       font=(self.ui_font, 12, 'bold'),
                       foreground='#1A1A1A',
                       background=self.colors['primary'],
                       borderwidth=3,
                       relief='raised',
                       focuscolor='none')
        
        style.map('Primary.TButton',
                 background=[('active', '#BBDEFB'),  # Dunkleres helles Blau beim Hover
                            ('pressed', '#90CAF9')],  # Noch dunkler beim Klick
                 foreground=[('active', '#1A1A1A'),
                            ('pressed', '#1A1A1A')],
                 relief=[('pressed', 'sunken')])
        
        style.configure('Success.TButton',
                       font=(self.ui_font, 12, 'bold'),
                       foreground='#1A1A1A',
                       background=self.colors['success'],
                       borderwidth=3,
                       relief='raised',
                       focuscolor='none')
        
        style.map('Success.TButton',
                 background=[('active', '#FFE0B2'),  # Dunkleres helles Orange beim Hover
                            ('pressed', '#FFCC02')],  # Noch dunkler beim Klick
                 foreground=[('active', '#1A1A1A'),
                            ('pressed', '#1A1A1A')],
                 relief=[('pressed', 'sunken')])
        
        # Standard Button Style verbessern
        style.configure('TButton',
                       font=(self.ui_font, 9),
                       foreground=self.colors['text'],
                       background='#E9ECEF',
                       borderwidth=1,
                       focuscolor='none')
        
        style.map('TButton',
                 background=[('active', '#DEE2E6'),
                            ('pressed', '#CED4DA')],
                 foreground=[('active', self.colors['text']),
                            ('pressed', self.colors['text'])])
        
        # Frame Styles
        style.configure('Card.TFrame',
                       background=self.colors['surface'],
                       relief='solid',
                       borderwidth=1)
        
        # Treeview Style
        style.configure('Custom.Treeview',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['surface'],
                       font=(self.ui_font, 9))
        
        style.configure('Custom.Treeview.Heading',
                       background=self.colors['primary'],
                       foreground=self.colors['text'],
                       font=(self.ui_font, 10, 'bold'))
        
    def create_widgets(self):
        """Erstellt alle GUI-Widgets"""
        # Hauptcontainer
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Notebook für Tabs
        self.notebook = ttk.Notebook(self.main_frame, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, pady=(10, 0))
        
        # Tabs erstellen
        self.create_input_tab()
        self.create_calculation_tab()
        self.create_results_tab()
        
        # Beispieldaten laden (nach Erstellung aller Widgets)
        self.load_example_data()
        
    def create_header(self):
        """Erstellt den Header-Bereich"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Titel
        title_label = ttk.Label(header_frame, 
                               text="Fördermittel-Verteilungsrechner",
                               font=(self.ui_font, 18, 'bold'),
                               foreground=self.colors['accent'])
        title_label.pack(side='left')
        
        # Rechte Seite mit Author-Button und Status
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side='right')
        
        # Über diese Anwendung Button
        about_button = ttk.Button(right_frame,
                                 text="Über diese Anwendung",
                                 command=self.show_copyright_info,
                                 style='TButton')
        about_button.pack(side='left', padx=(0, 10))
        
        # Status-Anzeige
        self.status_frame = ttk.Frame(right_frame)
        self.status_frame.pack(side='left')
        
        self.status_label = ttk.Label(self.status_frame,
                                     text="Bereit",
                                     font=(self.ui_font, 10),
                                     foreground=self.colors['ok'])
        self.status_label.pack()
        
    def create_input_tab(self):
        """Erstellt den Eingabe-Tab"""
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="📊 Eingabe")
        
        # Scrollable Frame
        canvas = tk.Canvas(self.input_frame, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.input_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        # Inhalt immer so breit wie der sichtbare Bereich
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))

        # Parameter-Sektion
        self.create_parameter_section(scrollable_frame)

        # Kommunen-Sektion
        self.create_kommunen_section(scrollable_frame)

        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mausrad-Scrollen
        self._register_scroll_canvas(canvas)
        
    def create_parameter_section(self, parent):
        """Erstellt die Parameter-Eingabe-Sektion"""
        # Parameter Card
        param_card = ttk.LabelFrame(parent, text="📋 Parameter", 
                                   style='Card.TFrame',
                                   padding=20)
        param_card.pack(fill='x', padx=20, pady=10)
        
        # Gesamtsumme
        gesamtsumme_frame = ttk.Frame(param_card)
        gesamtsumme_frame.pack(fill='x', pady=5)
        
        ttk.Label(gesamtsumme_frame, 
                 text="Gesamtsumme (€):",
                 font=(self.ui_font, 10, 'bold')).pack(side='left')
        
        self.gesamtsumme_var = tk.StringVar(value="500000")
        gesamtsumme_entry = ttk.Entry(gesamtsumme_frame, 
                                     textvariable=self.gesamtsumme_var,
                                     font=(self.ui_font, 12),
                                     width=15)
        gesamtsumme_entry.pack(side='right')
        
        # Mindestbetrag
        mindest_frame = ttk.Frame(param_card)
        mindest_frame.pack(fill='x', pady=5)
        
        ttk.Label(mindest_frame, 
                 text="Mindestbetrag (€):",
                 font=(self.ui_font, 10)).pack(side='left')
        
        self.mindestbetrag_var = tk.StringVar(value="12500")
        mindest_entry = ttk.Entry(mindest_frame, 
                                 textvariable=self.mindestbetrag_var,
                                 font=(self.ui_font, 12),
                                 width=15)
        mindest_entry.pack(side='right')
        
        # Sockelbetrag Prozent
        sockel_frame = ttk.Frame(param_card)
        sockel_frame.pack(fill='x', pady=5)
        
        ttk.Label(sockel_frame, 
                 text="Sockelbetrag (%):",
                 font=(self.ui_font, 10)).pack(side='left')
        
        self.sockelbetrag_var = tk.StringVar(value="50")
        sockel_entry = ttk.Entry(sockel_frame, 
                                textvariable=self.sockelbetrag_var,
                                font=(self.ui_font, 12),
                                width=15)
        sockel_entry.pack(side='right')
        
    def create_kommunen_section(self, parent):
        """Erstellt die Kommunen-Verwaltungs-Sektion"""
        # Kommunen Card
        kommunen_card = ttk.LabelFrame(parent, text="🏛️ Kommunen-Verwaltung", 
                                      style='Card.TFrame',
                                      padding=20)
        kommunen_card.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Eingabe-Bereich
        input_frame = ttk.Frame(kommunen_card)
        input_frame.pack(fill='x', pady=(0, 10))
        
        # Kommune Name
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.kommune_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.kommune_name_var, width=20).grid(row=0, column=1, padx=5)
        
        # Wert 2019
        ttk.Label(input_frame, text="Wert 2019 (€):").grid(row=0, column=2, sticky='w', padx=(10, 5))
        self.wert_2019_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.wert_2019_var, width=15).grid(row=0, column=3, padx=5)
        
        # Kinder U3
        ttk.Label(input_frame, text="Kinder U3:").grid(row=0, column=4, sticky='w', padx=(10, 5))
        self.kinder_u3_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.kinder_u3_var, width=10).grid(row=0, column=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=6, padx=(10, 0))
        
        ttk.Button(button_frame, text="➕ Hinzufügen", 
                  command=self.add_kommune,
                  style='Primary.TButton').pack(side='left', padx=2)
        
        ttk.Button(button_frame, text="✏️ Bearbeiten", 
                  command=self.edit_kommune).pack(side='left', padx=2)
        
        ttk.Button(button_frame, text="🗑️ Löschen", 
                  command=self.delete_kommune).pack(side='left', padx=2)
        
        # Import/Export Buttons
        io_frame = ttk.Frame(kommunen_card)
        io_frame.pack(fill='x', pady=5)
        
        ttk.Button(io_frame, text="📁 Excel Import", 
                  command=self.import_excel).pack(side='left', padx=(0, 5))
        
        ttk.Button(io_frame, text="💾 Vorlage erstellen", 
                  command=self.create_template).pack(side='left', padx=5)
        
        ttk.Button(io_frame, text="🧹 Alle löschen", 
                  command=self.clear_all_kommunen).pack(side='right')
        
        # Tabelle
        table_frame = ttk.Frame(kommunen_card)
        table_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Treeview
        columns = ('Name', 'Wert_2019', 'Kinder_U3')
        self.kommunen_tree = ttk.Treeview(table_frame, 
                                         columns=columns, 
                                         show='headings',
                                         style='Custom.Treeview',
                                         height=8)
        
        # Spalten konfigurieren
        self.kommunen_tree.heading('Name', text='Kommune')
        self.kommunen_tree.heading('Wert_2019', text='Wert 2019 (€)')
        self.kommunen_tree.heading('Kinder_U3', text='Kinder U3')
        
        self.kommunen_tree.column('Name', width=200)
        self.kommunen_tree.column('Wert_2019', width=150, anchor='e')
        self.kommunen_tree.column('Kinder_U3', width=100, anchor='e')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.kommunen_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.kommunen_tree.xview)
        self.kommunen_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.kommunen_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Doppelklick für Bearbeitung
        self.kommunen_tree.bind('<Double-1>', lambda e: self.edit_kommune())
        
    def create_calculation_tab(self):
        """Erstellt den Berechnungs-Tab"""
        self.calc_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.calc_frame, text="⚙️ Berechnung")
        
        # Berechnung Card
        calc_card = ttk.LabelFrame(self.calc_frame, text="🔄 Berechnung durchführen", 
                                  style='Card.TFrame',
                                  padding=30)
        calc_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Info-Bereich
        info_frame = ttk.Frame(calc_card)
        info_frame.pack(fill='x', pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, 
                                height=4, 
                                wrap='word',
                                font=(self.ui_font, 10),
                                bg=self.colors['background'],
                                relief='solid',
                                borderwidth=1)
        self.info_text.pack(fill='x')
        self.update_calculation_info()
        
        # Berechnung starten
        button_frame = ttk.Frame(calc_card)
        button_frame.pack(fill='x', pady=10)
        
        self.calc_button = ttk.Button(button_frame, 
                                     text="🚀 Berechnung starten",
                                     command=self.start_calculation,
                                     style='Success.TButton')
        self.calc_button.pack(side='left', padx=(0, 10))
        
        # Berechnungsmethode erklären Button
        explain_button = ttk.Button(button_frame,
                                   text="❓ Berechnungsmethode erklären",
                                   command=self.show_calculation_method,
                                   style='TButton')
        explain_button.pack(side='left', padx=(0, 10))
        
        # Progress Bar
        self.progress = ttk.Progressbar(button_frame, 
                                       mode='indeterminate',
                                       length=200)
        self.progress.pack(side='left', padx=10)
        
        # Log-Bereich
        log_frame = ttk.LabelFrame(calc_card, text="📋 Berechnungsprotokoll")
        log_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        self.log_text = tk.Text(log_frame, 
                               wrap='word',
                               font=(self.mono_font, 9),
                               bg=self.colors['surface'])
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
    def create_results_tab(self):
        """Erstellt den Ergebnis-Tab"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="📊 Ergebnisse")
        
        # Ergebnis-Übersicht
        summary_card = ttk.LabelFrame(self.results_frame, text="📈 Übersicht", 
                                     style='Card.TFrame',
                                     padding=20)
        summary_card.pack(fill='x', padx=20, pady=(20, 10))
        
        # Summary Labels
        self.summary_frame = ttk.Frame(summary_card)
        self.summary_frame.pack(fill='x')
        
        # Ergebnis-Tabelle
        results_card = ttk.LabelFrame(self.results_frame, text="📋 Detailergebnisse", 
                                     style='Card.TFrame',
                                     padding=20)
        results_card.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Export Buttons
        export_frame = ttk.Frame(results_card)
        export_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(export_frame, text="💾 Excel Export", 
                  command=self.export_excel,
                  style='Success.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(export_frame, text="📋 In Zwischenablage", 
                  command=self.copy_to_clipboard).pack(side='left')
        
        # Ergebnis-Tabelle
        results_table_frame = ttk.Frame(results_card)
        results_table_frame.pack(fill='both', expand=True)
        
        # Treeview für Ergebnisse
        result_columns = ('Name', 'Wert_2019', 'Kinder_U3', 'Sockelbetrag', 
                         'U3_Anteil', 'Zwischensumme', 'Endbetrag', 'Status')
        
        self.results_tree = ttk.Treeview(results_table_frame, 
                                        columns=result_columns, 
                                        show='headings',
                                        style='Custom.Treeview')
        
        # Spalten konfigurieren
        column_config = {
            'Name': ('Kommune', 150, 'w'),
            'Wert_2019': ('Wert 2019', 100, 'e'),
            'Kinder_U3': ('Kinder U3', 80, 'e'),
            'Sockelbetrag': ('Sockelbetrag', 100, 'e'),
            'U3_Anteil': ('U3-Anteil', 100, 'e'),
            'Zwischensumme': ('Zwischensumme', 130, 'e'),
            'Endbetrag': ('Endbetrag', 100, 'e'),
            'Status': ('Status', 200, 'w')
        }
        
        for col, (text, width, anchor) in column_config.items():
            self.results_tree.heading(col, text=text)
            self.results_tree.column(col, width=width, anchor=anchor)
        
        # Scrollbars für Ergebnisse
        results_v_scrollbar = ttk.Scrollbar(results_table_frame, orient='vertical', 
                                           command=self.results_tree.yview)
        results_h_scrollbar = ttk.Scrollbar(results_table_frame, orient='horizontal', 
                                           command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=results_v_scrollbar.set, 
                                   xscrollcommand=results_h_scrollbar.set)
        
        # Layout
        self.results_tree.pack(side='left', fill='both', expand=True)
        results_v_scrollbar.pack(side='right', fill='y')
        results_h_scrollbar.pack(side='bottom', fill='x')
        
    def setup_layout(self):
        """Konfiguriert das responsive Layout"""
        # Grid weights für responsive Verhalten
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def setup_shortcuts(self):
        """Richtet Keyboard-Shortcuts ein"""
        self.root.bind('<Control-n>', lambda e: self.add_kommune())
        self.root.bind('<Control-s>', lambda e: self.export_excel())
        self.root.bind('<Control-o>', lambda e: self.import_excel())
        self.root.bind('<F5>', lambda e: self.start_calculation())
    
    def show_copyright_info(self):
        """Zeigt Informationen über die Anwendung an"""
        copyright_window = tk.Toplevel(self.root)
        copyright_window.title("Über diese Anwendung")
        copyright_window.geometry("600x650")
        copyright_window.resizable(True, True)
        
        # Fenster zentrieren
        copyright_window.transient(self.root)
        copyright_window.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(copyright_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Copyright Titel - Prominent angezeigt
        copyright_title = ttk.Label(main_frame,
                                   text="© 2025 Fördermittel-Rechner",
                                   font=(self.ui_font, 18, 'bold'),
                                   foreground=self.colors['accent'])
        copyright_title.pack(pady=(0, 15))
        
        # Copyright Notice - Gut lesbar
        copyright_frame = ttk.LabelFrame(main_frame, text="Copyright-Vermerk", padding=15)
        copyright_frame.pack(fill='x', pady=(0, 15))
        
        copyright_text = ttk.Label(copyright_frame,
                                  text="Copyright © 2025 Marco Benta\nAlle Rechte vorbehalten.\n\nDiese Software ist unter der MIT-Lizenz\nlizenziert und darf frei verwendet werden.",
                                  font=(self.ui_font, 11),
                                  justify='center',
                                  foreground=self.colors['text'])
        copyright_text.pack(pady=5)
        
        # Entwickler Info Frame
        dev_frame = ttk.LabelFrame(main_frame, text="Entwickler", padding=15)
        dev_frame.pack(fill='x', pady=(0, 15))
        
        # Name
        name_frame = ttk.Frame(dev_frame)
        name_frame.pack(fill='x', pady=3)
        ttk.Label(name_frame, text="Entwickler:", font=(self.ui_font, 10, 'bold')).pack(side='left')
        ttk.Label(name_frame, text="Marco Benta", font=(self.ui_font, 10)).pack(side='left', padx=(10, 0))
        
        # Email
        email_frame = ttk.Frame(dev_frame)
        email_frame.pack(fill='x', pady=3)
        ttk.Label(email_frame, text="Kontakt:", font=(self.ui_font, 10, 'bold')).pack(side='left')
        email_label = ttk.Label(email_frame, text="marco@dabenta.de", 
                               font=(self.ui_font, 10),
                               foreground='blue',
                               cursor='hand2')
        email_label.pack(side='left', padx=(10, 0))
        
        # Email klickbar machen
        def open_email(event):
            import webbrowser
            webbrowser.open('mailto:marco@dabenta.de')
        email_label.bind('<Button-1>', open_email)
        
        # Version
        version_frame = ttk.Frame(dev_frame)
        version_frame.pack(fill='x', pady=3)
        ttk.Label(version_frame, text="Version:", font=(self.ui_font, 10, 'bold')).pack(side='left')
        ttk.Label(version_frame, text="0.8 (2025)", font=(self.ui_font, 10)).pack(side='left', padx=(10, 0))
        
        # Open-Source-Komponenten
        opensource_frame = ttk.LabelFrame(main_frame, text="Verwendete Open-Source-Programme", padding=15)
        opensource_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Scrollable Text für Open-Source-Informationen
        text_frame = ttk.Frame(opensource_frame)
        text_frame.pack(fill='both', expand=True)
        
        opensource_text = tk.Text(text_frame,
                                 height=8,
                                 wrap='word',
                                 font=(self.ui_font, 9),
                                 bg=self.colors['surface'],
                                 relief='solid',
                                 borderwidth=1)
        
        scrollbar_os = ttk.Scrollbar(text_frame, orient='vertical', command=opensource_text.yview)
        opensource_text.configure(yscrollcommand=scrollbar_os.set)
        
        opensource_content = """Diese Anwendung basiert auf folgenden Open-Source-Komponenten:

• Python 3.x (Python Software Foundation License)
  Copyright © 2001-2024 Python Software Foundation

• Tkinter GUI Framework (Python Software Foundation License)
  Teil der Python-Standardbibliothek

• OpenPyXL Excel-Bibliothek (MIT License)
  Copyright © 2010 openpyxl

• PyInstaller (GPL v2 mit Runtime Exception)
  Copyright © 2005-2024 PyInstaller Development Team

Vollständige Lizenzinformationen finden Sie in den Dateien LICENSE.md und THIRD-PARTY-NOTICES.md im Programmverzeichnis."""
        
        opensource_text.insert('1.0', opensource_content)
        opensource_text.config(state='disabled')  # Nur lesbar
        
        opensource_text.pack(side='left', fill='both', expand=True)
        scrollbar_os.pack(side='right', fill='y')
        
        # Schließen Button
        close_button = ttk.Button(main_frame,
                                 text="Schließen",
                                 command=copyright_window.destroy,
                                 style='Primary.TButton')
        close_button.pack(pady=(10, 0))
        
        # Fokus auf das Fenster setzen
        copyright_window.focus_set()
    
    def show_calculation_method(self):
        """Zeigt eine verständliche Erklärung der Berechnungsmethode an"""
        method_window = tk.Toplevel(self.root)
        method_window.title("Berechnungsmethode - Fördermittelverteilung")
        method_window.geometry("700x600")
        method_window.resizable(True, True)
        
        # Fenster zentrieren
        method_window.transient(self.root)
        method_window.grab_set()
        
        # Hauptframe mit Scrollbar
        main_frame = ttk.Frame(method_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Canvas und Scrollbar für scrollbaren Inhalt
        canvas = tk.Canvas(main_frame, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        # Inhalt immer so breit wie der sichtbare Bereich
        canvas.bind('<Configure>', lambda e: canvas.itemconfigure(window_id, width=e.width))
        
        # Titel
        title_label = ttk.Label(scrollable_frame,
                               text="🔢 Wie funktioniert die Fördermittelverteilung?",
                               font=(self.ui_font, 16, 'bold'),
                               foreground=self.colors['accent'])
        title_label.pack(pady=(0, 20))
        
        # Übersicht
        overview_frame = ttk.LabelFrame(scrollable_frame, text="Überblick", padding=15)
        overview_frame.pack(fill='x', pady=(0, 15))
        
        overview_text = ttk.Label(overview_frame,
                                  text="Die Fördermittelverteilung erfolgt nach einem iterativen Verfahren, das historische Werte und aktuelle Bedarfe berücksichtigt.",
                                  font=(self.ui_font, 11),
                                  wraplength=600,
                                  justify='left')
        overview_text.pack(anchor='w')
        
        # Schritt 1
        step1_frame = ttk.LabelFrame(scrollable_frame, text="Schritt 1: Sockelbetrag berechnen", padding=15)
        step1_frame.pack(fill='x', pady=(0, 15))
        
        step1_text = ttk.Label(step1_frame,
                               text="• Jede Kommune erhält einen Sockelbetrag basierend auf ihrem Förderwert aus 2019\n• Sockelbetrag = Wert 2019 × Sockelbetrag-Prozentsatz (Standard: 50%)\n• Der Sockelbetrag bildet die Grundlage der Förderung",
                               font=(self.ui_font, 10),
                               wraplength=600,
                               justify='left')
        step1_text.pack(anchor='w')
        
        # Schritt 2
        step2_frame = ttk.LabelFrame(scrollable_frame, text="Schritt 2: Restbudget für U3-Kinder verteilen", padding=15)
        step2_frame.pack(fill='x', pady=(0, 15))
        
        step2_text = ttk.Label(step2_frame,
                              text="• Restbudget = Gesamtsumme - Summe aller Sockelbeträge\n• Das Restbudget wird proportional zur Anzahl der U3-Kinder im SGB-II-Bezug verteilt\n• Multiplikator = Restbudget ÷ Gesamtzahl U3-Kinder\n• U3-Anteil je Kommune = Anzahl U3-Kinder × Multiplikator",
                              font=(self.ui_font, 10),
                              wraplength=600,
                              justify='left')
        step2_text.pack(anchor='w')
        
        # Schritt 3
        step3_frame = ttk.LabelFrame(scrollable_frame, text="Schritt 3: Mindestbetrag prüfen (Iterativ)", padding=15)
        step3_frame.pack(fill='x', pady=(0, 15))
        
        step3_text = ttk.Label(step3_frame,
                              text="• Zwischensumme = Sockelbetrag + U3-Anteil\n• Falls Zwischensumme < Mindestbetrag: Kommune wird auf Mindestbetrag fixiert\n• Das Budget wird neu auf die verbleibenden Kommunen verteilt\n• Dieser Prozess wiederholt sich, bis alle Kommunen mindestens den Mindestbetrag erhalten",
                              font=(self.ui_font, 10),
                              wraplength=600,
                              justify='left')
        step3_text.pack(anchor='w')
        
        # Schritt 4
        step4_frame = ttk.LabelFrame(scrollable_frame, text="Schritt 4: Rundung und Ausgleich", padding=15)
        step4_frame.pack(fill='x', pady=(0, 15))
        
        step4_text = ttk.Label(step4_frame,
                              text="• Alle Beträge werden auf ganze Euro gerundet\n• Rundungsdifferenzen werden bei der Kommune mit der höchsten Fördersumme ausgeglichen\n• So wird sichergestellt, dass die Gesamtsumme exakt eingehalten wird",
                              font=(self.ui_font, 10),
                              wraplength=600,
                              justify='left')
        step4_text.pack(anchor='w')
        
        # Beispiel
        example_frame = ttk.LabelFrame(scrollable_frame, text="Beispiel", padding=15)
        example_frame.pack(fill='x', pady=(0, 15))
        
        example_text = ttk.Label(example_frame,
                                text="Gesamtsumme: 500.000 €, Mindestbetrag: 12.500 €, Sockelbetrag: 50%\n\nKommune A: Wert 2019: 20.000 €, U3-Kinder: 10\n→ Sockelbetrag: 10.000 €\n\nKommune B: Wert 2019: 5.000 €, U3-Kinder: 5\n→ Sockelbetrag: 2.500 € (< Mindestbetrag)\n\nRunde 1: Kommune B wird auf 12.500 € fixiert\nRunde 2: Restbudget wird neu auf Kommune A verteilt",
                                font=(self.mono_font, 9),
                                wraplength=600,
                                justify='left',
                                background=self.colors['surface'])
        example_text.pack(anchor='w', fill='x')
        
        # Eigenschaften
        properties_frame = ttk.LabelFrame(scrollable_frame, text="Eigenschaften der Methode", padding=15)
        properties_frame.pack(fill='x', pady=(0, 20))
        
        properties_text = ttk.Label(properties_frame,
                                   text="• Berücksichtigung historischer Förderung\n• Verteilung nach aktuellen U3-Zahlen\n• Mindestbetrag für alle Kommunen\n• Exakte Einhaltung der Gesamtsumme\n• Nachvollziehbare Berechnung",
                                   font=(self.ui_font, 10),
                                   wraplength=600,
                                   justify='left')
        properties_text.pack(anchor='w')
        

        # Schließen Button
        close_button = ttk.Button(scrollable_frame,
                                 text="Verstanden - Fenster schließen",
                                 command=method_window.destroy,
                                 style='Primary.TButton')
        close_button.pack(pady=(20, 0))
        
        # Canvas und Scrollbar packen
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Mausrad-Scrolling aktivieren (wird beim Schließen automatisch entfernt)
        self._register_scroll_canvas(canvas)

        # Fokus auf das Fenster setzen
        method_window.focus_set()

    def _register_scroll_canvas(self, canvas):
        """Meldet ein Canvas für das Mausrad-Scrollen an."""
        self._scroll_canvases.add(canvas)
        canvas.bind('<Destroy>', lambda e: self._scroll_canvases.discard(canvas), add='+')

    def _on_mousewheel(self, event):
        """Scrollt das angemeldete Canvas, über dem sich der Mauszeiger befindet.

        Windows und macOS melden das Mausrad als <MouseWheel>, Linux (X11) als
        <Button-4> (hoch) und <Button-5> (runter).
        """
        widget = event.widget
        if not hasattr(widget, 'winfo_class'):
            return  # z.B. Elemente der Tk-Dateidialoge
        if widget.winfo_class() in ('Treeview', 'Text', 'Listbox'):
            return  # scrollen selbst – nicht zusätzlich die ganze Seite bewegen

        # Vom Widget unter dem Mauszeiger zum umgebenden Canvas hochgehen
        canvas = widget
        while canvas is not None and canvas not in self._scroll_canvases:
            canvas = canvas.master
        if canvas is None:
            return

        if event.num == 4:
            steps = -1
        elif event.num == 5:
            steps = 1
        elif event.delta:
            steps = -int(event.delta / 120) or (-1 if event.delta > 0 else 1)
        else:
            return
        canvas.yview_scroll(steps, 'units')
        
    def update_status(self, message, color=None):
        """Aktualisiert die Status-Anzeige"""
        self.status_label.config(text=message)
        if color:
            self.status_label.config(foreground=color)
        self.root.update_idletasks()
        
    def log_message(self, message):
        """Fügt eine Nachricht zum Berechnungsprotokoll hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.root.update_idletasks()
        
    def clear_log(self):
        """Löscht das Berechnungsprotokoll"""
        self.log_text.delete('1.0', 'end')
        
    def validate_parameters(self):
        """Validiert die eingegebenen Parameter"""
        try:
            gesamtsumme = float(self.gesamtsumme_var.get().replace(',', ''))
            mindestbetrag = float(self.mindestbetrag_var.get().replace(',', ''))
            sockelbetrag = float(self.sockelbetrag_var.get()) / 100
            
            if gesamtsumme <= 0:
                raise ValueError("Gesamtsumme muss positiv sein")
            if mindestbetrag < 0:
                raise ValueError("Mindestbetrag darf nicht negativ sein")
            if not 0 <= sockelbetrag <= 1:
                raise ValueError("Sockelbetrag muss zwischen 0 und 100% liegen")
                
            return gesamtsumme, mindestbetrag, sockelbetrag
            
        except ValueError as e:
            messagebox.showerror("Eingabefehler", f"Ungültige Parameter: {str(e)}")
            return None
            
    def add_kommune(self):
        """Fügt eine neue Kommune hinzu"""
        name = self.kommune_name_var.get().strip()
        
        if not name:
            messagebox.showwarning("Eingabefehler", "Bitte geben Sie einen Namen ein.")
            return
            
        try:
            wert_2019 = float(self.wert_2019_var.get().replace(',', ''))
            kinder_u3 = float(self.kinder_u3_var.get())  # BUGFIX: Verwende float() für Konsistenz
            
            if wert_2019 < 0 or kinder_u3 < 0:
                raise ValueError("Werte dürfen nicht negativ sein")
                
            # Prüfe auf doppelte Namen
            for item in self.kommunen_tree.get_children():
                if self.kommunen_tree.item(item)['values'][0] == name:
                    messagebox.showwarning("Eingabefehler", "Eine Kommune mit diesem Namen existiert bereits.")
                    return
                    
            # Füge zur Tabelle hinzu
            self.kommunen_tree.insert('', 'end', values=(name, f"{wert_2019:,.2f}", kinder_u3))
            
            # Leere Eingabefelder
            self.kommune_name_var.set('')
            self.wert_2019_var.set('')
            self.kinder_u3_var.set('')
            
            self.update_calculation_info()
            self.update_status(f"Kommune '{name}' hinzugefügt", self.colors['ok'])
            
        except ValueError as e:
            messagebox.showerror("Eingabefehler", "Bitte geben Sie gültige Zahlen ein.")
            
    def edit_kommune(self):
        """Bearbeitet die ausgewählte Kommune"""
        selection = self.kommunen_tree.selection()
        if not selection:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie eine Kommune zum Bearbeiten aus.")
            return
            
        item = selection[0]
        values = self.kommunen_tree.item(item)['values']
        
        # Setze Werte in Eingabefelder
        self.kommune_name_var.set(values[0])
        self.wert_2019_var.set(str(values[1]).replace(',', ''))
        self.kinder_u3_var.set(str(values[2]))
        
        # Lösche alte Zeile
        self.kommunen_tree.delete(item)
        
    def delete_kommune(self):
        """Löscht die ausgewählte Kommune"""
        selection = self.kommunen_tree.selection()
        if not selection:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie eine Kommune zum Löschen aus.")
            return
            
        if messagebox.askyesno("Bestätigung", "Möchten Sie die ausgewählte Kommune wirklich löschen?"):
            for item in selection:
                name = self.kommunen_tree.item(item)['values'][0]
                self.kommunen_tree.delete(item)
                self.update_status(f"Kommune '{name}' gelöscht", self.colors['text_secondary'])
                
            self.update_calculation_info()
            
    def clear_all_kommunen(self):
        """Löscht alle Kommunen"""
        if messagebox.askyesno("Bestätigung", "Möchten Sie wirklich alle Kommunen löschen?"):
            self.kommunen_tree.delete(*self.kommunen_tree.get_children())
            self.update_calculation_info()
            self.update_status("Alle Kommunen gelöscht", self.colors['text_secondary'])
            
    def load_example_data(self):
        """Lädt Beispieldaten"""
        beispiel_kommunen = [
            ("Stadt A", 50000, 120),
            ("Stadt B", 35000, 85),
            ("Gemeinde C", 15000, 30),
            ("Gemeinde D", 8000, 15),
            ("Stadt E", 45000, 95),
            ("Gemeinde F", 12000, 25),
            ("Stadt G", 60000, 140),
            ("Gemeinde H", 5000, 8),
            ("Stadt I", 40000, 75),
            ("Gemeinde J", 18000, 35)
        ]
        
        for name, wert_2019, kinder_u3 in beispiel_kommunen:
            self.kommunen_tree.insert('', 'end', values=(name, f"{wert_2019:,.2f}", kinder_u3))
            
        self.update_calculation_info()
        
    def update_calculation_info(self):
        """Aktualisiert die Berechnungsinformationen"""
        # Prüfe ob info_text Widget existiert
        if not hasattr(self, 'info_text'):
            return
            
        anzahl_kommunen = len(self.kommunen_tree.get_children())
        
        if anzahl_kommunen > 0:
            total_wert_2019 = sum(float(self.kommunen_tree.item(item)['values'][1].replace(',', '')) 
                                 for item in self.kommunen_tree.get_children())
            total_kinder_u3 = sum(float(self.kommunen_tree.item(item)['values'][2]) 
                                 for item in self.kommunen_tree.get_children())
        else:
            total_wert_2019 = 0
            total_kinder_u3 = 0
            
        info_text = f"""Berechnungsgrundlage:
• Anzahl Kommunen: {anzahl_kommunen}
• Summe Wert 2019: {total_wert_2019:,.2f} €
• Summe Kinder U3: {total_kinder_u3}"""
        
        self.info_text.delete('1.0', 'end')
        self.info_text.insert('1.0', info_text)
        
    def start_calculation(self):
        """Startet die Berechnung in einem separaten Thread"""
        # Validiere Parameter
        params = self.validate_parameters()
        if not params:
            return
            
        gesamtsumme, mindestbetrag, sockelbetrag = params
        
        # Prüfe ob Kommunen vorhanden
        if len(self.kommunen_tree.get_children()) == 0:
            messagebox.showwarning("Keine Daten", "Bitte fügen Sie mindestens eine Kommune hinzu.")
            return
            
        # UI für Berechnung vorbereiten
        self.calc_button.config(state='disabled', text="⏳ Berechnung läuft...")
        self.progress.start()
        self.clear_log()
        self.update_status("Berechnung läuft...", self.colors['accent'])
        
        # Starte Berechnung in separatem Thread
        thread = threading.Thread(target=self._run_calculation, 
                                 args=(gesamtsumme, mindestbetrag, sockelbetrag))
        thread.daemon = True
        thread.start()
        
    def _run_calculation(self, gesamtsumme, mindestbetrag, sockelbetrag):
        """Führt die Berechnung durch (läuft in separatem Thread)"""
        try:
            # Erstelle Rechner-Instanz
            self.rechner = FoerdermittelRechner(gesamtsumme)
            self.rechner.mindestbetrag = mindestbetrag
            self.rechner.sockelbetrag_prozent = sockelbetrag
            
            self.log_message("Berechnung gestartet...")
            self.log_message(f"Gesamtsumme: {gesamtsumme:,.2f} €")
            self.log_message(f"Mindestbetrag: {mindestbetrag:,.2f} €")
            self.log_message(f"Sockelbetrag: {sockelbetrag*100:.1f}%")
            self.log_message("-" * 50)
            
            # Füge Kommunen hinzu
            for item in self.kommunen_tree.get_children():
                values = self.kommunen_tree.item(item)['values']
                name = values[0]
                wert_2019 = float(values[1].replace(',', ''))
                kinder_u3 = float(values[2])
                
                self.rechner.kommune_hinzufuegen(name, wert_2019, kinder_u3)
                self.log_message(f"Kommune hinzugefügt: {name}")
                
            self.log_message("-" * 50)
            self.log_message("Starte iterative Berechnung...")
            
            # Führe Berechnung durch
            ergebnis = self.rechner.berechne_verteilung()
            
            # Aktualisiere UI im Hauptthread
            self.root.after(0, self._calculation_completed, ergebnis)
            
        except Exception as e:
            self.root.after(0, self._calculation_error, str(e))
            
    def _calculation_completed(self, ergebnis):
        """Wird aufgerufen wenn die Berechnung abgeschlossen ist"""
        # UI zurücksetzen
        self.calc_button.config(state='normal', text="🚀 Berechnung starten")
        self.progress.stop()
        self.update_status("Berechnung abgeschlossen", self.colors['ok'])
        
        self.log_message("=" * 50)
        self.log_message("✓ Berechnung erfolgreich abgeschlossen!")
        
        # Ergebnisse anzeigen
        self.display_results(ergebnis)
        
        # Wechsle zum Ergebnis-Tab
        self.notebook.select(2)
        
        messagebox.showinfo("Erfolg", "Die Berechnung wurde erfolgreich abgeschlossen!")
        
    def _calculation_error(self, error_message):
        """Wird aufgerufen wenn ein Fehler bei der Berechnung auftritt"""
        # UI zurücksetzen
        self.calc_button.config(state='normal', text="🚀 Berechnung starten")
        self.progress.stop()
        self.update_status("Fehler bei Berechnung", 'red')
        
        self.log_message(f"❌ FEHLER: {error_message}")
        
        messagebox.showerror("Berechnungsfehler", f"Ein Fehler ist aufgetreten:\n{error_message}")
        
    def display_results(self, ergebnis):
        """Zeigt die Berechnungsergebnisse an"""
        # Lösche alte Ergebnisse
        self.results_tree.delete(*self.results_tree.get_children())
        
        # Lösche alte Summary
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
            
        # Summary erstellen
        gesamt_verteilt = ergebnis['Endbetrag'].sum()
        anzahl_kommunen = len(ergebnis)
        durchschnitt = gesamt_verteilt / anzahl_kommunen if anzahl_kommunen > 0 else 0
        
        # Summary Labels
        summary_info = [
            ("Gesamtsumme verteilt:", f"{gesamt_verteilt:,.0f} €", self.colors['accent']),
            ("Anzahl Kommunen:", str(anzahl_kommunen), self.colors['text']),
            ("Durchschnitt pro Kommune:", f"{durchschnitt:,.0f} €", self.colors['text']),
            ("Mindestbetrag:", f"{self.rechner.mindestbetrag:,.0f} €", self.colors['text_secondary'])
        ]
        
        for i, (label, value, color) in enumerate(summary_info):
            frame = ttk.Frame(self.summary_frame)
            frame.grid(row=0, column=i, padx=20, sticky='w')
            
            ttk.Label(frame, text=label, font=(self.ui_font, 9)).pack()
            ttk.Label(frame, text=value, font=(self.ui_font, 12, 'bold'), 
                     foreground=color).pack()
                     
        # Ergebnisse in Tabelle einfügen
        for _, row in ergebnis.iterrows():
            values = (
                row['Name'],
                f"{row['Wert_2019']:,.0f}",
                f"{row['Kinder_U3']:.6f}",  # BUGFIX: Verwende volle Dezimalstellen für präzise Berechnung
                f"{row['Sockelbetrag']:,.0f}",
                f"{row['U3_Anteil']:,.0f}",
                f"{row['Zwischensumme']:,.0f}",
                f"{row['Endbetrag']:,.0f}",
                row['Status']
            )
            self.results_tree.insert('', 'end', values=values)
            
    def import_excel(self):
        """Importiert Kommunendaten aus Excel"""
        filename = filedialog.askopenfilename(
            title="Excel-Datei auswählen",
            # Großschreibung ergänzt: unter Linux unterscheidet der Dialog Groß/Klein
            filetypes=[("Excel files", "*.xlsx *.xls *.XLSX *.XLS"), ("All files", "*")]
        )
        
        if not filename:
            return
            
        try:
            # Versuche verschiedene Sheets und Formate
            df = None
            
            # Versuche zuerst "Kommunendaten" Sheet
            try:
                df = pd.read_excel(filename, sheet_name="Kommunendaten", skiprows=7)
            except:
                # Versuche erstes Sheet
                df = pd.read_excel(filename)
                
            if df is None:
                raise ValueError("Konnte keine Daten lesen")
                
            # Spalten-Mapping versuchen
            column_mapping = {
                'Kommune': 'Name',
                'Name': 'Name', 
                'Gemeinde': 'Name',
                'Stadt': 'Name',
                'Wert 2019 (€)': 'Wert_2019',
                'Wert 2019': 'Wert_2019',
                'Wert_2019': 'Wert_2019',
                'Kinder U3 im SGB-II-Bezug': 'Kinder_U3',
                'Kinder U3': 'Kinder_U3',
                'Kinder_U3': 'Kinder_U3',
                'U3': 'Kinder_U3'
            }
            
            # Rename columns
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns:
                    df = df.rename(columns={old_name: new_name})
                    
            # Prüfe erforderliche Spalten
            required_cols = ['Name', 'Wert_2019', 'Kinder_U3']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                messagebox.showerror("Import-Fehler", 
                                   f"Fehlende Spalten: {', '.join(missing_cols)}\n\n" +
                                   "Erwartete Spalten: Kommune, Wert 2019 (€), Kinder U3 im SGB-II-Bezug")
                return
                
            # Bereinige Daten
            df = df.dropna(subset=['Name'])
            
            # Verbesserte Zahlenkonvertierung für deutsche Formate
            def convert_german_number(value):
                """Konvertiert deutsche Zahlenformate (z.B. 1.000,50 oder 35,000)"""
                if pd.isna(value):
                    return None
                
                # Bereits numerisch?
                if isinstance(value, (int, float)):
                    return float(value)
                
                # String-Verarbeitung
                str_val = str(value).strip()
                if not str_val:
                    return None
                
                # Entferne Währungssymbole und Leerzeichen
                str_val = str_val.replace('€', '').replace(' ', '')
                
                # Intelligente Zahlenformatierung
                if ',' in str_val and '.' in str_val:
                    comma_pos = str_val.rfind(',')
                    dot_pos = str_val.rfind('.')
                    
                    if comma_pos > dot_pos:
                        # Format: 1.000,50 (deutsch) → 1000.50
                        str_val = str_val.replace('.', '').replace(',', '.')
                    else:
                        # Format: 1,000.50 (amerikanisch) → 1000.50
                        # Entferne alle Kommata außer dem letzten Punkt
                        parts = str_val.split('.')
                        if len(parts) >= 2:
                            # Behalte nur den letzten Teil nach dem Punkt als Dezimalstellen
                            integer_part = '.'.join(parts[:-1]).replace(',', '')
                            decimal_part = parts[-1]
                            str_val = f"{integer_part}.{decimal_part}"
                        else:
                            str_val = str_val.replace(',', '')
                elif ',' in str_val:
                    # Prüfe ob Komma als Dezimaltrennzeichen oder Tausendertrennzeichen
                    comma_pos = str_val.rfind(',')
                    after_comma = str_val[comma_pos+1:]
                    # Wenn nach Komma genau 1-2 Ziffern → wahrscheinlich Dezimaltrennzeichen
                    # Wenn nach Komma genau 3 Ziffern → wahrscheinlich Tausendertrennzeichen
                    if len(after_comma) <= 2 and after_comma.isdigit():
                        # Prüfe ob es mehrere Kommata gibt (dann Tausendertrennzeichen)
                        comma_count = str_val.count(',')
                        if comma_count == 1:
                            str_val = str_val.replace(',', '.')
                        else:
                            # Mehrere Kommata → alle entfernen außer dem letzten
                            parts = str_val.split(',')
                            if len(parts) >= 2:
                                integer_part = ''.join(parts[:-1])
                                decimal_part = parts[-1]
                                str_val = f"{integer_part}.{decimal_part}"
                    else:
                        # 3+ Ziffern nach Komma oder nicht-numerisch → Tausendertrennzeichen
                        str_val = str_val.replace(',', '')
                
                try:
                    return float(str_val)
                except ValueError:
                    return None
            
            # Konvertiere Werte mit verbesserter Funktion
            df['Wert_2019'] = df['Wert_2019'].apply(convert_german_number)
            df['Kinder_U3'] = df['Kinder_U3'].apply(convert_german_number)
            
            # Entferne ungültige Daten
            df = df.dropna(subset=['Wert_2019', 'Kinder_U3'])
            df = df[(df['Wert_2019'] >= 0) & (df['Kinder_U3'] >= 0)]
            
            if len(df) == 0:
                messagebox.showwarning("Import-Warnung", "Keine gültigen Daten in der Datei gefunden.")
                return
                
            # Lösche bestehende Daten
            if messagebox.askyesno("Bestätigung", 
                                  f"Sollen die {len(df)} importierten Kommunen die bestehenden Daten ersetzen?"):
                self.kommunen_tree.delete(*self.kommunen_tree.get_children())
                
            # Füge neue Daten hinzu
            imported_count = 0
            for _, row in df.iterrows():
                try:
                    name = str(row['Name']).strip()
                    wert_2019 = float(row['Wert_2019'])
                    kinder_u3 = float(row['Kinder_U3'])  # BUGFIX: Verwende float() statt int() für Konsistenz
                    
                    self.kommunen_tree.insert('', 'end', values=(name, f"{wert_2019:,.2f}", f"{kinder_u3:.6f}"))
                    imported_count += 1
                except:
                    continue
                    
            self.update_calculation_info()
            self.update_status(f"{imported_count} Kommunen importiert", self.colors['ok'])
            messagebox.showinfo("Import erfolgreich", f"{imported_count} Kommunen wurden erfolgreich importiert.")
            
        except Exception as e:
            messagebox.showerror("Import-Fehler", f"Fehler beim Import:\n{str(e)}")
            
    def create_template(self):
        """Erstellt eine Excel-Vorlage"""
        filename = filedialog.asksaveasfilename(
            title="Vorlage speichern",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="import_vorlage.xlsx"
        )
        
        if not filename:
            return
            
        try:
            from foerdermittel_rechner import erstelle_import_vorlage
            erstelle_import_vorlage(filename)
            
            messagebox.showinfo("Vorlage erstellt", 
                              f"Die Import-Vorlage wurde erfolgreich erstellt:\n{filename}")
            self.update_status("Vorlage erstellt", self.colors['ok'])
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der Vorlage:\n{str(e)}")
            
    def export_excel(self):
        """Exportiert die Ergebnisse nach Excel"""
        if self.rechner is None:
            messagebox.showwarning("Keine Ergebnisse", "Bitte führen Sie zuerst eine Berechnung durch.")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Ergebnisse exportieren",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"foerdermittel_ergebnis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if not filename:
            return
            
        try:
            self.rechner.exportiere_excel(filename)
            messagebox.showinfo("Export erfolgreich", 
                              f"Die Ergebnisse wurden erfolgreich exportiert:\n{filename}")
            self.update_status("Export abgeschlossen", self.colors['ok'])
            
        except Exception as e:
            messagebox.showerror("Export-Fehler", f"Fehler beim Export:\n{str(e)}")
            
    def copy_to_clipboard(self):
        """Kopiert die Ergebnisse in die Zwischenablage"""
        if self.rechner is None:
            messagebox.showwarning("Keine Ergebnisse", "Bitte führen Sie zuerst eine Berechnung durch.")
            return
            
        try:
            # Erstelle Text für Zwischenablage
            text_lines = []
            text_lines.append("FÖRDERMITTEL-VERTEILUNGSERGEBNIS")
            text_lines.append("=" * 50)
            text_lines.append(f"Gesamtsumme: {self.rechner.gesamtsumme:,.2f} €")
            text_lines.append(f"Mindestbetrag: {self.rechner.mindestbetrag:,.2f} €")
            text_lines.append(f"Sockelbetrag: {self.rechner.sockelbetrag_prozent*100:.1f}%")
            text_lines.append("")
            
            # Tabellen-Header
            text_lines.append(f"{'Kommune':<20} {'Wert 2019':>12} {'Kinder U3':>10} {'Endbetrag':>12} Status")
            text_lines.append("-" * 80)
            
            # Ergebnisse
            for _, row in self.rechner.ergebnis_df.iterrows():
                text_lines.append(
                    f"{row['Name']:<20} {row['Wert_2019']:>12,.0f} {row['Kinder_U3']:>10} {row['Endbetrag']:>12,.0f} {row['Status']}"
                )
                
            text_lines.append("-" * 80)
            text_lines.append(f"{'SUMME':<20} {'':<12} {'':<10} {self.rechner.ergebnis_df['Endbetrag'].sum():>12,.0f}")
            
            # In Zwischenablage kopieren
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(text_lines))
            
            messagebox.showinfo("Kopiert", "Die Ergebnisse wurden in die Zwischenablage kopiert.")
            self.update_status("In Zwischenablage kopiert", self.colors['ok'])
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Kopieren:\n{str(e)}")


def hide_hidden_files_in_dialogs(root):
    """Blendet in Tks eigenem Dateidialog (Linux) versteckte Dateien aus.

    Über den Schalter im Dialog lassen sie sich weiterhin einblenden.
    """
    try:
        # Der Dialog-Code wird erst beim ersten Aufruf geladen: mit einer
        # ungültigen Option laden, ohne dass ein Dialog erscheint.
        root.tk.call('tk_getOpenFile', '-foobarbaz')
    except tk.TclError:
        pass
    try:
        root.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
        root.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
    except tk.TclError:
        pass


def create_root():
    """Erzeugt das Tk-Hauptfenster mit Fensterklasse und Icon."""
    # Die Fensterklasse (WM_CLASS) verbindet das Fenster unter Linux mit dem
    # Eintrag im Anwendungsmenü (StartupWMClass), damit Dock und Taskleiste
    # das richtige Icon zeigen.
    root = tk.Tk(className='Foerdermittelrechner')

    # Setze Icon (falls vorhanden)
    icon_png = os.path.join(APP_DIR, 'assets', 'icon.png')
    try:
        if os.path.exists(icon_png):
            root._icon_image = tk.PhotoImage(file=icon_png)  # Referenz behalten
            root.iconphoto(True, root._icon_image)
        else:
            root.iconbitmap('icon.ico')
    except tk.TclError:
        pass

    if sys.platform.startswith('linux'):
        hide_hidden_files_in_dialogs(root)

    return root


def main():
    """Hauptfunktion zum Starten der GUI"""
    root = create_root()

    # Erstelle GUI
    app = FoerdermittelGUI(root)

    # Starte Hauptschleife
    root.mainloop()


if __name__ == "__main__":
    main()
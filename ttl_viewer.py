# ttl_viewer.py
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from panel_trips import TripsPanel
from panel_tours import ToursPanel
from panel_times import TimesPanel
from panel_files import FilesPanel
from panel_preview import PreviewPanel

class TTLViewerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parsed_data = {}
        self._build_ui()

    def _build_ui(self):
        menubar = tk.Frame(self, bd=1, relief="raised")
        menubar.pack(fill="x", side="top", pady=2)
        
        ttk.Button(menubar, text="📁 選擇 TTL...", command=self._load_ttl).pack(side="left", padx=2)
        ttk.Button(menubar, text="↩️ 返回上一步", command=self._undo_action).pack(side="left", padx=2)
        ttk.Button(menubar, text="↪️ 返回下一步", command=self._redo_action).pack(side="left", padx=2)
        ttk.Button(menubar, text="📝 修改 Ailist", command=self._set_ai_group).pack(side="left", padx=2)
        
        ttk.Button(menubar, text="⬅ 返回主選單", command=lambda: self.controller.show_frame("MainPage")).pack(side="right", padx=2)
        ttk.Button(menubar, text="📊 前往圖形化時刻表", command=lambda: self.controller.show_frame("TimelineViewerPage")).pack(side="right", padx=2)

        paned_main = tk.PanedWindow(self, orient=tk.VERTICAL, sashwidth=4, sashrelief="raised")
        paned_main.pack(fill="both", expand=True, padx=5, pady=5)

        top_frame = tk.Frame(paned_main)
        paned_main.add(top_frame, stretch="always", height=280)
        for i in range(3): top_frame.columnconfigure(i, weight=1)

        self.panel_trips = TripsPanel(top_frame)
        self.panel_trips.grid(row=0, column=0, sticky="nsew", padx=2)

        self.panel_tours = ToursPanel(top_frame, on_select_callback=self._on_tour_select)
        self.panel_tours.grid(row=0, column=1, sticky="nsew", padx=2)

        self.panel_times = TimesPanel(top_frame)
        self.panel_times.grid(row=0, column=2, sticky="nsew", padx=2)

        bottom_frame = tk.Frame(paned_main)
        paned_main.add(bottom_frame, stretch="always")
        bottom_frame.columnconfigure(1, weight=1)

        self.panel_files = FilesPanel(bottom_frame)
        self.panel_files.grid(row=0, column=0, sticky="nsew", padx=2)

        self.panel_preview = PreviewPanel(bottom_frame)
        self.panel_preview.grid(row=0, column=1, sticky="nsew", padx=5)

    def _undo_action(self):
        try:
            self.panel_preview.text_area.edit_undo()
        except tk.TclError:
            pass 

    def _redo_action(self):
        try:
            self.panel_preview.text_area.edit_redo()
        except tk.TclError:
            pass 

    def load_specific_ttl(self, filepath):
        if not os.path.exists(filepath): return
        filename = os.path.basename(filepath)
        self.panel_files.update_data([filename])
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
        self.panel_preview.update_content(raw_content)
        self._parse_ttl_content(raw_content)

    def _load_ttl(self):
        filepath = filedialog.askopenfilename(title="選擇 TTL 檔案", filetypes=[("OMSI Time Table", "*.ttl")])
        if not filepath: return
        self.load_specific_ttl(filepath)

    def _set_ai_group(self):
        messagebox.showwarning("Warning", "⚠️ Not yet implemented")

    def _parse_ttl_content(self, content):
        self.parsed_data = {}
        all_trips = set()
        current_tour = None
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line == "[newtour]" and i + 2 < len(lines):
                tour_id = lines[i+1].strip()
                ai_group = lines[i+2].strip() 
                
                current_tour = tour_id
                self.parsed_data[current_tour] = {'ai': ai_group, 'trips': []}
                i += 3
                continue
                
            if current_tour and line.startswith("Dep.:"):
                time_val = line.split("Dep.:")[1].strip()
                if i + 2 < len(lines) and lines[i+1].strip() == "[addtrip]":
                    trip_code = lines[i+2].strip()
                    self.parsed_data[current_tour]['trips'].append(f"{time_val} ({trip_code})")
                    all_trips.add(trip_code)
                    i += 2
            i += 1

        self.panel_trips.update_data(sorted(list(all_trips)))
        self.panel_tours.update_data(self.parsed_data)
        self.panel_times.update_data([])

    def _on_tour_select(self, selected_tour_id):
        if selected_tour_id in self.parsed_data:
            times = self.parsed_data[selected_tour_id]['trips']
            self.panel_times.update_data(times)
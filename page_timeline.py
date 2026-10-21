# page_timeline.py
import tkinter as tk
from tkinter import ttk

class TimelineViewerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        top_bar = tk.Frame(self, bd=1, relief="raised")
        top_bar.pack(fill="x", side="top")
        tk.Label(top_bar, text="OMSI 時間表編輯器 (圖形化預覽)", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        ttk.Button(top_bar, text="⬅ 返回主選單", command=lambda: self.controller.show_frame("MainPage")).pack(side="right", padx=5, pady=2)
        ttk.Button(top_bar, text="📁 讀取 TTL...", command=self._mock_load).pack(side="right", padx=5, pady=2)

        paned_main = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=4, sashrelief="raised")
        paned_main.pack(fill="both", expand=True)

        left_panel = tk.Frame(paned_main, width=220)
        paned_main.add(left_panel, stretch="never")
        
        canvas_l = tk.Canvas(left_panel, highlightthickness=0, width=210)
        scrollbar_l = ttk.Scrollbar(left_panel, orient="vertical", command=canvas_l.yview)
        scroll_frame = tk.Frame(canvas_l)
        scroll_frame.bind("<Configure>", lambda e: canvas_l.configure(scrollregion=canvas_l.bbox("all")))
        canvas_l.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas_l.configure(yscrollcommand=scrollbar_l.set)
        canvas_l.pack(side="left", fill="both", expand=True)
        scrollbar_l.pack(side="right", fill="y")

        self._add_left_controls(scroll_frame)

        right_panel = tk.Frame(paned_main, bg="white")
        paned_main.add(right_panel, stretch="always")

        self.timeline_canvas = tk.Canvas(right_panel, bg="white")
        scroll_x = ttk.Scrollbar(right_panel, orient="horizontal", command=self.timeline_canvas.xview)
        scroll_y = ttk.Scrollbar(right_panel, orient="vertical", command=self.timeline_canvas.yview)
        self.timeline_canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.timeline_canvas.pack(side="left", fill="both", expand=True)

        bottom_controls = tk.Frame(self)
        bottom_controls.pack(fill="x", side="bottom", pady=5)
        
        f_zoom = tk.Frame(bottom_controls)
        f_zoom.pack(pady=2)
        tk.Label(f_zoom, text="Zoom (hrs):").pack(side="left")
        ttk.Scale(f_zoom, from_=1, to=24, orient="horizontal", length=300).pack(side="left", padx=10)
        
        f_mid = tk.Frame(bottom_controls)
        f_mid.pack(pady=2)
        tk.Label(f_mid, text="Midpoint (hrs):").pack(side="left")
        ttk.Scale(f_mid, from_=0, to=24, orient="horizontal", length=300).pack(side="left", padx=10)

        self._draw_mock_grid()

    def _add_left_controls(self, parent):
        def make_label(text):
            tk.Label(parent, text=text, font=("Arial", 9)).pack(anchor="w", pady=(5,0))

        make_label("Line")
        ttk.Combobox(parent, values=["KMB - 71A"]).pack(fill="x", padx=5)
        ttk.Button(parent, text="Create").pack(anchor="w", padx=5, pady=2)
        
        tk.Checkbutton(parent, text="User is allowed to drive this line").pack(anchor="w")
        
        f_prio = tk.Frame(parent)
        f_prio.pack(fill="x", padx=5)
        tk.Label(f_prio, text="Priority:").pack(side="left")
        ttk.Entry(f_prio, width=5).pack(side="right")

        make_label("Tour")
        ttk.Combobox(parent, values=["71A-20", "71A-21"]).pack(fill="x", padx=5)
        ttk.Button(parent, text="Create").pack(anchor="w", padx=5, pady=2)

        make_label("AI-Veh. Group:")
        ttk.Combobox(parent, values=["KMB_ATENU"]).pack(fill="x", padx=5)

        make_label("Conditions:")
        f_cond = tk.Frame(parent)
        f_cond.pack(fill="x", padx=5)
        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Holiday", "No Hol.", "Hol."]):
            tk.Checkbutton(f_cond, text=day).grid(row=i%5, column=i//5, sticky="w")

        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)

        f_btns = tk.Frame(parent)
        f_btns.pack(fill="x", padx=5)
        ttk.Button(f_btns, text="Delete").pack(side="left", expand=True, padx=2)
        ttk.Button(f_btns, text="NEW").pack(side="left", expand=True, padx=2)

        make_label("Dep. Time:")
        f_time = tk.Frame(parent)
        f_time.pack(fill="x", padx=5)
        ttk.Entry(f_time, width=5).pack(side="left")
        tk.Label(f_time, text=":").pack(side="left")
        ttk.Entry(f_time, width=5).pack(side="left")

        make_label("Trip:")
        ttk.Combobox(parent, values=["71A_TPM"]).pack(fill="x", padx=5)
        
        make_label("Time Profile:")
        ttk.Combobox(parent, values=["71A_TPM_Profile"]).pack(fill="x", padx=5)

    def _draw_mock_grid(self):
        self.timeline_canvas.delete("all")
        canvas_width = 2400
        canvas_height = 800
        self.timeline_canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

        for hour in range(24):
            x = hour * 100
            self.timeline_canvas.create_line(x, 0, x, canvas_height, fill="#dddddd")
            self.timeline_canvas.create_text(x + 5, 10, text=f"{hour}:00", anchor="nw")

        for row in range(1, 10):
            y = row * 60
            self.timeline_canvas.create_line(0, y, canvas_width, y, fill="#aaaaaa")
            self.timeline_canvas.create_text(5, y + 10, text=f"Tour {row}", anchor="nw", fill="gray")

    def _mock_load(self):
        self.timeline_canvas.create_rectangle(550, 65, 600, 115, fill="#cc3333", outline="black")
        self.timeline_canvas.create_text(575, 90, text="71A", fill="white", font=("Arial", 7))
        
        self.timeline_canvas.create_rectangle(620, 65, 670, 115, fill="#993333", outline="black")
        self.timeline_canvas.create_text(645, 90, text="71A", fill="white", font=("Arial", 7))
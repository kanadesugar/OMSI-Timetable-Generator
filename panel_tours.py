import tkinter as tk

class ToursPanel(tk.Frame):
    def __init__(self, parent, on_select_callback=None):
        super().__init__(parent)
        self.on_select_callback = on_select_callback
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self)
        header.pack(fill="x")
        tk.Label(header, text="車序 (Tour) [AI群組]", font=("Arial", 12)).pack(side="left", expand=True)
        
        btn_f = tk.Frame(header)
        btn_f.pack(side="right")
        tk.Label(btn_f, text="s\no\nr\nt").pack(side="left")
        
        b_col = tk.Frame(btn_f)
        b_col.pack(side="left")
        tk.Button(b_col, text="Add", height=1).pack(fill="x")
        tk.Button(b_col, text="Remove", height=1).pack(fill="x")
        tk.Button(b_col, text="Duplicate", height=1).pack(fill="x")
        
        arr_f = tk.Frame(b_col)
        arr_f.pack(fill="x")
        tk.Button(arr_f, text="↑", width=2).pack(side="left", expand=True)
        tk.Button(arr_f, text="↓", width=2).pack(side="right", expand=True)

        self.listbox = tk.Listbox(self, font=("Arial", 10), exportselection=False)
        self.listbox.pack(fill="both", expand=True, pady=2)
        
        if self.on_select_callback:
            self.listbox.bind("<<ListboxSelect>>", self._handle_select)

    def _handle_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            selected_text = self.listbox.get(selection[0])
            actual_tour_id = selected_text.split(" [")[0].strip()
            self.on_select_callback(actual_tour_id)

    def update_data(self, tours_dict):
        self.listbox.delete(0, tk.END)
        for tour_id, data in tours_dict.items():
            ai_group = data.get('ai', '未知')
            display_text = f"{tour_id} [{ai_group}]"
            self.listbox.insert(tk.END, display_text)
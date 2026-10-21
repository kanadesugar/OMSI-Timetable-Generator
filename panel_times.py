import tkinter as tk

class TimesPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self)
        header.pack(fill="x")
        tk.Label(header, text="班次時間", font=("Arial", 12)).pack(side="left", expand=True)
        
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

    def update_data(self, data_list):
        self.listbox.delete(0, tk.END)
        for item in data_list:
            self.listbox.insert(tk.END, item)
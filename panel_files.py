import tkinter as tk

class FilesPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        r_head1 = tk.Frame(self)
        r_head1.pack(fill="x")
        tk.Label(r_head1, text="檔案 (TTL)", font=("Arial", 12)).pack(side="left")
        tk.Button(r_head1, text="Add").pack(side="left", padx=1)
        tk.Button(r_head1, text="Duplicate").pack(side="left", padx=1)
        
        r_head2 = tk.Frame(self)
        r_head2.pack(fill="x", pady=2)
        tk.Button(r_head2, text="↑", width=2).pack(side="left")
        tk.Button(r_head2, text="↓", width=2).pack(side="left")
        tk.Button(r_head2, text="Remove").pack(side="left", padx=1)
        tk.Button(r_head2, text="Check Val.").pack(side="left", padx=1)
        
        self.listbox = tk.Listbox(self, font=("Arial", 10))
        self.listbox.pack(fill="both", expand=True)

    def update_data(self, data_list):
        self.listbox.delete(0, tk.END)
        for item in data_list:
            self.listbox.insert(tk.END, item)
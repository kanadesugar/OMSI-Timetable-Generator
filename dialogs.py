import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class TripCodeDialog(tk.Toplevel):
    def __init__(self, parent, target_entry, route_entry):
        super().__init__(parent)
        self.title("Trip Code 設定")
        self.geometry("420x330")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.target_entry = target_entry
        self.route_str = route_entry.get().strip()
        self.route_num = self.route_str.split()[-1] if " " in self.route_str else self.route_str
        if not self.route_num: self.route_num = "Route"

        self.mode_var = tk.IntVar(value=1)
        self.preview_var = tk.StringVar(value=f"{self.route_num}_")
        self.parsed_trips = []

        self._build_ui()
        self._update_preview()

    def _build_ui(self):
        tk.Radiobutton(self, text="自動デフォルト (路線 + 地名頭文字)", variable=self.mode_var, value=1, command=self._update_preview).pack(anchor="w", padx=15, pady=(10, 2))
        f_auto = tk.Frame(self)
        f_auto.pack(fill="x", padx=35)
        tk.Label(f_auto, text="地名英語:").pack(side="left")
        self.ent_place = ttk.Entry(f_auto, width=28)
        self.ent_place.pack(side="left", padx=5)
        self.ent_place.insert(0, "Tsz Wan Shan South")
        self.ent_place.bind("<KeyRelease>", self._update_preview)

        tk.Radiobutton(self, text="手動入力コード", variable=self.mode_var, value=2, command=self._update_preview).pack(anchor="w", padx=15, pady=(5, 2))
        f_manual = tk.Frame(self)
        f_manual.pack(fill="x", padx=35)
        tk.Label(f_manual, text="コード:").pack(side="left")
        self.ent_manual = ttk.Entry(f_manual, width=28)
        self.ent_manual.pack(side="left", padx=5)
        self.ent_manual.bind("<KeyRelease>", self._update_preview)

        tk.Radiobutton(self, text="OMSI ttdataファイルから読み込む (.ttp / .ttr)", variable=self.mode_var, value=3, command=self._update_preview).pack(anchor="w", padx=15, pady=(5, 2))
        f_ttdata = tk.Frame(self)
        f_ttdata.pack(fill="x", padx=35)
        
        self.lbl_ttdata_file = tk.Label(f_ttdata, text="ファイル未選択", fg="gray", font=("Arial", 9))
        self.lbl_ttdata_file.pack(anchor="w", pady=(0, 3))
        
        f_ttdata_inner = tk.Frame(f_ttdata)
        f_ttdata_inner.pack(fill="x")
        ttk.Button(f_ttdata_inner, text="ファイル選択...", command=self._browse_ttdata).pack(side="left")
        
        self.combo_trips = ttk.Combobox(f_ttdata_inner, width=20, state="readonly")
        self.combo_trips.pack(side="left", padx=10)
        self.combo_trips.bind("<<ComboboxSelected>>", self._update_preview)

        f_preview = tk.Frame(self)
        f_preview.pack(fill="x", padx=15, pady=15)
        tk.Label(f_preview, text="プレビュー: ", font=("Arial", 10, "bold")).pack(side="left")
        tk.Label(f_preview, textvariable=self.preview_var, fg="blue", font=("Arial", 11, "bold")).pack(side="left")

        f_btn = tk.Frame(self)
        f_btn.pack(pady=5)
        ttk.Button(f_btn, text="確定", command=self._confirm).pack(side="left", padx=10)
        ttk.Button(f_btn, text="キャンセル", command=self.destroy).pack(side="left", padx=10)

    def _browse_ttdata(self):
        filepath = filedialog.askopenfilename(title="OMSIトリップファイル選択", filetypes=[("OMSI Trip Files", "*.ttp *.ttr")])
        if not filepath: return
        try:
            trips = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f.readlines()]
                for i, line in enumerate(lines):
                    if line == "[trip]" and i + 1 < len(lines):
                        trip_name = lines[i+1].strip()
                        if trip_name and trip_name not in trips: trips.append(trip_name)
            if trips:
                self.parsed_trips = trips
                self.combo_trips['values'] = self.parsed_trips
                self.combo_trips.current(0)
                self.mode_var.set(3)
                self._update_preview()
                
                filename = os.path.basename(filepath)
                self.lbl_ttdata_file.config(text=f"✅ 読込成功: {filename} ({len(trips)}件)", fg="green")
                messagebox.showinfo("成功", f"{filename} から {len(trips)} 件のトリップコードを抽出しました！")
            else:
                self.lbl_ttdata_file.config(text="⚠️ 有効なトリップコードなし", fg="red")
                messagebox.showwarning("警告", "ファイル内に [trip] コードが見つかりませんでした。")
        except Exception as e:
            self.lbl_ttdata_file.config(text="❌ 読込失敗", fg="red")
            messagebox.showerror("エラー", f"ファイル読込失敗: {e}")

    def _update_preview(self, event=None):
        if self.mode_var.get() == 1:
            place = self.ent_place.get().strip()
            words = re.split(r'[\s\-]+', place)
            initials = "".join([w[0].upper() for w in words if w])
            self.preview_var.set(f"{self.route_num}_{initials}" if initials else f"{self.route_num}_")
        elif self.mode_var.get() == 2:
            self.preview_var.set(self.ent_manual.get().strip())
        elif self.mode_var.get() == 3:
            self.preview_var.set(self.combo_trips.get() if self.combo_trips.get() else "(ファイルを選択してください)")

    def _confirm(self):
        code = self.preview_var.get().strip()
        if code and not code.startswith("("):
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, code)
        self.destroy()

class TourIDEditDialog(tk.Toplevel):
    def __init__(self, parent, tour_ids, summary_text, confirm_callback, cancel_callback):
        super().__init__(parent)
        self.title("Tour ID 確認と修正")
        self.geometry("450x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.tour_ids = tour_ids
        self.summary_text = summary_text
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback
        self.entries = {}

        self._build_ui()

    def _build_ui(self):
        lbl_info = tk.Label(self, text=self.summary_text, justify="left", font=("Arial", 9))
        lbl_info.pack(pady=10, padx=10, fill="x")
        
        tk.Label(self, text="検出された Tour_ID です。誤りがあれば右側の入力欄で修正できます：", fg="blue", justify="left").pack(padx=10, anchor="w")

        container = tk.Frame(self, bd=1, relief="sunken")
        container.pack(fill="both", expand=True, padx=10, pady=5)
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(scrollable_frame, text="元の Tour ID", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(scrollable_frame, text="修正後", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        for i, t_id in enumerate(self.tour_ids):
            ttk.Label(scrollable_frame, text=t_id).grid(row=i+1, column=0, padx=10, pady=2, sticky="w")
            ent = ttk.Entry(scrollable_frame, width=22)
            ent.insert(0, t_id)
            ent.grid(row=i+1, column=1, padx=10, pady=2, sticky="w")
            self.entries[t_id] = ent

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="確定して生成", command=self._on_confirm).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="キャンセル", command=self._on_cancel).pack(side="left", padx=10)

    def _on_confirm(self):
        mapping = {}
        for old_id, ent in self.entries.items():
            new_val = ent.get().strip()
            mapping[old_id] = new_val if new_val else old_id
        self.destroy()
        self.confirm_callback(mapping)

    def _on_cancel(self):
        self.destroy()
        self.cancel_callback()
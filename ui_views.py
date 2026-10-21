# ui_views.py
import os
import re
import threading
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from PIL import Image, ImageTk
from datetime import datetime

from ttl_core import build_ttl_content, save_ttl_file, generate_trip_entry
from data_importer import fetch_wiki_timetable, parse_multi_route_excel
from dialogs import TripCodeDialog, TourIDEditDialog

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        if os.path.exists("bg.jpg"):
            try:
                img = Image.open("bg.jpg").resize((800, 680), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img)
                tk.Label(self, image=self.bg_photo).place(x=0, y=0, relwidth=1, relheight=1)
            except Exception: pass
        
        box = tk.Frame(self, bg="#ffffff", bd=2, relief="groove")
        box.place(relx=0.5, rely=0.5, anchor="center", width=520, height=270)
        
        tk.Label(box, text="OMSI 時間表生成系統", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=15)
        
        btn_frame = tk.Frame(box, bg="#ffffff")
        btn_frame.pack(pady=10)
        
        b1 = ttk.Button(btn_frame, text="✏️ 手動建立模式", width=22, command=lambda: controller.show_frame("ManualPage"))
        b2 = ttk.Button(btn_frame, text="🌐 API / Excel 匯入", width=22, command=lambda: controller.show_frame("AutoPage"))
        b3 = ttk.Button(btn_frame, text="🔍 TTL 檢視器 (HOF Style)", width=22, command=lambda: controller.show_frame("TTLViewerPage"))
        b4 = ttk.Button(btn_frame, text="📊 圖形化時間表預覽", width=22, command=lambda: controller.show_frame("TimelineViewerPage"))
        
        b1.grid(row=0, column=0, padx=8, pady=8)
        b2.grid(row=0, column=1, padx=8, pady=8)
        b3.grid(row=1, column=0, padx=8, pady=8)
        b4.grid(row=1, column=1, padx=8, pady=8)

class ManualPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        top_bar = tk.Frame(self)
        top_bar.pack(fill="x", padx=10, pady=8)
        ttk.Button(top_bar, text="⬅ 返回主選單", command=lambda: controller.show_frame("MainPage")).pack(side="left")
        tk.Label(top_bar, text="手動建立時間表", font=("Arial", 12, "bold")).pack(side="left", padx=20)
        
        cfg_frame = ttk.LabelFrame(self, text="路線與運行資訊", padding=8)
        cfg_frame.pack(fill="x", padx=10, pady=4)
        
        ttk.Label(cfg_frame, text="路線名稱:").grid(row=0, column=0, sticky="w")
        self.ent_route = ttk.Entry(cfg_frame, width=12)
        self.ent_route.insert(0, "KMB 76K")
        self.ent_route.grid(row=0, column=1, padx=4, pady=2)
        
        ttk.Label(cfg_frame, text="Dir 1 代碼:").grid(row=0, column=2, sticky="w")
        f_dir1 = tk.Frame(cfg_frame)
        f_dir1.grid(row=0, column=3, padx=4, pady=2, sticky="w")
        self.ent_dir1 = ttk.Entry(f_dir1, width=12)
        self.ent_dir1.insert(0, "76K_LP")
        self.ent_dir1.pack(side="left")
        ttk.Button(f_dir1, text="⚙️", width=3, command=lambda: TripCodeDialog(self, self.ent_dir1, self.ent_route)).pack(side="left", padx=2)
        
        ttk.Label(cfg_frame, text="Dir 2 代碼:").grid(row=0, column=4, sticky="w")
        f_dir2 = tk.Frame(cfg_frame)
        f_dir2.grid(row=0, column=5, padx=4, pady=2, sticky="w")
        self.ent_dir2 = ttk.Entry(f_dir2, width=12)
        self.ent_dir2.insert(0, "76K_CH")
        self.ent_dir2.pack(side="left")
        ttk.Button(f_dir2, text="⚙️", width=3, command=lambda: TripCodeDialog(self, self.ent_dir2, self.ent_route)).pack(side="left", padx=2)
        
        self.sp_active = tk.BooleanVar(value=False)
        ttk.Checkbutton(cfg_frame, text="啟用特別班次代碼", variable=self.sp_active, command=self._toggle_sp).grid(row=1, column=0, columnspan=2, sticky="w", pady=4)
        
        self.sp_subframe = tk.Frame(cfg_frame)
        ttk.Label(self.sp_subframe, text="符號:").pack(side="left")
        self.ent_sym = ttk.Entry(self.sp_subframe, width=4)
        self.ent_sym.pack(side="left", padx=2)
        ttk.Label(self.sp_subframe, text="代碼:").pack(side="left", padx=4)
        self.ent_sp_code = ttk.Entry(self.sp_subframe, width=14)
        self.ent_sp_code.pack(side="left", padx=2)
        ttk.Button(self.sp_subframe, text="⚙️", width=3, command=lambda: TripCodeDialog(self, self.ent_sp_code, self.ent_route)).pack(side="left", padx=2)

        out_frame = tk.Frame(cfg_frame)
        out_frame.grid(row=2, column=0, columnspan=6, sticky="w", pady=4)
        
        ttk.Label(out_frame, text="AI 群組:").pack(side="left")
        self.combo_ai = ttk.Combobox(out_frame, width=15)
        self.combo_ai.pack(side="left", padx=2)
        ttk.Button(out_frame, text="讀取 Ailist...", command=self._browse_ailist).pack(side="left", padx=(0, 10))

        ttk.Label(out_frame, text="前綴:").pack(side="left")
        self.ent_out_name = ttk.Entry(out_frame, width=12)
        self.ent_out_name.insert(0, "Manual_Line")
        self.ent_out_name.pack(side="left", padx=4)
        
        ttk.Label(out_frame, text="運用數:").pack(side="left", padx=(5, 2))
        self.ent_max_tours = ttk.Entry(out_frame, width=4)
        self.ent_max_tours.insert(0, "8")
        self.ent_max_tours.pack(side="left")

        self.tabs = {}
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=4)
        
        for tab_name, day_key in [("平日", "1-5"), ("星期六", "6"), ("星期日/假期", "7")]:
            tab_frame = tk.Frame(notebook)
            notebook.add(tab_frame, text=tab_name)
            tk.Label(tab_frame, text="去程發車時間 (以空格或換行分隔):").pack(anchor="w", padx=6, pady=2)
            t1 = scrolledtext.ScrolledText(tab_frame, height=4)
            t1.pack(fill="x", padx=6, pady=2)
            tk.Label(tab_frame, text="回程發車時間 (以空格或換行分隔):").pack(anchor="w", padx=6, pady=2)
            t2 = scrolledtext.ScrolledText(tab_frame, height=4)
            t2.pack(fill="x", padx=6, pady=2)
            self.tabs[day_key] = (t1, t2)
            
        ttk.Button(self, text="生成 TTL 檔案", command=self._execute_manual).pack(pady=4)
        self.txt_log = scrolledtext.ScrolledText(self, height=6)
        self.txt_log.pack(fill="x", padx=10, pady=4)

    def _browse_ailist(self):
        filepath = filedialog.askopenfilename(title="選擇 ailists.cfg", filetypes=[("OMSI Ailist", "*.cfg"), ("All Files", "*.*")])
        if not filepath: return
        try:
            groups = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f.readlines()]
                for i, line in enumerate(lines):
                    if line in ("[aigroup]", "[aigroup_2]", "[aigroup_depot]"):
                        if i + 1 < len(lines):
                            g_name = lines[i+1].strip()
                            if g_name and g_name not in groups: groups.append(g_name)
            if groups:
                self.combo_ai['values'] = groups
                self.combo_ai.current(0)
                messagebox.showinfo("成功", f"已成功載入 {len(groups)} 個 AI 群組！")
            else:
                messagebox.showwarning("警告", "檔案內找不到 AI 群組標籤。")
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取 Ailist 失敗: {e}")

    def _toggle_sp(self):
        if self.sp_active.get(): self.sp_subframe.grid(row=1, column=2, columnspan=4, sticky="w", padx=6)
        else: self.sp_subframe.grid_remove()

    def _log(self, msg):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)
        if "❌" in msg or "失敗" in msg or "錯誤" in msg or "警告" in msg: logging.error(msg)
        else: logging.info(msg)

    def _execute_manual(self):
        route = self.ent_route.get().strip()
        if not route:
            messagebox.showwarning("警告", "請輸入路線名稱！")
            return
            
        try: max_tours = int(self.ent_max_tours.get().strip())
        except: max_tours = 8
            
        ai_group = self.combo_ai.get().strip()
        logging.info(f"開始手動生成 - 路線: {route}, AI: {ai_group}, 運用數: {max_tours}")
        
        specials = {self.ent_sym.get().strip(): self.ent_sp_code.get().strip()} if self.sp_active.get() and self.ent_sym.get().strip() else {}
        prefix = self.ent_out_name.get().strip() or "Output"
        
        for day_key, (t1_box, t2_box) in self.tabs.items():
            dir1_times = re.findall(r'\d{2}:\d{2}[^\s,]*', t1_box.get("1.0", tk.END))
            dir2_times = re.findall(r'\d{2}:\d{2}[^\s,]*', t2_box.get("1.0", tk.END))
            content = build_ttl_content(route, ai_group, specials, self.ent_dir1.get().strip(), dir1_times, self.ent_dir2.get().strip(), dir2_times, max_tours)
            if content: save_ttl_file(f"{prefix}_{day_key}.ttl", content, self._log)
        self._log("🎉 手動時間表處理完成！")

class AutoPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        top_bar = tk.Frame(self)
        top_bar.pack(fill="x", padx=10, pady=8)
        ttk.Button(top_bar, text="⬅ 返回主選單", command=lambda: controller.show_frame("MainPage")).pack(side="left")
        tk.Label(top_bar, text="自動資料匯入", font=("Arial", 12, "bold")).pack(side="left", padx=20)
        
        cfg_frame = ttk.LabelFrame(self, text="路線與資訊 (API 用)", padding=8)
        cfg_frame.pack(fill="x", padx=10, pady=4)
        
        ttk.Label(cfg_frame, text="路線名稱:").grid(row=0, column=0, sticky="w")
        self.ent_route = ttk.Entry(cfg_frame, width=12)
        self.ent_route.insert(0, "KMB 76K")
        self.ent_route.grid(row=0, column=1, padx=4, pady=2)
        
        ttk.Label(cfg_frame, text="Dir 1:").grid(row=0, column=2, sticky="w")
        f_dir1 = tk.Frame(cfg_frame)
        f_dir1.grid(row=0, column=3, padx=4, pady=2, sticky="w")
        self.ent_dir1 = ttk.Entry(f_dir1, width=12)
        self.ent_dir1.insert(0, "76K_LP")
        self.ent_dir1.pack(side="left")
        ttk.Button(f_dir1, text="⚙️", width=3, command=lambda: TripCodeDialog(self, self.ent_dir1, self.ent_route)).pack(side="left", padx=2)
        
        ttk.Label(cfg_frame, text="Dir 2:").grid(row=0, column=4, sticky="w")
        f_dir2 = tk.Frame(cfg_frame)
        f_dir2.grid(row=0, column=5, padx=4, pady=2, sticky="w")
        self.ent_dir2 = ttk.Entry(f_dir2, width=12)
        self.ent_dir2.insert(0, "76K_CH")
        self.ent_dir2.pack(side="left")
        ttk.Button(f_dir2, text="⚙️", width=3, command=lambda: TripCodeDialog(self, self.ent_dir2, self.ent_route)).pack(side="left", padx=2)

        out_frame = tk.Frame(cfg_frame)
        out_frame.grid(row=1, column=0, columnspan=6, sticky="w", pady=4)
        
        ttk.Label(out_frame, text="AI 群組:").pack(side="left")
        self.combo_ai = ttk.Combobox(out_frame, width=15)
        self.combo_ai.pack(side="left", padx=2)
        ttk.Button(out_frame, text="讀取 Ailist...", command=self._browse_ailist).pack(side="left", padx=(0, 10))

        ttk.Label(out_frame, text="前綴:").pack(side="left")
        self.ent_out_name = ttk.Entry(out_frame, width=12)
        self.ent_out_name.insert(0, "Combined_Schedule")
        self.ent_out_name.pack(side="left", padx=4)
        
        ttk.Label(out_frame, text="運用數:").pack(side="left", padx=(5, 2))
        self.ent_max_tours = ttk.Entry(out_frame, width=4)
        self.ent_max_tours.insert(0, "8")
        self.ent_max_tours.pack(side="left")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=6)
        
        wiki_tab = tk.Frame(notebook)
        notebook.add(wiki_tab, text="🌐 Wiki API 讀取")
        ttk.Label(wiki_tab, text="HK Bus Fandom 頁面名稱:").pack(anchor="w", padx=10, pady=4)
        self.ent_wiki = ttk.Entry(wiki_tab, width=45)
        self.ent_wiki.insert(0, "九巴76K線/詳細時間表")
        self.ent_wiki.pack(anchor="w", padx=10, pady=2)
        ttk.Button(wiki_tab, text="從 API 獲取並生成", command=self._start_api_thread).pack(anchor="w", padx=10, pady=10)
        
        excel_tab = tk.Frame(notebook)
        notebook.add(excel_tab, text="📊 讀取 Excel")
        ttk.Label(excel_tab, text="選擇包含 Route, Day_Type, Dep_Time, Trip_Code 的 Excel 檔案:").pack(anchor="w", padx=10, pady=4)
        f_row = tk.Frame(excel_tab)
        f_row.pack(anchor="w", padx=10, pady=2)
        self.ent_excel_path = ttk.Entry(f_row, width=38)
        self.ent_excel_path.pack(side="left", padx=2)
        ttk.Button(f_row, text="瀏覽...", command=self._browse_excel).pack(side="left", padx=4)
        ttk.Button(excel_tab, text="讀取 Excel 並生成", command=self._start_excel_thread).pack(anchor="w", padx=10, pady=10)
        
        self.txt_log = scrolledtext.ScrolledText(self, height=8)
        self.txt_log.pack(fill="x", padx=10, pady=6)

    def _browse_ailist(self):
        filepath = filedialog.askopenfilename(title="選擇 ailists.cfg", filetypes=[("OMSI Ailist", "*.cfg"), ("All Files", "*.*")])
        if not filepath: return
        try:
            groups = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f.readlines()]
                for i, line in enumerate(lines):
                    if line in ("[aigroup]", "[aigroup_2]", "[aigroup_depot]"):
                        if i + 1 < len(lines):
                            g_name = lines[i+1].strip()
                            if g_name and g_name not in groups: groups.append(g_name)
            if groups:
                self.combo_ai['values'] = groups
                self.combo_ai.current(0)
                messagebox.showinfo("成功", f"已成功載入 {len(groups)} 個 AI 群組！")
            else:
                messagebox.showwarning("警告", "找不到 AI 群組。")
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取 Ailist 失敗: {e}")

    def _log(self, msg):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)
        if "❌" in msg or "失敗" in msg or "錯誤" in msg or "警告" in msg: logging.error(msg)
        else: logging.info(msg)

    def _browse_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel 試算表", "*.xlsx")])
        if path:
            self.ent_excel_path.delete(0, tk.END)
            self.ent_excel_path.insert(0, path)

    def _get_specials(self):
        return {"＊": "76K_WM - LP", "＃": "76K_CH - PSO", "*": "76K_WM - LP", "#": "76K_CH - PSO"}

    def _auto_jump_to_viewer(self, target_file):
        viewer = self.controller.frames["TTLViewerPage"]
        viewer.load_specific_ttl(target_file)
        self.controller.show_frame("TTLViewerPage")

    def _start_api_thread(self): threading.Thread(target=self._fetch_api_task, daemon=True).start()

    def _fetch_api_task(self):
        wiki_title = self.ent_wiki.get().strip()
        route = self.ent_route.get().strip()
        if not wiki_title or not route:
            self.after(0, lambda: messagebox.showwarning("警告", "請輸入路線與 Wiki 頁面名稱！"))
            return
            
        try: max_tours = int(self.ent_max_tours.get().strip())
        except: max_tours = 8
            
        ai_group = self.combo_ai.get().strip()
        logging.info(f"開始 API 獲取 - 路線: {route}, AI: {ai_group}, 運用數: {max_tours}")
        
        data = fetch_wiki_timetable(wiki_title, lambda msg: self.after(0, self._log, msg))
        if data:
            self.after(0, self._confirm_api_data, data, route, ai_group, max_tours)

    def _confirm_api_data(self, data, route, ai_group, max_tours):
        total_wd = len(data['Weekday_Dir1']) + len(data['Weekday_Dir2'])
        total_sat = len(data['Saturday_Dir1']) + len(data['Saturday_Dir2'])
        total_sun = len(data['Sunday_Dir1']) + len(data['Sunday_Dir2'])
        
        msg = (f"API 讀取完成！請確認以下內容：\n\n路線: {route}\nAI: {ai_group if ai_group else '(使用路線名稱)'}\n運用數: {max_tours}\n\n"
               f"平日: {total_wd} 班\n星期六: {total_sat} 班\n星期日: {total_sun} 班\n\n是否生成 TTL 檔案？")
               
        if not messagebox.askyesno("確認", msg):
            self._log("⚠️ 已取消 API 匯入。")
            return
            
        threading.Thread(target=self._generate_api_ttls, args=(data, route, ai_group, max_tours), daemon=True).start()

    def _generate_api_ttls(self, data, route, ai_group, max_tours):
        prefix = self.ent_out_name.get().strip() or "API_Output"
        specials = self._get_specials()
        dir1_code = self.ent_dir1.get().strip()
        dir2_code = self.ent_dir2.get().strip()

        for day_tag, key_suffix in [('Weekday', '1-5'), ('Saturday', '6'), ('Sunday', '7')]:
            content = build_ttl_content(route, ai_group, specials, dir1_code, data[f'{day_tag}_Dir1'], dir2_code, data[f'{day_tag}_Dir2'], max_tours)
            if content: self.after(0, save_ttl_file, f"{prefix}_{key_suffix}.ttl", content, self._log)
            
        last_generated_file = f"{prefix}_1-5.ttl"
        self.after(0, self._log, "🎉 Wiki API 匯入完成！已自動載入至檢視器。")
        self.after(500, lambda: self._auto_jump_to_viewer(last_generated_file))

    def _start_excel_thread(self): threading.Thread(target=self._fetch_excel_task, daemon=True).start()

    def _fetch_excel_task(self):
        filepath = self.ent_excel_path.get().strip()
        if not os.path.exists(filepath):
            self.after(0, lambda: messagebox.showwarning("警告", "Excel 檔案路徑不存在！"))
            return
            
        try: max_tours = int(self.ent_max_tours.get().strip())
        except: max_tours = 8
            
        prefix = self.ent_out_name.get().strip() or "Excel_Output"
        logging.info(f"開始 Excel 匯入 - 檔案: {filepath}")
        try:
            df, has_tour_id = parse_multi_route_excel(filepath)
            self.after(0, self._confirm_excel_data, df, has_tour_id, max_tours, prefix)
        except Exception as e:
            self.after(0, lambda: self._log(f"❌ 讀取 Excel 失敗: {e}"))
            logging.error("Excel 匯入失敗", exc_info=True)

    def _confirm_excel_data(self, df, has_tour_id, max_tours, prefix):
        routes_found = df['Route'].unique().tolist()
        codes_found = df['Trip_Code'].unique().tolist()
        ai_group_ui = self.combo_ai.get().strip()
        
        routes_str = ", ".join(routes_found)[:80]
        codes_str = ", ".join(codes_found)[:80]
        
        summary_msg = (f"路線 ({len(routes_found)} 個): {routes_str}\n"
                       f"代碼 ({len(codes_found)} 種): {codes_str}\n"
                       f"AI: {ai_group_ui if ai_group_ui else '(依路線)'}\n"
                       f"總班次: {len(df)} 班\n")

        if has_tour_id:
            unique_tours = df['Tour_ID'].unique().tolist()
            TourIDEditDialog(
                self, 
                unique_tours,
                summary_text=f"【自訂 Tour_ID 模式】\n{summary_msg}",
                confirm_callback=lambda mapping: threading.Thread(target=self._generate_excel_ttls, args=(df, has_tour_id, max_tours, prefix, mapping, ai_group_ui), daemon=True).start(),
                cancel_callback=lambda: self._log("⚠️ 已取消 Excel 匯入。")
            )
        else:
            msg = (f"Excel 讀取完成！請確認以下內容：\n\n【自動運用輪替】\n{summary_msg}\n是否生成 TTL 檔案？")
            if messagebox.askyesno("確認", msg):
                threading.Thread(target=self._generate_excel_ttls, args=(df, has_tour_id, max_tours, prefix, None, ai_group_ui), daemon=True).start()
            else:
                self._log("⚠️ 已取消 Excel 匯入。")

    def _generate_excel_ttls(self, df, has_tour_id, max_tours, prefix, mapping, ai_group_ui):
        if mapping:
            df['Tour_ID'] = df['Tour_ID'].map(mapping).fillna(df['Tour_ID'])

        today = datetime.now().strftime("%d/%m/%Y")
        last_filename = ""
        try:
            for day_type, day_group in df.groupby('Day_Type'):
                filename = f"{prefix}_{day_type.strip()}.ttl"
                last_filename = filename
                lines = ["-----------------------", "Time Table Line File", "-----------------------\n",
                         "Created by OMSI Multi-Route Generator", f"Date: {today}\n", "[userallowed]\n", "[priority]\n1",
                         "------------------------------------\n"]
                
                if has_tour_id:
                    for tour_id, tour_group in day_group.groupby('Tour_ID'):
                        tour_id = str(tour_id).strip()
                        route_name = str(tour_group.iloc[0]['Route']).strip()
                        actual_ai = ai_group_ui if ai_group_ui else route_name
                        
                        trips = []
                        for _, row in tour_group.iterrows():
                            dep_time = str(row['Dep_Time']).strip()
                            time_parts = dep_time.split(":")
                            if len(time_parts) >= 2: dep_time = f"{int(time_parts[0]):02d}:{int(time_parts[1]):02d}"
                            trips.append((dep_time, str(row['Trip_Code']).strip()))
                            
                        trips.sort(key=lambda x: int(x[0].split(":")[0]) * 60 + int(x[0].split(":")[1]))
                        lines.append(f"[newtour]\n{tour_id}\n{actual_ai}\n1023\n")
                        lines.append("------------------------------------\n")
                        for time_str, code in trips:
                            entry = generate_trip_entry(time_str, code, {})
                            if entry: lines.append(entry)
                        lines.append("------------------------------------\n")
                else:
                    for route_name, route_group in day_group.groupby('Route'):
                        route_name = route_name.strip()
                        route_num = route_name.split()[-1] if " " in route_name else route_name
                        actual_ai = ai_group_ui if ai_group_ui else route_name
                        
                        trips = []
                        for _, row in route_group.iterrows():
                            dep_time = str(row['Dep_Time']).strip()
                            time_parts = dep_time.split(":")
                            if len(time_parts) >= 2: dep_time = f"{int(time_parts[0]):02d}:{int(time_parts[1]):02d}"
                            trips.append((dep_time, str(row['Trip_Code']).strip()))
                            
                        trips.sort(key=lambda x: int(x[0].split(":")[0]) * 60 + int(x[0].split(":")[1]))
                        tours_data = {i: [] for i in range(max_tours)}
                        for i, (time_str, code) in enumerate(trips):
                            tours_data[i % max_tours].append((time_str, code))
                            
                        for i in range(max_tours):
                            if not tours_data[i]: continue
                            tour_id = f"{route_num}-{i+1:03d}"
                            lines.append(f"[newtour]\n{tour_id}\n{actual_ai}\n1023\n")
                            lines.append("------------------------------------\n")
                            for time_str, code in tours_data[i]:
                                entry = generate_trip_entry(time_str, code, {})
                                if entry: lines.append(entry)
                            lines.append("------------------------------------\n")
                
                self.after(0, save_ttl_file, filename, "\n".join(lines), self._log)
            
            self.after(0, self._log, "🎉 Excel 時間表生成完成！已自動載入至檢視器。")
            if last_filename:
                self.after(500, lambda: self._auto_jump_to_viewer(last_filename))
        except Exception as e:
            self.after(0, lambda: self._log(f"❌ 生成失敗: {e}"))
            logging.error("寫入檔案失敗", exc_info=True)
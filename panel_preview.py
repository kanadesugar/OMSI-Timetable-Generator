# panel_preview.py
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

class PreviewPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        raw_head = tk.Frame(self)
        raw_head.pack(fill="x")
        tk.Label(raw_head, text="TTL 內容預覽 (支援區塊編輯)", font=("Arial", 12)).pack(side="left")
        
        raw_body = tk.Frame(self)
        raw_body.pack(fill="both", expand=True)
        
        self.text_area = scrolledtext.ScrolledText(raw_body, font=("Consolas", 10), wrap="none", undo=True)
        self.text_area.pack(side="left", fill="both", expand=True)
        
        r_btns = tk.Frame(raw_body)
        r_btns.pack(side="right", fill="y", padx=5)
        
        arr_f2 = tk.Frame(r_btns)
        arr_f2.pack(fill="x", pady=2)
        tk.Button(arr_f2, text="↑", width=3, command=self._move_block_up).pack(side="left", expand=True)
        tk.Button(arr_f2, text="↓", width=3, command=self._move_block_down).pack(side="right", expand=True)
        
        tk.Button(r_btns, text="Add", width=8, command=self._add_trip_block).pack(fill="x", pady=4)
        tk.Button(r_btns, text="Remove", width=8, command=self._remove_trip_block).pack(fill="x", pady=4)
        tk.Button(r_btns, text="Change", width=8, command=self._change_trip_block).pack(fill="x", pady=4)

    def update_content(self, text_content):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text_content)
        self.text_area.edit_reset()

    def _get_block_start_line(self):
        cursor_line = int(self.text_area.index(tk.INSERT).split('.')[0])
        for i in range(cursor_line, max(0, cursor_line - 5), -1):
            if "Dep.:" in self.text_area.get(f"{i}.0", f"{i}.end"):
                if "[addtrip]" in self.text_area.get(f"{i+1}.0", f"{i+1}.end"):
                    return i
        return -1

    def _move_block_up(self):
        start_line = self._get_block_start_line()
        if start_line == -1: return
        
        prev_start = -1
        for i in range(start_line - 1, 0, -1):
            if "Dep.:" in self.text_area.get(f"{i}.0", f"{i}.end") and "[addtrip]" in self.text_area.get(f"{i+1}.0", f"{i+1}.end"):
                prev_start = i
                break
                
        if prev_start != -1:
            current_block = self.text_area.get(f"{start_line}.0", f"{start_line+5}.0")
            self.text_area.delete(f"{start_line}.0", f"{start_line+5}.0")
            self.text_area.insert(f"{prev_start}.0", current_block)
            self.text_area.mark_set("insert", f"{prev_start}.0")
            self.text_area.see("insert")

    def _move_block_down(self):
        start_line = self._get_block_start_line()
        if start_line == -1: return
        
        next_start = -1
        last_line = int(self.text_area.index(tk.END).split('.')[0])
        for i in range(start_line + 5, last_line):
            if "Dep.:" in self.text_area.get(f"{i}.0", f"{i}.end") and "[addtrip]" in self.text_area.get(f"{i+1}.0", f"{i+1}.end"):
                next_start = i
                break
                
        if next_start != -1:
            current_block = self.text_area.get(f"{start_line}.0", f"{start_line+5}.0")
            self.text_area.delete(f"{start_line}.0", f"{start_line+5}.0")
            self.text_area.insert(f"{next_start}.0", current_block)
            self.text_area.mark_set("insert", f"{next_start}.0")
            self.text_area.see("insert")

    def _add_trip_block(self):
        time_str = simpledialog.askstring("新增行程", "輸入發車時間 (HH:MM):", parent=self)
        if not time_str: return
        trip_code = simpledialog.askstring("新增行程", "輸入行程代碼 (Trip Code):", parent=self)
        if not trip_code: return

        try:
            hr, mn = map(int, time_str.split(":"))
            total_mins = hr * 60 + mn
            block = f"  Dep.: {hr}:{mn}:0\n[addtrip]\n{trip_code.strip()}\n0\n{total_mins}.000\n"
            self.text_area.insert(tk.INSERT, block)
        except Exception:
            messagebox.showerror("錯誤", "時間格式錯誤 (HH:MM)")

    def _remove_trip_block(self):
        start_line = self._get_block_start_line()
        if start_line != -1:
            self.text_area.delete(f"{start_line}.0", f"{start_line+5}.0")
        else:
            messagebox.showwarning("警告", "請將游標置於 [addtrip] 區塊內。")

    def _change_trip_block(self):
        start_line = self._get_block_start_line()
        if start_line == -1:
            messagebox.showwarning("警告", "請將游標置於 [addtrip] 區塊內。")
            return
            
        dep_line = self.text_area.get(f"{start_line}.0", f"{start_line}.end")
        old_code = self.text_area.get(f"{start_line+2}.0", f"{start_line+2}.end").strip()
        
        try:
            time_parts = dep_line.split("Dep.:")[1].strip().split(":")
            old_time = f"{int(time_parts[0]):02d}:{int(time_parts[1]):02d}"
        except:
            old_time = ""

        new_time = simpledialog.askstring("修改行程", "修改發車時間 (HH:MM):", initialvalue=old_time, parent=self)
        if new_time is None: return
        new_code = simpledialog.askstring("修改行程", "修改代碼:", initialvalue=old_code, parent=self)
        if new_code is None: return

        try:
            hr, mn = map(int, new_time.split(":"))
            total_mins = hr * 60 + mn
            block = f"  Dep.: {hr}:{mn}:0\n[addtrip]\n{new_code.strip()}\n0\n{total_mins}.000\n"
            
            self.text_area.delete(f"{start_line}.0", f"{start_line+5}.0")
            self.text_area.insert(f"{start_line}.0", block)
        except Exception:
            messagebox.showerror("錯誤", "時間格式錯誤 (HH:MM)")
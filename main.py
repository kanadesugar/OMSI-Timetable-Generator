import sys
import os
import logging
import platform
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# 匯入所有的 UI 頁面模組
from ui_views import MainPage, ManualPage, AutoPage
from ttl_viewer import TTLViewerPage
from page_timeline import TimelineViewerPage

SYSTEM_OS = platform.system()

# 啟用高解析度支援 (Windows)
if SYSTEM_OS == "Windows":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# 設定日誌記錄
log_filename = f"OMSI_Log_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("❌ 系統發生未預期錯誤:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

class OMSIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OMSI タイムテーブル総合生成・閲覧システム")
        self.geometry("900x750")
        
        # 設定跨平台 UI 風格與字型
        style = ttk.Style(self)
        if SYSTEM_OS == "Windows":
            style.theme_use('vista')
            default_font = ("Microsoft JhengHei", 10)
        elif SYSTEM_OS == "Darwin":
            style.theme_use('aqua')
            default_font = ("PingFang TC", 12)
        else:
            style.theme_use('clam')
            default_font = ("Noto Sans CJK TC", 10)
            
        style.configure('.', font=default_font)

        # 容器視窗配置
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        # 註冊所有分頁
        for PageClass in (MainPage, ManualPage, AutoPage, TTLViewerPage, TimelineViewerPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        # 預設顯示主控台
        self.show_frame("MainPage")
        logging.info(f"=== OMSI タイムテーブルシステム起動 ({SYSTEM_OS}) ===")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = OMSIApp()
    app.mainloop()
    logging.info("=== システム正常終了 ===\n")
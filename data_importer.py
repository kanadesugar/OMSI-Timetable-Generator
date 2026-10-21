# data_importer.py
import re
import requests
import pandas as pd

def fetch_wiki_timetable(page_title, log_callback):
    api_url = "https://hkbus.fandom.com/api.php"
    params = {
        "action": "query", "prop": "revisions", "titles": page_title,
        "rvprop": "content", "rvslots": "main", "format": "json"
    }
    headers = {'User-Agent': 'OMSITimetableGenerator/1.0 (Python)'}
    
    log_callback(f"正在連接並讀取 API: {page_title} ...")
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            log_callback(f"❌ 讀取失敗 HTTP 狀態碼: {response.status_code}")
            return None
    except Exception as e:
        log_callback(f"❌ 網路連線錯誤: {e}")
        return None
        
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    page_id = list(pages.keys())[0]
    
    if page_id == "-1":
        log_callback("❌ 找不到 Wiki 頁面。")
        return None
        
    wikitext = pages[page_id]["revisions"][0]["slots"]["main"]["*"]
    
    timetable = {'Weekday_Dir1': [], 'Weekday_Dir2': [], 'Saturday_Dir1': [], 'Saturday_Dir2': [], 'Sunday_Dir1': [], 'Sunday_Dir2': []}
    current_dir = 0
    current_day = None
    
    for line in wikitext.split('\n'):
        line = line.strip()
        if '由' in line and '開出' in line and '!' in line:
            current_dir += 1
            if current_dir > 2: break
            
        if '星期一至五' in line: current_day = 'Weekday'
        elif '星期六' in line: current_day = 'Saturday'
        elif '星期日' in line: current_day = 'Sunday'
            
        match = re.match(r'^\|\s*(\d{2}(?:\s*-\s*\d{2})?)\s*\|\|(.*)', line)
        if match and current_dir in [1, 2] and current_day:
            hour_part = match.group(1).strip()
            min_part = match.group(2).strip()
            
            hours = []
            if '-' in hour_part:
                start_hr, end_hr = map(int, [x.strip() for x in hour_part.split('-')])
                hours = list(range(start_hr, end_hr + 1))
            else:
                hours = [int(hour_part)]
                
            min_part_clean = re.sub(r"\{\{FC\|[^|]+\|([^}]+)\}\}", r"\1", min_part)
            min_matches = re.findall(r"(\d{2})\s*([＊＃*#]?)", min_part_clean)
            
            for h in hours:
                for m_str, sym in min_matches:
                    timetable[f"{current_day}_Dir{current_dir}"].append(f"{h:02d}:{m_str}{sym}")
    return timetable

def parse_multi_route_excel(filepath):
    df = pd.read_excel(filepath, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    
    required_cols = {'Route', 'Day_Type', 'Dep_Time', 'Trip_Code'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Excel 欄位不足。必須欄位: {required_cols}")

    has_tour_id = 'Tour_ID' in df.columns
    if has_tour_id:
        df = df.dropna(subset=['Route', 'Day_Type', 'Dep_Time', 'Trip_Code', 'Tour_ID'])
    else:
        df = df.dropna(subset=['Route', 'Day_Type', 'Dep_Time', 'Trip_Code'])
        
    return df, has_tour_id
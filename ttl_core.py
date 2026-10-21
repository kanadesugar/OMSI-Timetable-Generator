import pandas as pd
from datetime import datetime

MAX_TOURS = 8

def generate_trip_entry(time_str, default_dir_code, special_dict):
    trip_code = default_dir_code
    clean_time = str(time_str).strip()
    
    for symbol, special_code in special_dict.items():
        if symbol and symbol in clean_time:
            trip_code = special_code
            clean_time = clean_time.replace(symbol, "").strip()
            break
            
    try:
        hr, mn = map(int, clean_time.split(":"))
        total_mins = hr * 60 + mn
        return f"  Dep.: {hr}:{mn}:0\n[addtrip]\n{trip_code}\n0\n{total_mins}.000\n\n"
    except Exception:
        return ""

def build_ttl_content(route_name, ai_group, specials, dir1_code, dir1_times, dir2_code, dir2_times, max_tours=8):
    clean_dir1 = [t for t in dir1_times if pd.notna(t) and str(t).strip() != ""]
    clean_dir2 = [t for t in dir2_times if pd.notna(t) and str(t).strip() != ""]
    
    if not clean_dir1 and not clean_dir2: 
        return None

    route_num = route_name.split()[-1] if " " in route_name else route_name
    all_trips = [(t, dir1_code) for t in clean_dir1] + [(t, dir2_code) for t in clean_dir2]
        
    def get_sort_key(item):
        time_clean = str(item[0])
        for symbol in specials.keys():
            if symbol: time_clean = time_clean.replace(symbol, "")
        return time_clean.strip()
        
    all_trips.sort(key=get_sort_key)
    
    tours_data = {i: [] for i in range(max_tours)}
    for i, (time_str, default_dir) in enumerate(all_trips):
        tours_data[i % max_tours].append((time_str, default_dir))

    today = datetime.now().strftime("%d/%m/%Y")
    lines = [
        "-----------------------", "Time Table Line File", "-----------------------\n",
        "Created by OMSI Generator", f"Date: {today}\n", "[userallowed]\n", "[priority]\n1",
        "------------------------------------\n"
    ]
    
    actual_ai = ai_group if ai_group else route_name

    for i in range(max_tours):
        if not tours_data[i]: 
            continue
        tour_id = f"{route_num}-{i+1:03d}"
        lines.append(f"[newtour]\n{tour_id}\n{actual_ai}\n1023\n")
        lines.append("------------------------------------\n")
        for time_str, default_dir in tours_data[i]:
            entry = generate_trip_entry(time_str, default_dir, specials)
            if entry: lines.append(entry)
        lines.append("------------------------------------\n")
        
    return "\n".join(lines)

def save_ttl_file(filename, content, log_callback):
    if not content: 
        return
    with open(filename, "w", encoding="utf-8", errors="ignore") as f:
        f.write(content)
    log_callback(f"✅ 生成成功: {filename}")
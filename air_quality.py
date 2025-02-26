import requests
import json
import pandas as pd
import os
from datetime import datetime

# 當前時間，用於檔案命名
current_time = datetime.now().strftime("%Y%m%d_%H%M")

# API 請求
url = "https://airtw.moenv.gov.tw/AJAX_MinChart.aspx?Target=IOT_Chart&siteid=2&Hour=1&_=1740531463588"
response = requests.get(url)
data = response.json()

# 解析數據
dates = data[0]["DATA_DATE"]

# 初始化數據字典
air_data = {"timestamp": dates}

# 解析各項污染物數據
for item in data[1]["Line"]:
    item_name = item["Item"].split("(")[0].strip()
    item_value = item["ItemValue"].replace("NULL", "null")
    item_values = json.loads(item_value)
    air_data[item_name] = item_values

# 轉換為 DataFrame
df = pd.DataFrame(air_data)

# 建立資料夾（如果不存在）
os.makedirs("air_quality_data", exist_ok=True)

# 保存當前數據
current_file = f"air_quality_data/{current_time}.csv"
df.to_csv(current_file, index=False)
print(f"Saved current data to {current_file}")

# 彙總已有的所有數據
all_files = [f for f in os.listdir("air_quality_data") if f.endswith(".csv")]
all_data = []

for file in all_files:
    file_path = os.path.join("air_quality_data", file)
    file_df = pd.read_csv(file_path)
    
    # 從檔名提取日期時間作為識別符
    file_datetime = file.split(".")[0]
    file_df["collection_time"] = file_datetime
    
    all_data.append(file_df)

# 合併所有數據
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.to_csv("air_quality_combined.csv", index=False)
    print("Updated combined data file")

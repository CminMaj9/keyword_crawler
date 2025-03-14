import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import openpyxl
from openpyxl.styles import Alignment

# 连接 MySQL 数据库
db_config = {
    'host': '47.251.73.120',
    'user': 'joker',
    'password': 'Iamajoker666!',
    'database': 'keyword_db'
}
engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

# Excel 文件路径
excel_path = "keyword_data_filtered.xlsx"

# 1. **查询 MySQL 获取最新数据**
query = "SELECT date, keyword, monthpv FROM keyword_data;"
df = pd.read_sql(query, engine)

# 2. **透视数据，使 keyword 变为列名，仅保留 monthpv**
df_pivot = df.pivot(index="date", columns="keyword", values="monthpv")
df_pivot.reset_index(inplace=True)

# 3. **检查 Excel 是否存在**
if os.path.exists(excel_path):
    # **如果存在，则读取原始 Excel**
    df_existing = pd.read_excel(excel_path)

    # **合并数据，去重**
    df_combined = pd.concat([df_existing, df_pivot], ignore_index=True)
    df_combined.drop_duplicates(subset=["date"], keep="last", inplace=True)  # 避免重复数据
else:
    # **如果 Excel 不存在，直接使用新数据**
    df_combined = df_pivot

# 4. **导出数据到 Excel**
df_combined.to_excel(excel_path, index=False)

# 5. **使用 openpyxl 自动调整列宽并居中对齐内容**
wb = openpyxl.load_workbook(excel_path)
ws = wb.active

# 遍历所有列，调整宽度并居中对齐
for col in ws.columns:
    max_length = 0
    column = col[0].column_letter  # 获取列字母
    for cell in col:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(cell.value)
            # 设置单元格内容居中
            cell.alignment = Alignment(horizontal='center', vertical='center')
        except:
            pass
    adjusted_width = (max_length + 16)  # 增加一些空间
    ws.column_dimensions[column].width = adjusted_width

# 保存调整后的 Excel 文件
wb.save(excel_path)

print(f"Excel 文件已更新并且列宽已自动调整，内容已居中：{excel_path}")

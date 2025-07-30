import pandas as pd

# Đọc hai file Parquet
df1 = pd.read_parquet(r"C:\Users\Administrator\Documents\Search_engine\data\train-00000-of-00002.parquet")
df2 = pd.read_parquet(r"C:\Users\Administrator\Documents\Search_engine\data\train-00001-of-00002.parquet")

# Gộp hai DataFrame
df_combined = pd.concat([df1, df2], ignore_index=True)

# Ghi lại thành file mới
df_combined.to_parquet(r"C:\Users\Administrator\Documents\Search_engine\data\text_data.parquet")

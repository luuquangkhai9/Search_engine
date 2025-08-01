import pandas as pd

df1 = pd.read_parquet(r"C:\Users\Administrator\Documents\Search_engine\data\train-00000-of-00002.parquet")
df2 = pd.read_parquet(r"C:\Users\Administrator\Documents\Search_engine\data\train-00001-of-00002.parquet")

df_combined = pd.concat([df1, df2], ignore_index=True)

df_combined.to_parquet(r"C:\Users\Administrator\Documents\Search_engine\data\text_data.parquet")

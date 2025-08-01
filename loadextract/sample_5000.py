import pandas as pd

df = pd.read_parquet('data/train-00000-of-00002.parquet')

sample_df = df.head(10000)

sample_df.to_parquet('data/sample_10000.parquet', index=False)

print("Đã lưu 10000 văn bản vào sample_10000.parquet")

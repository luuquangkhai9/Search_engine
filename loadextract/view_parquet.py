import pandas as pd

file_path =r'C:\Users\Administrator\Documents\Search_engine\data\train-00000-of-00002.parquet'

try:
    df = pd.read_parquet(file_path)

    print("--- 5 DÒNG ĐẦU TIÊN ---")
    print(df.head())

    print("\n--- THÔNG TIN DỮ LIỆU ---")
    df.info()

except Exception as e:
    print(f"Đã có lỗi xảy ra: {e}")
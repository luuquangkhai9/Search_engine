import pandas as pd

# Thay đổi đường dẫn đến file parquet của bạn
file_path =r'C:\Users\Administrator\Documents\Search_engine\data\train-00000-of-00002.parquet'

try:
    # Đọc file parquet
    df = pd.read_parquet(file_path)

    # In ra 5 dòng đầu tiên để xem
    print("--- 5 DÒNG ĐẦU TIÊN ---")
    print(df.head())

    # In ra thông tin về các cột và kiểu dữ liệu
    print("\n--- THÔNG TIN DỮ LIỆU ---")
    df.info()

except Exception as e:
    print(f"Đã có lỗi xảy ra: {e}")
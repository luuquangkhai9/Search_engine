import pandas as pd

# Đọc file parquet gốc (không cần load toàn bộ nếu file quá lớn)
df = pd.read_parquet('data/train-00000-of-00002.parquet')

# Lấy 5000 dòng đầu tiên (hoặc bạn có thể dùng random nếu muốn)
sample_df = df.head(10000)

# Ghi ra file mới
sample_df.to_parquet('data/sample_10000.parquet', index=False)

print("Đã lưu 10000 văn bản vào sample_10000.parquet")

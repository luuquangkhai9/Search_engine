import os

input_file = r"C:\Users\Administrator\Documents\Search_engine\part_1.csv"
output_dir = r"C:\Users\Administrator\Documents\Search_engine"
num_parts = 5

# Tạo thư mục xuất nếu chưa có
os.makedirs(output_dir, exist_ok=True)

# Đếm tổng số dòng (trừ dòng header)
with open(input_file, 'r', encoding='utf-8') as f:
    total_lines = sum(1 for _ in f) - 1  # trừ dòng tiêu đề

lines_per_file = total_lines // num_parts
extra_lines = total_lines % num_parts

# Tách file
with open(input_file, 'r', encoding='utf-8') as f:
    header = f.readline()
    for i in range(num_parts):
        part_lines = lines_per_file + (1 if i < extra_lines else 0)
        part_path = os.path.join(output_dir, f"part_{i+1}.csv")
        with open(part_path, 'w', encoding='utf-8') as out:
            out.write(header)  # ghi dòng tiêu đề
            for _ in range(part_lines):
                line = f.readline()
                if not line:
                    break
                out.write(line)

print(f"Đã chia file CSV thành {num_parts} phần tại: {output_dir}")

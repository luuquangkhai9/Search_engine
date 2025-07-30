import pandas as pd
import psycopg2
import sys

# --- THÔNG TIN KẾT NỐI DATABASE ---
DB_NAME = "searchdb"
DB_USER = "myuser"
DB_PASS = "mysecretpassword"
DB_HOST = "localhost"
DB_PORT = "5432"

def migrate_data():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        print("Kết nối database thành công!")

        # Tạo bảng nếu chưa tồn tại
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id VARCHAR(255) PRIMARY KEY,
                doc_id VARCHAR(255),
                content TEXT
            );
        """)
        conn.commit()
        print("Bảng 'chunks' đã sẵn sàng.")
        
        # --- MỚI: Xóa toàn bộ dữ liệu cũ trong bảng ---
        print("Đang xóa dữ liệu cũ...")
        cur.execute("TRUNCATE TABLE chunks;")
        conn.commit()
        print("Đã xóa dữ liệu cũ thành công.")
        # ---------------------------------------------

        # Đọc dữ liệu từ file CSV
        df = pd.read_csv('data/chunked_articles.csv')
        print(f"Đang di chuyển {len(df)} chunks mới vào database...")

        # Insert từng dòng vào database
        for index, row in df.iterrows():
            # Không cần ON CONFLICT nữa vì bảng đã trống
            cur.execute(
                "INSERT INTO chunks (chunk_id, doc_id, content) VALUES (%s, %s, %s);",
                (row['chunk_id'], row['doc_id'], row['content'])
            )
        
        conn.commit()
        cur.close()
        conn.close()
        print("Di chuyển dữ liệu hoàn tất!")

    except psycopg2.OperationalError as e:
        print(f"Lỗi kết nối: Không thể kết nối đến server PostgreSQL.", file=sys.stderr)
        print("Vui lòng đảm bảo container Docker 'search_db' đang chạy.", file=sys.stderr)
    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}", file=sys.stderr)

if __name__ == "__main__":
    migrate_data()
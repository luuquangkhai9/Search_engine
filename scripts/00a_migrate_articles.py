import pandas as pd
import psycopg2
import sys

# --- THÔNG TIN KẾT NỐI DATABASE ---
DB_NAME = "searchdb"
DB_USER = "myuser"
DB_PASS = "mysecretpassword"
DB_HOST = "localhost"
DB_PORT = "5432"

def migrate_original_articles():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        print("Kết nối database thành công!")

        # Tạo bảng articles nếu chưa tồn tại
        cur.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                doc_id VARCHAR(255) PRIMARY KEY,
                full_content TEXT
            );
        """)
        conn.commit()
        print("Bảng 'articles' đã sẵn sàng.")

        # Đọc dữ liệu từ file articles.csv gốc
        df = pd.read_csv('data/articles.csv')
        print(f"Đang di chuyển {len(df)} bài viết gốc vào database...")

        # Insert từng dòng vào database
        for index, row in df.iterrows():
            # Đảm bảo doc_id là string để khớp với kiểu dữ liệu VARCHAR
            doc_id_str = str(row['id'])
            cur.execute(
                "INSERT INTO articles (doc_id, full_content) VALUES (%s, %s) ON CONFLICT (doc_id) DO UPDATE SET full_content = EXCLUDED.full_content;",
                (doc_id_str, row['content'])
            )
        
        conn.commit()
        cur.close()
        conn.close()
        print("Di chuyển dữ liệu gốc hoàn tất!")

    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}", file=sys.stderr)

if __name__ == "__main__":
    migrate_original_articles()
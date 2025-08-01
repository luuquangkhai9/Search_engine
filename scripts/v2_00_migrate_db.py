import pandas as pd
import psycopg2
import sys

# --- THÔNG TIN KẾT NỐI DATABASE V2 ---
DB_NAME = "searchdb_v2"
DB_USER = "myuser_v2"
DB_PASS = "mysecretpassword_v2"
DB_HOST = "localhost"
DB_PORT = "5433" # Cổng mới

PARQUET_FILE_PATH = r'C:\Users\Administrator\Documents\Search_engine\data\sample_50000.parquet'
CHUNKED_CSV_PATH = 'data/chunked_50000_v2.csv'

def migrate_v2():
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()
        print("Kết nối database v2 thành công!")

        # 1. Xử lý bảng articles (văn bản gốc)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                doc_id VARCHAR(255) PRIMARY KEY,
                full_content TEXT,
                domain VARCHAR(255)
            );
        """)
        cur.execute("TRUNCATE TABLE articles;") # Xóa dữ liệu cũ
        df_articles = pd.read_parquet(PARQUET_FILE_PATH)
        for _, row in df_articles.iterrows():
            cur.execute(
                "INSERT INTO articles (doc_id, full_content, domain) VALUES (%s, %s, %s);",
                (row['id'], row['text'], row['domain'])
            )
        print(f"Đã di chuyển {len(df_articles)} bài viết gốc vào bảng 'articles'.")

        # 2. Xử lý bảng chunks
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id VARCHAR(255) PRIMARY KEY,
                doc_id VARCHAR(255),
                content TEXT,
                domain VARCHAR(255)
            );
        """)
        cur.execute("TRUNCATE TABLE chunks;") # Xóa dữ liệu cũ
        df_chunks = pd.read_csv(CHUNKED_CSV_PATH)
        for _, row in df_chunks.iterrows():
            cur.execute(
                "INSERT INTO chunks (chunk_id, doc_id, content, domain) VALUES (%s, %s, %s, %s);",
                (row['chunk_id'], row['doc_id'], row['content'], row['domain'])
            )
        print(f"Đã di chuyển {len(df_chunks)} chunks vào bảng 'chunks'.")

        conn.commit()
        cur.close()
        conn.close()
        print("Di chuyển dữ liệu cho v2 hoàn tất!")

    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}", file=sys.stderr)

if __name__ == "__main__":
    migrate_v2()
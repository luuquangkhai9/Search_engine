import psycopg2
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm
import os

# --- THÔNG TIN KẾT NỐI ---
DB_NAME = "searchdb_v2"
DB_USER = "myuser_v2"
DB_PASS = "mysecretpassword_v2"
DB_HOST = "localhost"
DB_PORT = "5433"

ES_INDEX_NAME = "articles_v2"
# ES_PASSWORD = "0u+EFI2EsqiCKHwZs_Ap" 
os.environ['no_proxy'] = 'localhost,127.0.0.1'

def create_es_index(es_client):
    """Tạo index và mapping cho Elasticsearch."""
    if es_client.indices.exists(index=ES_INDEX_NAME):
        print(f"Index '{ES_INDEX_NAME}' đã tồn tại. Xóa index cũ...")
        es_client.indices.delete(index=ES_INDEX_NAME)
    
    mapping = {
        "properties": {
            "doc_id": {"type": "keyword"},
            "chunk_id": {"type": "keyword"},
            "content": {"type": "text"},
            "domain": {"type": "keyword"}
        }
    }
    es_client.indices.create(index=ES_INDEX_NAME, mappings=mapping)
    print(f"Đã tạo index '{ES_INDEX_NAME}' thành công.")

def index_data_to_es():
    """Đọc dữ liệu từ DB và index vào Elasticsearch."""
    # Kết nối DB
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    df = pd.read_sql_query("SELECT chunk_id, doc_id, content, domain FROM chunks", conn)
    conn.close()
    print(f"Đã đọc {len(df)} chunks từ PostgreSQL.")
    
    # THAY ĐỔI: Kết nối đến Elasticsearch với HTTPS
    # es = Elasticsearch(
    #     "https://localhost:9200",
    #     basic_auth=("elastic", ES_PASSWORD),
    #     ca_certs="./http_ca.crt" # Đường dẫn đến file chứng chỉ
    # )
    es = Elasticsearch("http://localhost:9200")  # Sử dụng HTTP nếu không có chứng chỉ
    print("Kết nối đến Elasticsearch thành công!")

    create_es_index(es)
    
    # Chuẩn bị dữ liệu và index
    actions = [
        {
            "_index": ES_INDEX_NAME,
            "_id": row['chunk_id'],
            "_source": {
                "chunk_id": row['chunk_id'],
                "doc_id": row['doc_id'],
                "content": row['content'],
                "domain": row['domain']
            }
        }
        for _, row in df.iterrows()
    ]
    
    print("Bắt đầu index dữ liệu vào Elasticsearch...")
    success, _ = bulk(es, actions, raise_on_error=True)
    print(f"Đã index thành công {success} văn bản vào Elasticsearch.")

if __name__ == "__main__":
    index_data_to_es()
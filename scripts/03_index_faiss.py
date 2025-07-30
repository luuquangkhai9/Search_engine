import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import psycopg2

# Thông tin kết nối database
DB_NAME = "searchdb"
DB_USER = "myuser"
DB_PASS = "mysecretpassword"
DB_HOST = "localhost"
DB_PORT = "5432"

MODEL_NAME = 'AITeamVN/Vietnamese_Embedding_v2' 

def create_faiss_index():
    # 1. Tải model
    print("Đang tải model embedding...")
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Đọc dữ liệu từ PostgreSQL
    print("Đang đọc dữ liệu từ PostgreSQL...")
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()
    cur.execute("SELECT chunk_id, content FROM chunks;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    chunk_ids = [row[0] for row in rows]
    texts = [row[1] for row in rows]
    print(f"Đã đọc {len(texts)} chunks.")
    
    # 3. Tạo embeddings
    print("Đang tạo embeddings... (có thể mất thời gian)")
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    embeddings = embeddings.cpu().numpy().astype('float32')
    
    # 4. Xây dựng FAISS index
    d = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(d, 32)
    print("Đang xây dựng index HNSW...")
    index.add(embeddings)
    
    # 5. Lưu index và mapping
    print("Đang lưu index và mapping...")
    faiss.write_index(index, 'models/faiss.index')
    with open('models/id_mapping.pkl', 'wb') as f:
        pickle.dump(chunk_ids, f)
        
    print(f"Đã tạo và lưu FAISS index (HNSW) với {index.ntotal} vectors.")

if __name__ == "__main__":
    create_faiss_index()
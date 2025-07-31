import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import psycopg2
import pandas as pd

DB_NAME = "searchdb_v2"
DB_USER = "myuser_v2"
DB_PASS = "mysecretpassword_v2"
DB_HOST = "localhost"
DB_PORT = "5433"

MODEL_NAME = 'keepitreal/vietnamese-sbert' # Tên mô hình mới

def create_faiss_index_v2():
    print(f"Đang tải model embedding: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    d = model.get_sentence_embedding_dimension()
    print(f"Số chiều vector của mô hình: {d}") # Sẽ in ra 768

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    df = pd.read_sql_query("SELECT chunk_id, content FROM chunks", conn)
    conn.close()
    
    chunk_ids = df['chunk_id'].tolist()
    texts = df['content'].tolist()
    print(f"Đã đọc {len(texts)} chunks.")
    
    print("Đang tạo embeddings...")
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=True, batch_size=32)
    embeddings = embeddings.cpu().numpy().astype('float32')
    
    # Dùng L2 distance mặc định, phù hợp cho Cosine Similarity
    index = faiss.IndexHNSWFlat(d, 32) 
    print("Đang xây dựng index HNSW...")
    index.add(embeddings)
    
    print("Đang lưu index và mapping cho v2...")
    faiss.write_index(index, 'models/faiss_v2.index')
    with open('models/id_mapping_v2.pkl', 'wb') as f:
        pickle.dump(chunk_ids, f)
        
    print(f"Đã tạo và lưu FAISS index v2 với {index.ntotal} vectors.")

if __name__ == "__main__":
    create_faiss_index_v2()
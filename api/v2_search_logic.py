import os
import faiss
import pickle
import torch
from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2 import pool 
from elasticsearch import Elasticsearch

# --- THÔNG TIN KẾT NỐI DATABASE V2 ---
DB_NAME = "searchdb_v2"
DB_USER = "myuser_v2"
DB_PASS = "mysecretpassword_v2"
DB_HOST = "localhost"
DB_PORT = "5433"

# --- KHỞI TẠO ---
os.environ['no_proxy'] = 'localhost,127.0.0.1'
print("API (v2) is starting, loading models...")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

#bản 2 dùng mô hình nhẹ hơn để phù hợp cấu hình :((
EMBEDDING_MODEL = SentenceTransformer('keepitreal/vietnamese-sbert', device=DEVICE) 
FAISS_INDEX = faiss.read_index('models/faiss_v2.index')
with open('models/id_mapping_v2.pkl', 'rb') as f:
    ID_MAPPING = pickle.load(f)

ES = Elasticsearch("http://localhost:9200")
ES_INDEX_NAME = "articles_v2"

db_pool = psycopg2.pool.SimpleConnectionPool(1, 10,
                                             dbname=DB_NAME,
                                             user=DB_USER,
                                             password=DB_PASS,
                                             host=DB_HOST,
                                             port=DB_PORT)

print("Models and data loaded successfully!")

# --- HÀM LOGIC ---

def search_faiss(query, top_k=50):
    query_vector = EMBEDDING_MODEL.encode([query], convert_to_numpy=True)
    distances, indices = FAISS_INDEX.search(query_vector, top_k)
    return [ID_MAPPING[i] for i in indices[0]]

def search_es(query, top_k=50):
    response = ES.search(
        index=ES_INDEX_NAME,
        query={"match": {"content": query}},
        size=top_k
    )
    return [hit['_id'] for hit in response['hits']['hits']]

def reciprocal_rank_fusion(results_lists, k=60):
    scores = {}
    for results in results_lists:
        for rank, doc_id in enumerate(results):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank + 1)
    return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

# Sử dụng connection pool
def get_content_by_ids(chunk_ids: list[str]):
    if not chunk_ids: return []
    conn = db_pool.getconn() # Lấy kết nối từ pool
    try:
        with conn.cursor() as cur:
            query = "SELECT chunk_id, doc_id, content FROM chunks WHERE chunk_id = ANY(%s);"
            cur.execute(query, (chunk_ids,))
            rows = cur.fetchall()
            content_map = {row[0]: {"doc_id": row[1], "content": row[2]} for row in rows}
            results = []
            for chunk_id in chunk_ids:
                if chunk_id in content_map:
                    results.append({
                        "id": chunk_id,
                        "doc_id": content_map[chunk_id]["doc_id"],
                        "content": content_map[chunk_id]["content"]
                    })
    finally:
        db_pool.putconn(conn) # Trả kết nối về pool
    return results

# Sử dụng connection pool
def get_full_article_by_doc_id(doc_id: str):
    conn = db_pool.getconn() # Lấy kết nối từ pool
    try:
        with conn.cursor() as cur:
            query = "SELECT full_content FROM articles WHERE doc_id = %s;"
            cur.execute(query, (doc_id,))
            row = cur.fetchone()
    finally:
        db_pool.putconn(conn) # Trả kết nối về pool
    return row[0] if row else None
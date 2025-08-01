import os
import faiss
import pickle
import torch
from sentence_transformers import SentenceTransformer
import psycopg2

# --- THÔNG TIN KẾT NỐI DATABASE ---
DB_NAME = "searchdb"
DB_USER = "myuser"
DB_PASS = "mysecretpassword"
DB_HOST = "localhost"
DB_PORT = "5432"

# --- KHỞI TẠO ---
os.environ['no_proxy'] = 'localhost,127.0.0.1'
print("API (v1) is starting, loading models...")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# Tải mô hình embedding và index FAISS
EMBEDDING_MODEL = SentenceTransformer('AITeamVN/Vietnamese_Embedding_v2', device=DEVICE)
FAISS_INDEX = faiss.read_index('models/faiss.index')
with open('models/id_mapping.pkl', 'rb') as f:
    ID_MAPPING = pickle.load(f)

print("Models loaded successfully!")

# --- HÀM LOGIC ---
def search_faiss(query, top_k=50):
    """Tìm kiếm trên FAISS và trả về danh sách ID."""
    query_vector = EMBEDDING_MODEL.encode([query], convert_to_numpy=True)
    distances, indices = FAISS_INDEX.search(query_vector, top_k)
    return [ID_MAPPING[i] for i in indices[0]]

def get_content_by_ids(chunk_ids: list[str]):
    """Lấy nội dung từ PostgreSQL bằng các chunk_id."""
    if not chunk_ids:
        return []

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()
    
    query = "SELECT chunk_id, content FROM chunks WHERE chunk_id = ANY(%s);"
    cur.execute(query, (chunk_ids,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Tạo một dict để truy xuất nhanh và giữ đúng thứ tự
    content_map = {row[0]: row[1] for row in rows}
    
    # Sắp xếp kết quả theo đúng thứ tự của chunk_ids đầu vào
    results = [{"id": chunk_id, "content": content_map.get(chunk_id)} for chunk_id in chunk_ids]
    
    return results

def get_full_article_by_doc_id(doc_id: str):
    """Lấy toàn bộ nội dung của một văn bản gốc từ doc_id."""
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()
    
    query = "SELECT full_content FROM articles WHERE doc_id = %s;"
    cur.execute(query, (doc_id,))
    row = cur.fetchone() 
    
    cur.close()
    conn.close()
    
    if row:
        return row[0] # Trả về nội dung
    return None # Hoặc trả về thông báo lỗi
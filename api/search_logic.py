import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModelForSequenceClassification # Dùng cho Re-ranker

# --- KHỞI TẠO CÁC THÀNH PHẦN KHI START APP ---

# 1. Tải các mô hình và index
print("API is starting, loading models...")
DEVICE = "cpu" # "cpu" nếu không có GPU

# Model tạo embedding cho truy vấn
EMBEDDING_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=DEVICE)

# Mô hình Re-ranker (ví dụ cross-encoder)
# Thay thế bằng ColBERT trong thực tế nếu có đủ tài nguyên
RERANKER_TOKENIZER = AutoTokenizer.from_pretrained('cross-encoder/ms-marco-MiniLM-L-6-v2')
RERANKER_MODEL = AutoModelForSequenceClassification.from_pretrained('cross-encoder/ms-marco-MiniLM-L-6-v2').to(DEVICE)
RERANKER_MODEL.eval()

# Tải FAISS index và mapping
FAISS_INDEX = faiss.read_index('models/faiss.index')
with open('models/id_mapping.pkl', 'rb') as f:
    ID_MAPPING = pickle.load(f)

# Kết nối Elasticsearch
ES = Elasticsearch("http://localhost:9200")
ES_INDEX_NAME = "vietnamese_articles"

print("Models loaded successfully!")

# --- CÁC HÀM LOGIC ---

def search_es(query, top_k=50):
    """Tìm kiếm trên Elasticsearch."""
    response = ES.search(
        index=ES_INDEX_NAME,
        query={"match": {"content": query}},
        size=top_k
    )
    return [hit['_id'] for hit in response['hits']['hits']]

def search_faiss(query, top_k=50):
    """Tìm kiếm trên FAISS."""
    query_vector = EMBEDDING_MODEL.encode([query], convert_to_numpy=True)
    distances, indices = FAISS_INDEX.search(query_vector, top_k)
    return [ID_MAPPING[i] for i in indices[0]]

def reciprocal_rank_fusion(results_lists, k=60):
    """Thực hiện RRF."""
    scores = {}
    for results in results_lists:
        for rank, doc_id in enumerate(results):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank + 1)
    
    return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

def rerank(query, doc_ids):
    """Xếp hạng lại bằng Cross-Encoder (ví dụ cho Re-ranker)."""
    # Lấy nội dung của các docs từ ES
    response = ES.mget(index=ES_INDEX_NAME, ids=doc_ids)
    contents = [hit['_source']['content'] for hit in response['docs']]
    
    # Tạo cặp [query, content]
    pairs = [[query, content] for content in contents]
    
    with torch.no_grad():
        inputs = RERANKER_TOKENIZER(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512).to(DEVICE)
        scores = RERANKER_MODEL(**inputs).logits.squeeze().cpu().numpy()
    
    # Sắp xếp lại doc_ids dựa trên scores
    reranked_docs = [doc for _, doc in sorted(zip(scores, doc_ids), reverse=True)]
    return reranked_docs
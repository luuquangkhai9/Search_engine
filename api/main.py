from fastapi import FastAPI
from pydantic import BaseModel
from . import search_logic

app = FastAPI(title="Hybrid Search API")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

class SuggestRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search")
def search(request: SearchRequest):
    # Giai đoạn 1: Retrieval & Fusion
    es_results = search_logic.search_es(request.query, top_k=50)
    faiss_results = search_logic.search_faiss(request.query, top_k=50)
    
    fused_results = search_logic.reciprocal_rank_fusion([es_results, faiss_results])
    
    # Giai đoạn 2: Re-ranking
    # Chỉ re-rank top 25 ứng viên đầu tiên để tối ưu tốc độ
    candidates = fused_results[:25]
    reranked_results = search_logic.rerank(request.query, candidates)
    
    return {
        "status": "success",
        "results": reranked_results[:request.top_k]
    }

@app.post("/suggest")
def suggest(request: SuggestRequest):
    """API endpoint đơn giản cho autocomplete."""
    # Chỉ dùng Elasticsearch cho tốc độ
    results = search_logic.search_es(request.query, top_k=request.top_k)
    return {
        "status": "success",
        "suggestions": results
    }
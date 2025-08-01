import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from . import v2_search_logic 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Vector Search API (v2)")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

@app.post("/search")
def search(request: SearchRequest):
    start_time = time.time()

    # BƯỚC 1: TRUY VẤN SONG SONG
    es_results = v2_search_logic.search_es(request.query, top_k=50)
    faiss_results = v2_search_logic.search_faiss(request.query, top_k=50)

    # BƯỚC 2: TỔNG HỢP KẾT QUẢ BẰNG RRF
    fused_ids = v2_search_logic.reciprocal_rank_fusion([es_results, faiss_results])

    # Lấy top_k kết quả tốt nhất từ danh sách đã tổng hợp
    top_ids = fused_ids[:request.top_k]
    
    # BƯỚC 3: LẤY NỘI DUNG
    results = v2_search_logic.get_content_by_ids(top_ids)
    
    end_time = time.time()
    duration = end_time - start_time
    
    return {
        "status": "success",
        "duration": duration,
        "results": results
    }

@app.get("/document/{doc_id}")
def get_document(doc_id: str):
    full_content = v2_search_logic.get_full_article_by_doc_id(doc_id)
    if full_content is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"doc_id": doc_id, "content": full_content}
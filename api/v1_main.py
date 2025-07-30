import time # MỚI: Import thư viện time
from fastapi import FastAPI
from pydantic import BaseModel
from . import v1_search_logic
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException


app = FastAPI(title="Simple Vector Search API (v1)")

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
    # --- THAY ĐỔI Ở ĐÂY ---
    # 1. Ghi lại thời gian bắt đầu
    start_time = time.time()
    
    # Logic tìm kiếm
    relevant_ids = v1_search_logic.search_faiss(
        request.query, 
        top_k=request.top_k
    )
    results = v1_search_logic.get_content_by_ids(relevant_ids)
    
    # 2. Ghi lại thời gian kết thúc và tính toán
    end_time = time.time()
    duration = end_time - start_time
    
    # 3. Thêm thời gian vào kết quả trả về
    return {
        "status": "success",
        "duration": duration, # Thêm trường duration
        "results": results
    }

@app.get("/document/{doc_id}")
def get_document(doc_id: str):
    full_content = v1_search_logic.get_full_article_by_doc_id(doc_id)
    if full_content is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"doc_id": doc_id, "content": full_content}
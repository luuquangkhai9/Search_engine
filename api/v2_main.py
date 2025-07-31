import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from . import v2_search_logic # Import logic v2
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
    relevant_ids = v2_search_logic.search_faiss(request.query, top_k=request.top_k)
    results = v2_search_logic.get_content_by_ids(relevant_ids)
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
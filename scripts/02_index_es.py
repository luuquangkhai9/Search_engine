
import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import pandas as pd

os.environ['no_proxy'] = 'localhost,127.0.0.1'

es = Elasticsearch("https://localhost:9200")
INDEX_NAME = "vietnamese_articles"

def create_es_index():
    """Tạo index với mapping phù hợp cho tiếng Việt."""
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print("Index cũ đã được xóa.")

    mapping = {
        "properties": {
            "doc_id": {"type": "keyword"},
            "chunk_id": {"type": "keyword"},
            "content": {
                "type": "text",
                "analyzer": "standard" 
            }
        }
    }

    es.indices.create(index=INDEX_NAME, body={"mappings": mapping})
    print(f"Đã tạo index '{INDEX_NAME}'.")

def index_data():
    """Đọc dữ liệu chunk và đẩy vào Elasticsearch."""
    df = pd.read_csv('data/chunked_articles.csv')
    
    actions = [
        {
            "_index": INDEX_NAME,
            "_id": row['chunk_id'],
            "_source": {
                "doc_id": row['doc_id'],
                "chunk_id": row['chunk_id'],
                "content": row['content']
            }
        }
        for index, row in df.iterrows()
    ]
    
    success, _ = bulk(es, actions)
    print(f"Đã index thành công {success} văn bản.")

if __name__ == "__main__":
    create_es_index()
    index_data()
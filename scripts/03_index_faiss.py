import faiss
import numpy as np
import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer

# Model để tạo embedding
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2' 
# (Lưu ý: nên dùng model tốt hơn cho tiếng Việt như VoVanPhuc/sup-SimCSE-VietNamese-phobert-base)

def create_faiss_index():
    # 1. Tải model
    print("Đang tải model embedding...")
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Đọc dữ liệu
    df = pd.read_csv('data/chunked_articles.csv')
    texts = df['content'].tolist()
    chunk_ids = df['chunk_id'].tolist()
    
    # 3. Tạo embeddings
    print("Đang tạo embeddings... (có thể mất thời gian)")
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    embeddings = embeddings.cpu().numpy()
    
    # 4. Xây dựng FAISS index
    d = embeddings.shape[1]  # Chiều của vector
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    
    # 5. Lưu index và mapping
    faiss.write_index(index, 'models/faiss.index')
    with open('models/id_mapping.pkl', 'wb') as f:
        pickle.dump(chunk_ids, f)
        
    print(f"Đã tạo và lưu FAISS index với {index.ntotal} vectors.")
    print("Đã lưu id_mapping.")

if __name__ == "__main__":
    create_faiss_index()
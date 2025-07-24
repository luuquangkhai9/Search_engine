import pandas as pd
import pickle

def chunk_text(text, chunk_size=256, overlap=50):
    """Chia văn bản thành các đoạn nhỏ có chồng lấn."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def main():
    # 1. Đọc dữ liệu
    df = pd.read_csv('data/articles.csv')
    print(f"Đã đọc {len(df)} bài viết.")

    # 2. Chunking
    all_chunks = []
    for index, row in df.iterrows():
        doc_id = row['id']
        content = row['content']
        chunks = chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'doc_id': doc_id,
                'chunk_id': f"{doc_id}_{i}",
                'content': chunk
            })

    # 3. Lưu lại
    chunked_df = pd.DataFrame(all_chunks)
    chunked_df.to_csv('data/chunked_articles.csv', index=False)
    print(f"Đã tạo và lưu {len(chunked_df)} chunks vào data/chunked_articles.csv")

if __name__ == "__main__":
    main()
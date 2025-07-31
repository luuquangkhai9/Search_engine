import pandas as pd
from underthesea import word_tokenize, sent_tokenize
from transformers import AutoTokenizer
from tqdm import tqdm

PARQUET_FILE_PATH = r'C:\Users\Administrator\Documents\Search_engine\data\sample_100000.parquet'
OUTPUT_CSV_PATH = 'data/chunked_v2.csv'
MODEL_NAME = 'keepitreal/vietnamese-sbert'

TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)

def structured_chunking_with_overlap(text, max_tokens=256, sentence_overlap=2):
    """
    Chunking với underthesea, chồng lấn (overlap) giữa các chunk.
    """
    try:
        word_segmented_text = word_tokenize(text, format="text")
        sentences = sent_tokenize(word_segmented_text)
    except Exception:
        return []

    if not sentences:
        return []

    chunks = []
    current_chunk_sentences = []
    current_chunk_tokens = 0
    
    for sentence in sentences:
        sentence_tokens = len(TOKENIZER.encode(sentence, add_special_tokens=False))
        
        # Nếu thêm câu này sẽ vượt quá giới hạn, lưu chunk hiện tại
        if current_chunk_tokens + sentence_tokens > max_tokens and current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))
            
            # Bắt đầu chunk mới với sự chồng lấn
            overlap_start_index = max(0, len(current_chunk_sentences) - sentence_overlap)
            current_chunk_sentences = current_chunk_sentences[overlap_start_index:]
            current_chunk_tokens = len(TOKENIZER.encode(" ".join(current_chunk_sentences), add_special_tokens=False))
            
        # Thêm câu hiện tại vào chunk
        current_chunk_sentences.append(sentence)
        current_chunk_tokens += sentence_tokens

    # Thêm chunk cuối cùng vào danh sách
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))
        
    return chunks

def main():
    df = pd.read_parquet(PARQUET_FILE_PATH)
    print(f"Đã đọc {len(df)} bài viết.")

    all_chunks = []
    print("Bắt đầu chunking văn bản (underthesea + overlap)...")
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Chunking Progress"):
        doc_id = row['id']
        content = row['text']
        domain = row['domain']
        
        if not isinstance(content, str) or not content.strip():
            continue

        # Gọi hàm chunking mới có overlap
        chunks = structured_chunking_with_overlap(content)
        
        for i, chunk_content in enumerate(chunks):
            all_chunks.append({
                'doc_id': doc_id,
                'chunk_id': f"{doc_id}_{i}",
                'content': chunk_content,
                'domain': domain
            })

    chunked_df = pd.DataFrame(all_chunks)
    chunked_df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"\nĐã tạo và lưu {len(chunked_df)} chunks vào {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    main()
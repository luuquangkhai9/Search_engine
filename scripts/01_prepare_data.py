import pandas as pd
from underthesea import sent_tokenize
from transformers import AutoTokenizer

# Tải tokenizer của mô hình
MODEL_NAME = 'AITeamVN/Vietnamese_Embedding_v2'
TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)

def chunk_text_by_sentence(text, max_tokens=256, sentence_overlap=2):
    """
    Chia văn bản thành các đoạn nhỏ (chunk) dựa trên tách câu từ underthesea.
    Mỗi chunk có tối đa max_tokens. chồng lắp câu giữa các chunk.
    """
    try:
        sentences = sent_tokenize(text)
    except Exception as e:
        print(f"[Lỗi] Không thể tách câu văn bản: {e}")
        return []

    chunks = []
    current_chunk_sentences = []
    current_chunk_tokens = 0

    for i, sentence in enumerate(sentences):
        sentence_tokens = len(TOKENIZER.encode(sentence, add_special_tokens=False))

        # Nếu thêm câu này sẽ vượt quá giới hạn token
        if current_chunk_tokens + sentence_tokens > max_tokens and current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))

            # Tạo overlap: lấy lại n câu cuối của chunk trước
            overlap_start = max(0, len(current_chunk_sentences) - sentence_overlap)
            current_chunk_sentences = current_chunk_sentences[overlap_start:]
            current_chunk_tokens = len(TOKENIZER.encode(" ".join(current_chunk_sentences), add_special_tokens=False))

        # Thêm câu vào chunk hiện tại
        current_chunk_sentences.append(sentence)
        current_chunk_tokens += sentence_tokens

    # Thêm chunk cuối cùng nếu còn
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks

def main():
    df = pd.read_csv('data/articles.csv')
    print(f"Đã đọc {len(df)} bài viết.")

    all_chunks = []

    for index, row in df.iterrows():
        doc_id = row.get('id')
        content = row.get('content')

        if not isinstance(content, str) or not content.strip():
            print(f"[Bỏ qua] Dòng {index} không có nội dung hợp lệ.")
            continue

        chunks = chunk_text_by_sentence(content)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'doc_id': doc_id,
                'chunk_id': f"{doc_id}_{i}",
                'content': chunk
            })

    chunked_df = pd.DataFrame(all_chunks)
    chunked_df.to_csv('data/chunked_articles.csv', index=False)
    print(f"Đã tạo và lưu {len(chunked_df)} chunks vào 'data/chunked_articles.csv'")

if __name__ == "__main__":
    main()

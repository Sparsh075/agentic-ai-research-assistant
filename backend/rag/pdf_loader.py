from pypdf import PdfReader


def _split_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks = []
    start = 0
    step = max(1, chunk_size - chunk_overlap)
    text_length = len(cleaned)

    while start < text_length:
        end = min(text_length, start + chunk_size)
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_length:
            break
        start += step

    return chunks


def load_and_chunk_pdf(pdf_path: str):
    reader = PdfReader(pdf_path)
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    return _split_text("\n".join(text_parts))


def load_and_chunk_pdf_with_metadata(pdf_path: str):
    reader = PdfReader(pdf_path)
    records = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if not page_text:
            continue

        page_chunks = _split_text(page_text)
        for chunk_idx, chunk in enumerate(page_chunks):
            records.append(
                {
                    "text": chunk,
                    "page_number": page_number,
                    "chunk_id": f"p{page_number}_c{chunk_idx}",
                }
            )

    return records


if __name__ == "__main__":
    pdf_path = "data/transformer_paper.pdf"
    chunks = load_and_chunk_pdf(pdf_path)

    print(f"Total chunks created: {len(chunks)}")
    print("\n--- Sample Chunk ---\n")
    print(chunks[0][:1000])

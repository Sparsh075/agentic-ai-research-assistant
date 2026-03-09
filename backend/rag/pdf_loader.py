from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter



def load_and_chunk_pdf(pdf_path: str):
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_text(text)
    return chunks


def load_and_chunk_pdf_with_metadata(pdf_path: str):
    reader = PdfReader(pdf_path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    records = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if not page_text:
            continue

        page_chunks = splitter.split_text(page_text)
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
    pdf_path = "data/transformer_paper.pdf"  # change if needed
    chunks = load_and_chunk_pdf(pdf_path)

    print(f"Total chunks created: {len(chunks)}")
    print("\n--- Sample Chunk ---\n")
    print(chunks[0][:1000])

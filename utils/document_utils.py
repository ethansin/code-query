from langchain_core.documents import Document

def create_document(document_contents: str, file_name: str):
    return Document(
        page_content=document_contents,
        metadata={"file_name": file_name}
    )

def is_indented(line):
    return len(line) - len(line.lstrip()) > 0 and line.strip() != ""
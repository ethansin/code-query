#!/usr/bin/env python3

import os
import faiss
import ast

from utils.document_utils import is_indented, create_document

from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from uuid import uuid4

from argparse import ArgumentParser

def parse_file(file_path: str) -> list:

    file_name = os.path.basename(file_path)
    with open(file_path, 'r') as file:
        try:
            lines = file.readlines()
        except UnicodeDecodeError:
            print(f"Could not read file {file_path}")
            return []

    chunks = []
    for i in range(0, len(lines), 30):
        chunk = lines[i:i + 40]
        chunks.append(create_document(''.join(chunk), file_name))

    return chunks

def parse_python_script_by_indent(file_path: str) -> list:

    file_name = os.path.basename(file_path)
    with open(file_path, 'r') as file:
        try:
            lines = file.readlines()
        except UnicodeDecodeError:
            print(f"Could not read file {file_path}")
            return

    chunks = []
    current_chunk = []
    is_hierarchy = False
    for idx, line in enumerate(lines):

        if idx == len(lines) - 1:
            current_chunk.append(line)
            chunks.append(create_document(''.join(current_chunk), file_name))
            break

        if current_chunk == []:
            current_chunk = []
            current_chunk.append(line)
            if is_indented(lines[idx + 1]):
                is_hierarchy = True
            else:
                is_hierarchy = False
        elif len(current_chunk) > 50:
            current_chunk = lines[idx - 10:idx] + current_chunk
            chunks.append(create_document(''.join(current_chunk), file_name))
            current_chunk = []
            current_chunk.append(line)
            if is_indented(lines[idx + 1]):
                is_hierarchy = True
            else:
                is_hierarchy = False
        elif is_hierarchy:
            if is_indented(line) or line.strip() == "":
                current_chunk.append(line)
            else:
                chunks.append(create_document(''.join(current_chunk), file_name))
                current_chunk = []
                current_chunk.append(line)
                if is_indented(lines[idx + 1]):
                    is_hierarchy = True
                else:
                    is_hierarchy = False
        elif not is_hierarchy:
            if is_indented(lines[idx + 1]):
                chunks.append(create_document(''.join(current_chunk), file_name))
                current_chunk = []
                current_chunk.append(line)
                if is_indented(lines[idx + 1]):
                    is_hierarchy = True
                else:
                    is_hierarchy = False
            else:
                current_chunk.append(line)

    return chunks

def parse_python_script_by_tree(file_path: str) -> list:
    file_name = os.path.basename(file_path)
    with open(file_path, 'r') as file:
        try:
            tree = ast.parse(file.read(), filename=file_name)
        except (SyntaxError, UnicodeDecodeError):
            print(f"Could not parse file {file_path}")
            return []

    chunks = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_lineno = node.lineno - 1
            end_lineno = node.end_lineno if hasattr(node, 'end_lineno') else node.body[-1].lineno
            with open(file_path, 'r') as file:
                lines = file.readlines()
                function_code = ''.join(lines[start_lineno:end_lineno])
                chunks.append(create_document(function_code, file_name))

    return chunks


def create_documents(directory: str) -> None:
    doc_store = []
    for root, _, files in os.walk(directory):
        for file in files:
            documents = []
            file_path = os.path.join(root, file)
            if file_path.endswith(".py"):
                documents.extend(parse_python_script_by_indent(file_path))
                documents.extend(parse_python_script_by_tree(file_path))
            else:
                documents.extend(parse_file(file_path))
            if isinstance(documents, list):
                doc_store.extend(documents)
    return doc_store


def build_vector_store(path: str) -> None:

    if not os.path.exists("vector_stores"):
        os.makedirs("vector_stores")

    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    dim = len(embeddings.embed_query("Initialize embedding dimensions for index."))
    index = faiss.IndexFlatL2(dim)


    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    doc_store = create_documents(path)
    uuids = [str(uuid4()) for _ in range(len(doc_store))]
    vector_store.add_documents(documents=doc_store, ids=uuids)
    vector_store.save_local(f"vector_stores/{os.path.basename(path)}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path", type=str, help="Path to the directory containing the documents to be indexed.")
    args = parser.parse_args()

    build_vector_store(args.path)
import os

from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from scripts.index_codebase_in_vector_store import build_vector_store

app = FastAPI()

class QueryData(BaseModel):
    content: str
    repo_path: str

prompt = PromptTemplate.from_template(
    """
    You are an expert on the codebase at {repo_path} that is written in python.
    Under the context section, you are given relevant snippets from files in {repo_path}.
    Use only this information to answer the question in the question section.
    If the answer is unclear, just say you do not know.

    ## Context
    {context}

    ## Question
    {question}
    """
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.9,
)
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

def query_vector_store(query: str, vector_store: FAISS, k: int = 4):
    results = vector_store.similarity_search(
        query,
        k=k,
    )
    return results

@app.post("/query")
def code_query(query: QueryData):
    vector_store = FAISS.load_local(f"vector_stores/{os.path.basename(query.repo_path)}", embeddings, "index", allow_dangerous_deserialization=True)
    results = query_vector_store(query.content, vector_store, k=6)
    retrieved_context = ""
    for result in results:
        retrieved_context += f"## from {result.metadata["file_name"]}:\n{result.page_content}\n\n"

    messages = prompt.invoke({
        "repo_path": query.repo_path,
        "context": retrieved_context,
        "question": query.content,
    })
    response = llm.invoke(messages)
    return response.content

@app.post("/retrieval")
def code_retrieval(query: QueryData):
    vector_store = FAISS.load_local(f"vector_stores/{os.path.basename(query.repo_path)}", embeddings, "index", allow_dangerous_deserialization=True)
    results = query_vector_store(query.content, vector_store, k=6)
    return results
    
@app.post("/create_vector_store")
def create_vector_store(query: QueryData):
    if os.path.exists(f"vector_stores/{os.path.basename(query.repo_path)}"):
        return "Vector store already exists, skipping creation."
    else:
        build_vector_store(query.repo_path)
        return "Vector store created!"
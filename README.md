# code-query

A REST API to build an indexed vector store of a target repository and initiate retrieval-augmented response generations from an LLM. Make sure the target repository is a fresh repository that does not have packages/modules installed as currently the vector store creation function cannot ignore those package files.

## Installation
The following commands will install all necessary requirements, run the process to host the REST API app locally, and initialize a script to make requests to the REST API

```
cd path/to/code-query
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn main:app --reload    
```

Then in another terminal

```
cd path/to/code-query
bash make_query.sh path/to/target-repo
```

From there you will be given two prompts
Answer 1 to get the relevant code snippets to your query without an LLM generation.
Answer 2 to get the retrieval-augmented LLM generation to your answer.

```
Enter 1 for retrieval-only and 2 for query:
Enter your query about "path/to/target-repo":
```

OR use these commands to make the requests directly

```
curl -X POST "http://127.0.0.1:8000/create_vector_store" -H "Content-Type: application/json" -d JSON_INPUT
curl -X POST "http://127.0.0.1:8000/retrieval" -H "Content-Type: application/json" -d JSON_INPUT
curl -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d JSON_INPUT
```

Where JSON_INPUT should contain a dictionary that looks like:

```
{
    "content": your query here,
    "repo_path": path/to/target-repo
}
```

Making the POST request to `/create_vector_store` OR running `scripts/index_codebase_in_vector_store.py` first is necessary for `/retrieval` and `/query` to work.
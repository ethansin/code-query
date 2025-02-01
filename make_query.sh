#!/bin/bash

repo_path=$1

curl -X POST "http://127.0.0.1:8000/create_vector_store" -H "Content-Type: application/json" -d "{\"content\": \"$content\", \"repo_path\": \"$repo_path\"}"

read -p "Enter 1 for retrieval-only and 2 for query: " TYPE
read -p "Enter your query about \"$repo_path\": " content

if [ $TYPE -eq 1 ]; then
    curl -X POST "http://127.0.0.1:8000/retrieval" -H "Content-Type: application/json" -d "{\"content\": \"$content\", \"repo_path\": \"$repo_path\"}"
elif [ $TYPE -eq 2 ]; then
    curl -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d "{\"content\": \"$content\", \"repo_path\": \"$repo_path\"}"
else
    echo "Invalid choice"
    exit 1
fi


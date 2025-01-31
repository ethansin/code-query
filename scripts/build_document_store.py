import os

def is_indented(line):
    return len(line) - len(line.lstrip()) > 0 and line.strip() != ""

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
        chunks.append({
            "content": ''.join(chunk),
            "metadata": {"file_name": file_name}
        })

    return chunks

def parse_python_script(file_path: str) -> None:

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
            chunks.append({
                "content": ''.join(current_chunk),
                "metadata": {"file_name": file_name}
            })
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
            chunks.append({
                "content": ''.join(current_chunk),
                "metadata": {"file_name": file_name}
            })
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
                chunks.append({
                    "content": ''.join(current_chunk),
                    "metadata": {"file_name": file_name}
                })
                current_chunk = []
                current_chunk.append(line)
                if is_indented(lines[idx + 1]):
                    is_hierarchy = True
                else:
                    is_hierarchy = False
        elif not is_hierarchy:
            if is_indented(lines[idx + 1]):
                chunks.append({
                    "content": ''.join(current_chunk),
                    "metadata": {"file_name": file_name}
                })
                current_chunk = []
                current_chunk.append(line)
                if is_indented(lines[idx + 1]):
                    is_hierarchy = True
                else:
                    is_hierarchy = False
            else:
                current_chunk.append(line)

    return chunks


def walk_directory(directory: str) -> None:
    doc_store = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(".py"):
                documents = parse_python_script(file_path)
            else:
                documents = parse_file(file_path)
            if isinstance(documents, list):
                doc_store.extend(documents)
    return doc_store


def main(path: str) -> None:
    walk_directory(path)


if __name__ == "__main__":
    main("/Users/ethansin/Desktop/mcode-project/grip-no-tests")
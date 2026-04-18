import os

EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'node_modules', '.idea', '.vscode'}

SERVER_EXCLUDE_FILES = {'.DS_Store', 'codebase_bundle.txt', 'bundle_codebase.py', 'scan_stats.py'}
SERVER_EXTENSIONS = {'.py', '.sql', '.html', '.css', '.js', '.json', '.env', '.example', '.txt', '.md', '.sh', '.lua'}

CLIENT_EXCLUDE_FILES = {'.DS_Store', 'package-lock.json'}
CLIENT_EXTENSIONS = {'.ts', '.tsx', '.js', '.json'}

def collect_files(root_dir, extensions, exclude_files):
    files_to_process = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file in exclude_files:
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                files_to_process.append(os.path.join(root, file))
    return sorted(files_to_process)

def write_files(f, files, label_root):
    for file_path in files:
        relative_path = os.path.relpath(file_path, label_root)
        f.write("=" * 80 + "\n")
        f.write(f"FILE: {relative_path}\n")
        f.write("=" * 80 + "\n\n")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as source_file:
                f.write(source_file.read())
        except Exception as e:
            f.write(f"[ERROR READING FILE: {str(e)}]")
        f.write("\n\n")

if __name__ == "__main__":
    repo_root = "/Users/yousefbustami/Desktop/saas-authentication-paid"
    server_dir = os.path.join(repo_root, "server")
    client_dir = os.path.join(repo_root, "client")
    output_path = os.path.join(server_dir, "codebase_bundle.txt")

    server_files = collect_files(server_dir, SERVER_EXTENSIONS, SERVER_EXCLUDE_FILES)
    client_files = collect_files(client_dir, CLIENT_EXTENSIONS, CLIENT_EXCLUDE_FILES)

    print(f"📦 Bundling server ({len(server_files)} files) + client ({len(client_files)} files)...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("SERVER\n")
        f.write("=" * 80 + "\n\n")
        write_files(f, server_files, repo_root)

        f.write("=" * 80 + "\n")
        f.write("CLIENT\n")
        f.write("=" * 80 + "\n\n")
        write_files(f, client_files, repo_root)

    print(f"✅ Codebase successfully bundled into: {output_path}")

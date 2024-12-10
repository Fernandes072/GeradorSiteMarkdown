import subprocess
import os

pandoc_exe = "pandoc.exe"

def exec_pandoc(md_file_path, md_file_name, dist_path):
    relative_path = os.path.relpath(md_file_path, "../docs")
    dist_path = os.path.join(dist_path, relative_path)
    os.makedirs(dist_path, exist_ok=True)
    md_file = os.path.join(md_file_path, md_file_name)
    html_file = os.path.join(dist_path, os.path.basename(md_file).replace(".md", ".html"))
    subprocess.run([pandoc_exe, md_file, "-o", html_file, "--template", "template.html"])
    return None

def convert_md_files(docs, dist):
    for path, _, files in os.walk(docs):
        for file in files:
            if file.endswith(".md"):
                #exec_pandoc(os.path.join(path, file), dist)
                exec_pandoc(path, file, dist)

def main(docs, dist):
    convert_md_files(docs, dist)

main("../docs", "../dist")
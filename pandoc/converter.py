import subprocess
import os

pandoc_exe = "pandoc.exe"

def exec_pandoc(md_file, dist_path):
    #relative_path = os.path.relpath(os.path.abspath(md_file), "../docs")
    #dist_path = os.path.join("../docs", relative_path)
    html_file = os.path.join(dist_path, os.path.basename(md_file).replace(".md", ".html"))
    subprocess.run([pandoc_exe, md_file, "-o", html_file, "--template", "template.html"])
    return None

def convert_md_files(docs, dist):
    for path, _, files in os.walk(docs):
        for file in files:
            if file.endswith(".md"):
                exec_pandoc(os.path.join(path, file), dist)

def main(docs, dist):
    convert_md_files(docs, dist)

main("../docs", "../dist")
import subprocess
import os

pandoc_exe = "pandoc.exe"

def exec_pandoc(md_file, dist_path):
    html_file = os.path.join(dist_path, os.path.basename(md_file).replace(".md", ".html"))
    subprocess.run([pandoc_exe, md_file, "-o", html_file, "--template", "template.html"])
    return None

exec_pandoc("../docs/teste.md", "../dist")
import subprocess
import os
import argparse
import shutil

pandoc_exe = "pandoc.exe"

def exec_pandoc(md_file_path, md_file_name, input, output):
    #Pega o caminho do arquivo md sem o caminho de entrada
    relative_path = os.path.relpath(md_file_path, input)
    #Junta o caminho de saída com o caminho do arquivo md
    output = os.path.join(output, relative_path)
    #Cria a pasta de saída
    os.makedirs(output, exist_ok=True)
    #Junta o caminho do arquivo md com o nome do arquivo
    md_file = os.path.join(md_file_path, md_file_name)
    #Junta o caminho de saída com o nome do arquivo .md substituindo por .html
    html_file = os.path.join(output, md_file_name.replace(".md", ".html"))
    subprocess.run([pandoc_exe, md_file, "-o", html_file, "--template", "template.html"])

def copy_files(file_path, file_name, input, output):
    relative_path = os.path.relpath(file_path, input)
    output = os.path.join(output, relative_path)
    os.makedirs(output, exist_ok=True)
    file = os.path.join(file_path, file_name)
    output_file = os.path.join(output, file_name)
    shutil.copy(file, output_file)

def convert_md_files(input, output):
    #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
    for path, _, files in os.walk(input):
        for file in files:
            if file.endswith(".md"):
                #Passa o caminho da pasta, o nome do arquivo, o caminho de entrada e o caminho de saída
                exec_pandoc(path, file, input, output)
            else:
                copy_files(path, file, input, output)

#Pega os argumentos passados pelo terminal
def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="../dist")
    return parser.parse_args()

def main():
    args = arguments()
    os.makedirs(args.output, exist_ok=True)
    convert_md_files(args.input, args.output)

#python converter.py -i ""../docs" [-o ""../dist"]
main()
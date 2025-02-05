import subprocess
import os
import argparse
import shutil
import re

def replaceMdToHtml(htmlFile): # Substitui .md por .html
    with open(htmlFile, 'r', encoding='utf-8') as file:
        text = file.read() # Pega o conteúdo do arquivo html
    text = text.replace(".md", ".html") # Substitui .md por .html
    with open(htmlFile, 'w', encoding='utf-8') as file:
        file.write(text) # Escreve o conteúdo no arquivo html, mas com a alteração

#pode ter o header e o footer então precisa ser uma lista
def updateInclude(htmlFile, outputPath): # Substitui o !!!__ INCLUDE “nome-do-arquivo” __!!! pelo conteúdo do arquivo
    with open(htmlFile, 'r', encoding='utf-8') as file:
        text = file.read() # Pega o conteúdo do arquivo html
    regex = r'!!!__ INCLUDE “([^”]+)” __!!!' # Regex para encontrar o INCLUDE e pegar o nome do arquivo
    results = re.findall(regex, text) # Procura o INCLUDE no conteúdo do arquivo
    for result in results:
        resultFile = os.path.join(f"{outputPath}/templates", result) # Junta o caminho da pasta de templates com o nome do arquivo
        with open(resultFile, 'r', encoding='utf-8') as file:
            otherText = file.read() # Pega o conteúdo do arquivo do template
        regex = r'<main[^>]*>(.*?)</main>' # Regex para pegar o conteúdo da tag main
        otherResult = re.search(regex, otherText, re.DOTALL) # Procura a tag main no conteúdo do arquivo do template
        if otherResult:
            otherResult = otherResult.group(1) # Pega o conteúdo da tag main
            text = text.replace("!!!__ INCLUDE “" + result + "” __!!!", otherResult) # Substitui o INCLUDE pelo conteúdo da tag main
            with open(htmlFile, 'w', encoding='utf-8') as file:
                file.write(text) # Escreve o conteúdo no arquivo html, mas com a alteração

def updateWorkDir(htmlFile, outputPath): # Atualiza o {workdir} para o caminho relativo da pasta assets/assets-do-script
    workDir = os.path.relpath(f"{outputPath}/assets/assets-do-script", os.path.dirname(htmlFile)) # Calcula o caminho relativo do arquivo html para a pasta assets/assets-do-script
    with open(htmlFile, 'r', encoding='utf-8') as file:
        text = file.read() # Pega o conteúdo do arquivo html
    text = text.replace("{workdir}assets", workDir) # Substitui o {workdir}assets pelo caminho relativo calculado
    with open(htmlFile, 'w', encoding='utf-8') as file:
        file.write(text) # Escreve o conteúdo no arquivo html, mas com a alteração

def adjustments(outputPath): # Faz ajustes nos arquivos .html
    for path, _, files in os.walk(outputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if file.endswith(".html"):
                file = os.path.join(path, file) #Junta o caminho da pasta com o nome do arquivo
                replaceMdToHtml(file) # Substitui .md por .html
                updateInclude(file, outputPath) # Substitui o INCLUDE pelo conteúdo do arquivo
                updateWorkDir(file, outputPath) # Atualiza o {workdir}

def execPandoc(mdFilePath, mdFileName, inputPath, outputPath): #Converte os arquivos .md para .html
    relativePath = os.path.relpath(mdFilePath, inputPath) #Pega o caminho do arquivo md sem o caminho de entrada
    outputPath = os.path.join(outputPath, relativePath) #Junta o caminho de saída com o caminho do arquivo md
    os.makedirs(outputPath, exist_ok=True) #Cria a pasta de saída
    mdFile = os.path.join(mdFilePath, mdFileName) #Junta o caminho do arquivo md com o nome do arquivo
    htmlFile = os.path.join(outputPath, mdFileName.replace(".md", ".html")) #Junta o caminho de saída com o nome do arquivo .md substituindo por .html
    templatePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html") #Pega o caminho absoluto do script, tira o nome do script e junta com o template.html
    pandoc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pandoc.exe") #Pega o caminho absoluto do script, tira o nome do script e junta com o pandoc.exe
    subprocess.run([pandoc, mdFile, "-o", htmlFile, "--template", templatePath]) #Exexcuta o pandoc

def copyFiles(inputFilePath, inputFileName, inputPath, outputPath): #Copia os arquivos que não são .md
    relativePath = os.path.relpath(inputFilePath, inputPath) #Pega o caminho do arquivo sem o caminho de entrada
    outputPath = os.path.join(outputPath, relativePath) #Junta o caminho de saída com o caminho do arquivo
    os.makedirs(outputPath, exist_ok=True) #Cria a pasta de saída
    inputFile = os.path.join(inputFilePath, inputFileName) #Junta o caminho do arquivo com o nome do arquivo
    outputFile = os.path.join(outputPath, inputFileName) #Junta o caminho de saída com o nome do arquivo
    shutil.copy(inputFile, outputFile) #Copia o arquivo

def convertMdFiles(inputPath, outputPath): #Varre as pastas para converter os arquivos .md e copiar os outros arquivos
    for path, _, files in os.walk(inputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if file.endswith(".md"):
                execPandoc(path, file, inputPath, outputPath) #Passa o caminho da pasta, o nome do arquivo, o caminho de entrada e o caminho de saída
            else:
                copyFiles(path, file, inputPath, outputPath)

def copyAssets(outputPath):
    os.makedirs(os.path.join(outputPath, "assets/assets-do-script"), exist_ok=True) #Cria a pasta assets/assets-do-script na pasta de saída
    assetsDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets") #Pega o caminho absoluto do script, tira o nome do script e junta com a pasta assets
    for file in os.listdir(assetsDir):
        shutil.copy(os.path.join(assetsDir, file), os.path.join(outputPath, "assets/assets-do-script", file)) #Copia os arquivos da pasta assets para a pasta assets/assets-do-script na pasta de saída

def arguments(): #Pega os argumentos passados pelo terminal
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="dist")
    return parser.parse_args()

def main():
    args = arguments()
    inputPath = os.path.abspath(args.input) #Caminho absoluto da pasta de entrada
    outputPath = os.path.join(os.path.dirname(args.input), args.output) #Pega o caminho em que a pasta de entrada está e junta com a pasta de saída
    os.makedirs(outputPath, exist_ok=True) #Cria a pasta de saída
    convertMdFiles(inputPath, outputPath)
    copyAssets(outputPath)
    adjustments(outputPath)

#python converter.py -i "../docs"
#Caminho absoluto: python "D:/Trabalho Web/Projeto/pandoc/converter.py" -i "D:/Trabalho Web/Projeto/src"
#Na pasta do pandoc: python converter.py -i "D:/Trabalho Web/Projeto/src"
#Na pasta do pandoc: converter.py -i "../docs"
main()
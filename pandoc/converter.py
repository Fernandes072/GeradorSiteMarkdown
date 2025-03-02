import subprocess
import os
import argparse
import shutil
import re
import cssmin
import jsmin
import htmlmin
from PIL import Image

def dpiImage(image, outputPath, dpi): # Ajusta o dpi da imagem
    for path, _, files in os.walk(outputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if file == image:
                file = os.path.join(path, file) # Junta o caminho da pasta com o nome da imagem original
                image = Image.open(file) # Abre a imagem original
                ext = file.split('.')[-1] # Pega a extensão da imagem
                image.save(file.replace("." + ext, f'-{dpi}.' + ext), dpi=(dpi, dpi)) # Adiciona o dpi no nome da imagem e salva a imagem
                return file

def resizeImage(image, outputPath, dimensions): # Redimensiona a imagem
    for path, _, files in os.walk(outputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if file == image:
                file = os.path.join(path, file) # Junta o caminho da pasta com o nome da imagem original
                image = Image.open(file) # Abre a imagem original
                image = image.resize((int(dimensions[0]), int(dimensions[1]))) # Redimensiona a imagem
                ext = file.split('.')[-1] # Pega a extensão da imagem
                image.save(file.replace("." + ext, f'-{dimensions[0]}x{dimensions[1]}.' + ext)) # Adiciona as dimensões no nome da imagem e salva a imagem
                return file

def removeMetadata(image, outputPath): # Remove os metadados da imagem
    for path, _, files in os.walk(outputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if file == image:
                file = os.path.join(path, file) # Junta o caminho da pasta com o nome da imagem original
                image = Image.open(file) # Abre a imagem original
                data = list(image.getdata()) # Pega os dados da imagem
                newImage = Image.new(image.mode, image.size) # Cria uma nova imagem com o mesmo modo e tamanho da imagem original
                newImage.putdata(data) # Coloca os dados na nova imagem
                ext = file.split('.')[-1] # Pega a extensão da imagem
                newImage.save(file.replace("." + ext, '-no-exif.' + ext)) # Adiciona no-exif no nome da imagem e salva a imagem
                return file

def convertToWebp(image, outputPath): # Converte a imagem para .webp
    for path, _, files in os.walk(outputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
            for file in files:
                if file == image:
                    ext = file.split('.')[-1] # Pega a extensão da imagem original
                    file = os.path.join(path, file) # Junta o caminho da pasta com o nome da imagem original
                    image = Image.open(file) # Abre a imagem original
                    image.save(file.replace(ext, 'webp'), "WEBP", quality=90) # Salva a imagem em .webp
                    fileSize = os.path.getsize(file) # Pega o tamanho do arquivo original
                    webpSize = os.path.getsize(file.replace(ext, 'webp')) # Pega o tamanho do arquivo .webp
                    if (webpSize > fileSize):
                        os.remove(file.replace(ext, 'webp')) # Apaga a imagem webp
                        return False
                    return True, file

def imageOptimizations(mdFile, outputPath): # Faz otimizações nas imagens
    with open(mdFile, 'r', encoding='utf-8') as f:
        text = f.read() # Pega o conteúdo do arquivo
    regex = r'!\[.*?\](.+)' # Regex para encontrar ![] e pegar o que vem depois
    results = re.findall(regex, text, re.MULTILINE) # Procura ![] no conteúdo do arquivo e retorna uma lista de ocorrências
    for result in results:
        removeImage = False # Na primeira modificação a imagem fonte é mantida, mas nas próximas é removida
        result = result.split("@") # (imagem)@[ajustes] -> Separa o nome da imagem e os ajustes
        if (len(result) == 2): # Se tiver menos de 2 elementos não tem ajustes e se tiver mais digitou errado
            complements = "{" # São alguns atributos que podem ser adicionados na tag img, como loading, class, id
            newImage = result[0] # É o (imagem) final, que vai sofrer as alterações no nome e será substituído no texto
            adjustments = result[1].replace("[", "").replace("]", "").split(" + ") # Tira os colchetes e separa os ajustes
            for adjustment in adjustments:
                if (adjustment == "converter-imagem"):
                    image = os.path.basename(newImage.split(" ")[0].replace("(", "").replace(")", "")) # Pega o nome da imagem
                    hasConverted, pathImage = convertToWebp(image, outputPath) # Converte a imagem para .webp
                    if hasConverted:
                        if removeImage:
                            os.remove(pathImage) # Apaga a imagem antiga
                        ext = image.split('.')[-1] # Pega a extensão da imagem original
                        newImage = newImage.replace(ext, 'webp') # Substitui a extensão da imagem original por .webp
                        removeImage = True
                elif (adjustment == "remover-exif"):
                    image = os.path.basename(newImage.split(" ")[0].replace("(", "").replace(")", "")) # Pega o nome da imagem
                    pathImage = removeMetadata(image, outputPath) # Remove os metadados da imagem
                    if removeImage:
                        os.remove(pathImage) # Apaga a imagem antiga
                    ext = newImage.split('.')[-1] # Pega a extensão da imagem
                    newImage = newImage.replace("." + ext, '-no-exif.' + ext) # Adiciona no-exif no nome da imagem
                    removeImage = True
                elif (adjustment.split("=")[0] == "resolucao"):
                    image = os.path.basename(newImage.split(" ")[0].replace("(", "").replace(")", "")) # Pega o nome da imagem
                    dimensions = adjustment.split("=")[1].split("x") # Pega as dimensões da imagem
                    pathImage = resizeImage(image, outputPath, dimensions) # Redimensiona a imagem
                    if removeImage:
                        os.remove(pathImage) # Apaga a imagem antiga
                    ext = newImage.split('.')[-1] # Pega a extensão da imagem
                    newImage = newImage.replace("." + ext, f'-{dimensions[0]}x{dimensions[1]}.' + ext) # Adiciona a resolução no nome da imagem
                    removeImage = True
                elif (adjustment.split("=")[0] == "dpi"):
                    image = os.path.basename(newImage.split(" ")[0].replace("(", "").replace(")", "")) # Pega o nome da imagem
                    dpi = adjustment.split("=")[1] # Pega o dpi da imagem
                    pathImage = dpiImage(image, outputPath, dpi) # Ajusta o dpi a imagem
                    if removeImage:
                        os.remove(pathImage) # Apaga a imagem antiga
                    ext = newImage.split('.')[-1] # Pega a extensão da imagem
                    newImage = newImage.replace("." + ext, f'-{dpi}.' + ext) # Adiciona o dpi no nome da imagem
                    removeImage = True
                else:
                    complements += ' loading="lazy"'
            text = text.replace(result[0] + "@" + result[1], newImage + complements + "}") # Substitui (imagem)@[ajustes] por (imagem){complementos}
    with open(mdFile, 'w', encoding='utf-8') as f:
        f.write(text) # Escreve o conteúdo no arquivo, mas com as alterações

def minifyHtml(outputPath): # Minifica os arquivos .html
    for path, _, files in os.walk(outputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if file.endswith(".html"):
                file = os.path.join(path, file) #Junta o caminho da pasta com o nome do arquivo
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read() #Pega o conteúdo do arquivo .html
                text = htmlmin.minify(text) #Minifica o conteúdo do arquivo .html
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(text) #Escreve o conteúdo minificado no arquivo .html

def minifyCssJs(outputPath): # Minifica os arquivos .css e .js
    # Essa parte minifica os arquivos .css e .js
    cssjsFiles = {}
    for path, _, files in os.walk(outputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if file.endswith(".css"):
                cssjsFiles[file] = file.replace(".css", ".min.css") #Adiciona o nome do arquivo .css e .min.css no dicionário
                file = os.path.join(path, file) #Junta o caminho da pasta com o nome do arquivo
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read() #Pega o conteúdo do arquivo .css
                text = cssmin.cssmin(text) #Minifica o conteúdo do arquivo .css
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(text) #Escreve o conteúdo minificado no arquivo .css
                os.rename(file, file.replace(".css", ".min.css")) #Renomeia o arquivo .css para .min.css
            elif file.endswith(".js"):
                cssjsFiles[file] = file.replace(".js", ".min.js") #Adiciona o nome do arquivo .js e .min.js no dicionário
                file = os.path.join(path, file) #Junta o caminho da pasta com o nome do arquivo
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read() #Pega o conteúdo do arquivo .js
                text = jsmin.jsmin(text) #Minifica o conteúdo do arquivo .js
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(text) #Escreve o conteúdo minificado no arquivo .js
                os.rename(file, file.replace(".js", ".min.js")) #Renomeia o arquivo .js para .min.js

    # Essa parte substitui os arquivos .css pelos .min.css nos arquivos .html
    for path, _, files in os.walk(outputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if file.endswith(".html"):
                file = os.path.join(path, file) #Junta o caminho da pasta com o nome do arquivo
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read() #Pega o conteúdo do arquivo .html
                for key in cssjsFiles:
                    text = text.replace(key, cssjsFiles[key]) #Substitui o nome do arquivo .css pelo nome do arquivo .min.css
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(text) #Escreve o conteúdo no arquivo .html, mas com as alterações

def replaceHrInMdFiles(mdFile): # Substitui -- por <hr> no arquivo .md
    with open(mdFile, 'r', encoding='utf-8') as f:
        text = f.read() # Pega o conteúdo do arquivo
    regex = r'--(.+)$' # Regex para encontrar --
    results = re.findall(regex, text, re.MULTILINE) # Procura -- no conteúdo do arquivo e retorna uma lista de ocorrências
    for result in results:
        regex = r'([a-zA-Z0-9]+:[a-zA-Z0-9]+)' # Regex para pegar informações no formato chave:valor
        otherResults = re.findall(regex, result) # Procura informações no formato chave:valor para cada ocorrência de --
        classhr = []
        classhr.append("ca-hr") # Adiciona a classe ca-hr que é padrão para todos os hr
        for r in otherResults:
            r = r.split(":") # Separa a chave e o valor
            if r[0] == "h":
                classhr.append(f"ca-{r[1]}") # Se a chave for h, adiciona a classe ca-valor
            else:
                classhr.append(f"m{r[0]}-{r[1]}") # Para qualquer outra chave, adiciona a classe mchave-valor
        classhr = " ".join(classhr) # Junta todas as classes com um espaço entre elas
        text = text.replace(f"--{result}", f'<hr class="{classhr}">')
    with open(mdFile, 'w', encoding='utf-8') as f:
        f.write(text) # Escreve o conteúdo no arquivo, mas com as alterações
                
def replaceMdToHtml(htmlFile): # Substitui .md por .html
    with open(htmlFile, 'r', encoding='utf-8') as file:
        text = file.read() # Pega o conteúdo do arquivo html
    text = text.replace(".md", ".html") # Substitui .md por .html
    with open(htmlFile, 'w', encoding='utf-8') as file:
        file.write(text) # Escreve o conteúdo no arquivo html, mas com a alteração

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
                replaceMdToHtml(file) # Substitui .md por .html

def execPandoc(mdFilePath, mdFileName, inputPath, outputPath): #Converte os arquivos .md para .html
    relativePath = os.path.relpath(mdFilePath, inputPath) #Pega o caminho do arquivo md sem o caminho de entrada
    outputPath = os.path.join(outputPath, relativePath) #Junta o caminho de saída com o caminho do arquivo md
    os.makedirs(outputPath, exist_ok=True) #Cria a pasta de saída
    mdFile = os.path.join(mdFilePath, mdFileName) #Junta o caminho do arquivo md com o nome do arquivo
    htmlFile = os.path.join(outputPath, mdFileName.replace(".md", ".html")) #Junta o caminho de saída com o nome do arquivo .md substituindo por .html
    templatePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html") #Pega o caminho absoluto do script, tira o nome do script e junta com o template.html
    pandoc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pandoc.exe") #Pega o caminho absoluto do script, tira o nome do script e junta com o pandoc.exe
    with open(mdFile, 'r', encoding='utf-8') as file:
        text = file.read() #Pega o conteúdo do arquivo .md
    replaceHrInMdFiles(mdFile) #Substitui -- por <hr>, mas ele altera o arquivo de entrada, então salva o texto original, faz as alterações, converte o md e depois volta para o texto original
    imageOptimizations(mdFile, outputPath) #Faz as otimizações nas imagens
    subprocess.run([pandoc, mdFile, "-o", htmlFile, "--template", templatePath]) #Exexcuta o pandoc
    with open(mdFile, 'w', encoding='utf-8') as file:
        file.write(text) #Volta para o texto original

def copyFiles(inputPath, outputPath): #Copia os arquivos que não são .md
    for path, _, files in os.walk(inputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if not file.endswith(".md"):
                relativePath = os.path.relpath(path, inputPath) #Pega o caminho do arquivo sem o caminho de entrada
                outPath = os.path.join(outputPath, relativePath) #Junta o caminho de saída com o caminho do arquivo
                os.makedirs(outPath, exist_ok=True) #Cria a pasta de saída
                inputFile = os.path.join(path, file) #Junta o caminho do arquivo com o nome do arquivo
                outputFile = os.path.join(outPath, file) #Junta o caminho de saída com o nome do arquivo
                shutil.copy(inputFile, outputFile) #Copia o arquivo

def convertMdFiles(inputPath, outputPath): #Varre as pastas para converter os arquivos .md e copiar os outros arquivos
    for path, _, files in os.walk(inputPath): #path: caminho da pasta atual / _: subpastas na pasta atual / files: arquivos na pasta atual
        for file in files:
            if file.endswith(".md"):
                execPandoc(path, file, inputPath, outputPath) #Passa o caminho da pasta, o nome do arquivo, o caminho de entrada e o caminho de saída

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
    copyFiles(inputPath, outputPath)
    convertMdFiles(inputPath, outputPath)
    copyAssets(outputPath)
    adjustments(outputPath)
    minifyCssJs(outputPath)
    minifyHtml(outputPath)

#python converter.py -i "../docs"
#Caminho absoluto: python "D:/Trabalho Web/Projeto/pandoc/converter.py" -i "D:/Trabalho Web/Projeto/src"
#Na pasta do pandoc: python converter.py -i "D:/Trabalho Web/Projeto/src"
#Na pasta do pandoc: converter.py -i "../docs"
main()
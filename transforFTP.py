import os
import re
import logging
import py7zr
import lzma
import tempfile
from pathlib import Path

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("app.log", encoding='utf-8')
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

logger.propagate = False

def verificar_ou_criar_pasta_dados(pasta_destino="DadosFTP"):
    Path(pasta_destino).mkdir(exist_ok=True)
    logger.info("Pasta '%s' verificada/criada.", pasta_destino)

def obter_pastas_ano(pasta_raiz="DadosExtraidos"):
    padrao_ano = re.compile(r"^\d{4}$")
    pastas = [
        os.path.join(pasta_raiz, nome)
        for nome in os.listdir(pasta_raiz)
        if padrao_ano.match(nome) and os.path.isdir(os.path.join(pasta_raiz, nome))
    ]
    logger.info("Pastas de ano identificadas: %s", pastas)
    return pastas

def localizar_arquivos_7z(pasta_ano):
    arquivos = [
        str(path)
        for path in Path(pasta_ano).rglob("*.7z")
        if path.is_file()
    ]
    logger.info("Arquivos .7z encontrados em '%s': %s", pasta_ano, arquivos)
    return arquivos

def extrair_arquivos_texto(arquivo_7z, pasta_destino="Dados"):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with py7zr.SevenZipFile(arquivo_7z, mode='r') as archive:
                try:
                    arquivos_txt = [nome for nome in archive.getnames() if nome.lower().endswith(".txt")]
                except Exception as e:
                    logger.warning("Falha ao listar arquivos no .7z: %s - %s", arquivo_7z, str(e))
                    return

                for nome in arquivos_txt:
                    try:
                        archive.extract(path=temp_dir, targets=[nome])
                        caminho_temp = os.path.join(temp_dir, nome)
                        caminho_destino = os.path.join(pasta_destino, os.path.basename(nome))

                        try:
                            with open(caminho_temp, 'r', encoding='latin-1') as f:
                                conteudo = f.read()
                            with open(caminho_destino, 'w', encoding='latin-1') as f:
                                f.write(conteudo)
                            logger.info("Arquivo extraído com sucesso: %s", caminho_destino)

                        except Exception as e_texto:
                            logger.warning("Erro ao ler como texto: %s. Tentando restaurar como binário.", str(e_texto))
                            with open(caminho_temp, 'rb') as f:
                                conteudo_binario = f.read()

                            caminho_restaurado = caminho_destino + "_restaurado"
                            with open(caminho_restaurado, 'wb') as f:
                                f.write(conteudo_binario)

                            logger.info("Arquivo parcialmente restaurado como binário: %s", caminho_restaurado)

                    except Exception as e_individual:
                        logger.warning("Falha ao extrair '%s' em '%s': %s", nome, arquivo_7z, str(e_individual))

    except py7zr.exceptions.Bad7zFile:
        logger.error("Arquivo .7z inválido ou fortemente corrompido: %s", arquivo_7z)
    except lzma.LZMAError:
        logger.error("Erro LZMA ao processar: %s", arquivo_7z)
    except Exception as e:
        logger.exception("Erro inesperado ao processar '%s': %s", arquivo_7z, str(e))

def processar_dados_extraidos():
    pasta_dados = "Dados"
    verificar_ou_criar_pasta_dados(pasta_dados)

    pastas_ano = obter_pastas_ano("DadosExtraidos")
    for pasta_ano in pastas_ano:
        arquivos_7z = localizar_arquivos_7z(pasta_ano)
        for arquivo_7z in arquivos_7z:
            extrair_arquivos_texto(arquivo_7z, pasta_destino=pasta_dados)

if __name__ == "__main__":
    processar_dados_extraidos()


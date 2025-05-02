import os
import ftplib
import hashlib
import logging
import shutil
import socket
import datetime
import time

FTP_HOST = "ftp.mtps.gov.br"
FTP_USER = "anonymous"
FTP_PASS = ""
FTP_DIR = "/pdet/microdados/CAGED"
LOCAL_BASE_DIR = "DadosExtraidos"
TIME_INTERNET = 25

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

def verificar_conexao_net(timeout=5):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False

def aguardar_conexao_net():
    while not verificar_conexao_net():

        agora = datetime.datetime.now().strftime('%H:%M:%S')
        logger.warning(f"[{agora}] Sem conexão com a internet. Verificando novamente em {TIME_INTERNET} segundos...")
        time.sleep(TIME_INTERNET)

def clear_local_directory(directory):
    aguardar_conexao_net()
    if os.path.exists(directory):
        shutil.rmtree(directory)
        logger.info(f"Conteúdo da pasta {directory} removido.")
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Pasta {directory} recriada para novo carregamento.")

def connect_ftp():
    aguardar_conexao_net()
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(FTP_DIR)
    logger.info("Conectado ao FTP com sucesso.")
    return ftp

def calculate_md5(file_path):
    aguardar_conexao_net()
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Erro ao calcular hash MD5: {e}")
        return None

def listar_itens_flat(ftp, path_base):
    aguardar_conexao_net()
    itens = []

    def _listar_interno(path_atual, caminho_relativo=""):
        try:
            lista = []
            ftp.retrlines(f"LIST {path_atual}", lista.append)
            for linha in lista:
                partes = linha.split()
                nome = partes[-1]
                tipo = linha[0]
                caminho_completo = f"{path_atual}/{nome}".replace("//", "/")
                caminho_rel = os.path.join(caminho_relativo, nome)
                if tipo == 'd':
                    itens.append((caminho_completo, caminho_rel))
                    _listar_interno(caminho_completo, caminho_rel)
                else:
                    itens.append((caminho_completo, caminho_rel))
        except ftplib.error_perm as e:
            logger.warning(f"Erro ao acessar {path_atual}: {e}")

    _listar_interno(path_base)
    return itens

def geral():
    aguardar_conexao_net()
    clear_local_directory(LOCAL_BASE_DIR)
    ftp = connect_ftp()

    logger.info("Listando todos os arquivos disponíveis...")
    todos_itens = listar_itens_flat(ftp, FTP_DIR)

    if not todos_itens:
        logger.warning("Nenhum arquivo encontrado no FTP.")
        return

    nomes_relativos = [rel for _, rel in todos_itens]
    itens_numerados = [f"[{i}] {nome}" for i, nome in enumerate(nomes_relativos)]

    logger.info("Itens disponíveis para seleção: " + " | ".join(itens_numerados))

    escolhas = input(">>>>>>>>>>>>>>>>>>>>>>>>>>>> Digite os números dos arquivos ou pastas que deseja baixar separados por vírgula ou 'tudo' para baixar tudo: ").strip()

    logger.info(f"Itens selecionados pelo usuário: {escolhas}")

    if escolhas.lower() == 'tudo':
        aguardar_conexao_net()
        itens_a_baixar = todos_itens
    else:
        try:
            indices = [int(i.strip()) for i in escolhas.split(',') if i.strip().isdigit()]
        except ValueError:
            logger.error("Entrada inválida. Finalizando.")
            ftp.quit()
            return

        itens_a_baixar = [todos_itens[i] for i in indices if 0 <= i < len(todos_itens)]

    for caminho_remoto, caminho_relativo in itens_a_baixar:
        aguardar_conexao_net()
        try:
            if '.' in os.path.basename(caminho_remoto):  # Arquivo
                local_path = os.path.join(LOCAL_BASE_DIR, caminho_relativo)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f"RETR {caminho_remoto}", f.write)
                logger.info(f"Arquivo baixado: {caminho_remoto}")
                logger.info(f"MD5: {calculate_md5(local_path)}")
            else:
                logger.info(f"Iniciando download da pasta: {caminho_remoto}")
                subitens = listar_itens_flat(ftp, caminho_remoto)
                for sub_remoto, sub_relativo in subitens:
                    if '.' not in os.path.basename(sub_remoto):
                        continue

                    caminho_raiz = os.path.basename(caminho_remoto.rstrip('/'))
                    caminho_completo_relativo = os.path.join(caminho_raiz, sub_relativo)

                    local_path = os.path.join(LOCAL_BASE_DIR, caminho_completo_relativo)
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, 'wb') as f:
                        ftp.retrbinary(f"RETR {sub_remoto}", f.write)
                    logger.info(f"Arquivo baixado: {sub_remoto}")
                    logger.info(f"MD5: {calculate_md5(local_path)}")
        except Exception as e:
            logger.error(f"Erro ao baixar {caminho_remoto}: {e}")

    ftp.quit()
    logger.info("Download finalizado e conexão encerrada.")

if __name__ == "__main__":
    geral()

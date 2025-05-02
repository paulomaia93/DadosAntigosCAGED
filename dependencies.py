import logging
import subprocess
import sys

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

def instalar_dependencias():
    pacotes = ['py7zr','python-dotenv']

    for pacote in pacotes:
        try:
            __import__(pacote)
            logger.info(f'Pacote "{pacote}" já está instalado.')
        except ImportError:
            logger.warning(f'Pacote "{pacote}" não encontrado. Instalando...')
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
                logger.info(f'Pacote "{pacote}" instalado com sucesso.')
            except subprocess.CalledProcessError as e:
                logger.error(f'Erro ao instalar o pacote "{pacote}": {e}')

if __name__ == "__main__":
    instalar_dependencias()
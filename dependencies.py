import logging
import subprocess
import sys

# Configuração do logger principal da aplicação
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Verifica se o logger já tem handlers configurados para evitar duplicações
if not logger.handlers:
    # Define o formato dos logs
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )

    # Handler para exibir logs no terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Handler para salvar logs em arquivo
    file_handler = logging.FileHandler("app.log", encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Adiciona os handlers ao logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

# Evita propagação de logs para o logger raiz do Python
logger.propagate = False

def instalar_dependencias():
    # Lista de pacotes necessários para a aplicação
    pacotes = [
        'google-cloud-bigquery',
        'py7zr',
        'python-dotenv',
        'psycopg2-binary',
        'apscheduler',
        'openpyxl'
    ]

    # Verifica e instala cada pacote, se necessário
    for pacote in pacotes:
        try:
            # Tenta importar o pacote para verificar se já está instalado
            __import__(pacote)
            logger.info(f'Pacote "{pacote}" já está instalado.')
        except ImportError:
            # Caso o pacote não esteja disponível, tenta instalar com pip
            logger.warning(f'Pacote "{pacote}" não encontrado. Instalando...')
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
                logger.info(f'Pacote "{pacote}" instalado com sucesso.')
            except subprocess.CalledProcessError as e:
                # Registra erro se a instalação falhar
                logger.error(f'Erro ao instalar o pacote "{pacote}": {e}')

# Executa a função principal quando o script for executado diretamente
if __name__ == "__main__":
    instalar_dependencias()
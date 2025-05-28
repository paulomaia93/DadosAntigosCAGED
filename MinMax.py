import csv
import os
import logging
from dotenv import load_dotenv

# Carrega variáveis de ambiente a partir do arquivo .env
load_dotenv()

# Configuração do logger principal da aplicação
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Evita duplicidade de handlers
if not logger.handlers:
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )

    # Saída para o console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Saída para o arquivo de log
    file_handler = logging.FileHandler("app.log", encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Adiciona os dois handlers ao logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

# Impede propagação para loggers de nível superior
logger.propagate = False

# Lê a variável de ambiente com os anos informados
anos_inter = os.getenv("ANOS")

def gerar_intervalos(anos_str):
    try:
        # Converte string dos anos para tupla de inteiros
        anos = tuple(map(int, anos_str.strip("()").split(", ")))
        logger.info(f'Anos extraídos: {anos}')
    except ValueError as e:
        # Log de erro se houver falha na conversão
        logger.error(f'Erro ao processar os anos: {e}')
        return

    logger.info('Início da geração dos intervalos.')

    # Determina os limites do intervalo
    ano_minimo = min(anos)
    ano_maximo = max(anos)
    
    logger.info(f'Menor ano identificado: {ano_minimo}')
    logger.info(f'Maior ano identificado: {ano_maximo}')

    # Geração das datas de início e fim com base nos anos
    if ano_minimo == ano_maximo:
        data_inicio = f"01/01/{ano_minimo}"
        data_fim = f"31/12/{ano_maximo}"
        logger.info(f'Único ano encontrado. Data início e fim: {data_inicio}')
    else:
        data_inicio = f"01/01/{ano_minimo}"
        data_fim = f"31/12/{ano_maximo}"
        logger.info(f'Datas geradas para o intervalo: {data_inicio} - {data_fim}')

    # Criação do diretório 'Dimensões' se não existir
    pasta_dimensoes = os.path.join(os.getcwd(), 'Dimensões')
    
    if not os.path.exists(pasta_dimensoes):
        os.makedirs(pasta_dimensoes)
        logger.info('Pasta "Dimensões" criada com sucesso.')

    # Caminho final do arquivo CSV
    caminho_arquivo = os.path.join(pasta_dimensoes, 'intervalos.csv')

    try:
        # Escrita das datas no arquivo CSV
        with open(caminho_arquivo, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['data_inicio', 'data_fim'])
            writer.writerow([data_inicio, data_fim])
        logger.info(f'Arquivo CSV "intervalos.csv" gerado com sucesso em {caminho_arquivo}.')
    except Exception as e:
        # Log de erro em caso de falha na escrita do CSV
        logger.error(f'Erro ao gerar o arquivo CSV: {e}')
  
# Execução da função principal se o script for executado diretamente
if __name__ == "__main__":
    gerar_intervalos(anos_inter)
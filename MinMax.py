import csv
import os
import logging
from dotenv import load_dotenv

load_dotenv()

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

anos_inter = os.getenv("ANOS")

def gerar_intervalos(anos_str):
    try:
        anos = tuple(map(int, anos_str.strip("()").split(", ")))
        logger.info(f'Anos extraídos: {anos}')
    except ValueError as e:
        logger.error(f'Erro ao processar os anos: {e}')
        return

    logger.info('Início da geração dos intervalos.')

    ano_minimo = min(anos)
    ano_maximo = max(anos)
    
    logger.info(f'Menor ano identificado: {ano_minimo}')
    logger.info(f'Maior ano identificado: {ano_maximo}')

    if ano_minimo == ano_maximo:
        data_inicio = f"01/01/{ano_minimo}"
        data_fim = f"31/12/{ano_maximo}"
        logger.info(f'Único ano encontrado. Data início e fim: {data_inicio}')
    else:
        data_inicio = f"01/01/{ano_minimo}"
        data_fim = f"31/12/{ano_maximo}"
        logger.info(f'Datas geradas para o intervalo: {data_inicio} - {data_fim}')

    pasta_dimensoes = os.path.join(os.getcwd(), 'Dimensões')
    
    if not os.path.exists(pasta_dimensoes):
        os.makedirs(pasta_dimensoes)
        logger.info('Pasta "Dimensões" criada com sucesso.')

    caminho_arquivo = os.path.join(pasta_dimensoes, 'intervalos.csv')

    try:
        with open(caminho_arquivo, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['data_inicio', 'data_fim'])
            writer.writerow([data_inicio, data_fim])
        logger.info(f'Arquivo CSV "intervalos.csv" gerado com sucesso em {caminho_arquivo}.')
    except Exception as e:
        logger.error(f'Erro ao gerar o arquivo CSV: {e}')
  
if __name__ == "__main__":
    gerar_intervalos(anos_inter)
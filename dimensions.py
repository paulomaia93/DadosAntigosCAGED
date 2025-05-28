import os
import logging
from google.cloud import bigquery
import csv
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do logger para registrar execuções em console e arquivo
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

# Define o diretório de destino dos arquivos CSV
pasta_destino = "Dimensões"
output_base_path = os.path.join(os.getcwd(), pasta_destino)

# Cria a pasta de destino se não existir
if not os.path.exists(output_base_path):
    os.makedirs(output_base_path)
    logger.info(f"A pasta '{pasta_destino}' foi criada em: {output_base_path}")
else:
    logger.info(f"A pasta '{pasta_destino}' já existe em: {output_base_path}")

# Configura as credenciais do Google Cloud a partir do arquivo .env
google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path
    logger.info(f"Credenciais carregadas de: {google_credentials_path}")
else:
    logger.error("A variável de ambiente GOOGLE_APPLICATION_CREDENTIALS não foi definida no arquivo .env")
    exit(1)

# Instancia o cliente do BigQuery
client = bigquery.Client()

# Define as tabelas que serão exportadas e os nomes dos respectivos arquivos
tabelas_e_arquivos = [
    ("`basedosdados.br_bd_diretorios_brasil.cbo_2002`", "br_bd_diretorios_brasil_cbo_2002.csv"),
    ("`basedosdados.br_bd_diretorios_brasil.cnae_1`", "br_bd_diretorios_brasil_cnae_1.csv"),
    ("`basedosdados.br_bd_diretorios_brasil.cnae_2`", "br_bd_diretorios_brasil_cnae_2.csv"),
    ("`basedosdados.br_bd_diretorios_brasil.municipio`", "br_bd_diretorios_brasil_municipio.csv"),
    ("`basedosdados.br_bd_diretorios_brasil.uf`", "br_bd_diretorios_brasil_uf.csv")
]

# Função responsável por executar a consulta no BigQuery e salvar o resultado em CSV
def export_to_csv(tabela, output_file):
    logger.info(f"Iniciando consulta para a tabela: {tabela}")
    query = f"SELECT * FROM {tabela}"
    query_job = client.query(query)
    
    results = query_job.result()

    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        headers = [field.name for field in results.schema]
        writer.writerow(headers)

        for row in results:
            writer.writerow([str(row[field.name]) for field in results.schema])

    logger.info(f"Arquivo CSV gerado com sucesso: {output_file}")

# Executa a exportação para cada tabela definida
for tabela, arquivo in tabelas_e_arquivos:
    output_file = os.path.join(output_base_path, arquivo)
    
    export_to_csv(tabela, output_file)
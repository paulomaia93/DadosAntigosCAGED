import os
import logging
from google.cloud import bigquery
import csv
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

pasta_destino = "DadosSQL"

output_base_path = os.path.join(os.getcwd(), pasta_destino)

if not os.path.exists(output_base_path):
    os.makedirs(output_base_path)
    logger.info(f"A pasta '{pasta_destino}' foi criada em: {output_base_path}")
else:
    logger.info(f"A pasta '{pasta_destino}' já existe em: {output_base_path}")

google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path
    logger.info(f"Credenciais carregadas de: {google_credentials_path}")
else:
    logger.error("A variável de ambiente GOOGLE_APPLICATION_CREDENTIALS não foi definida no arquivo .env")
    exit(1)

client = bigquery.Client()

tabelas_e_arquivos = [
    ("`basedosdados.br_me_caged.microdados_antigos`", "DataBase.csv")   
]

anos = os.getenv("ANOS")

def export_to_csv(tabela, output_file):
    logger.info(f"Iniciando consulta para a tabela: {tabela}")

    query = f"""
    SELECT
        ano AS Competencia_Declarada_Ano,
        mes AS Competencia_Declarada_Mes,
        id_municipio_6 AS Municipio,
        admitidos_desligados AS Admitidos_Desligados,
        cbo_2002 AS CBO_2002_Ocupacao,
        cnae_2_subclasse AS CNAE_2_SubClasse,
        salario_mensal AS Salario_Mensal,
        idade AS Idade,
        sexo AS Sexo
    FROM
        {tabela}
    WHERE
        ano IN {anos}
    ;
    """

    query_job = client.query(query)
    
    results = query_job.result()

    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        headers = [field.name for field in results.schema]
        writer.writerow(headers)

        for row in results:
            writer.writerow([str(row[field.name]) for field in results.schema])

    logger.info(f"Arquivo CSV gerado com sucesso: {output_file}")

for tabela, arquivo in tabelas_e_arquivos:
    output_file = os.path.join(output_base_path, arquivo)

    export_to_csv(tabela, output_file)
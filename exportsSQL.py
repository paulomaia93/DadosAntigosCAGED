import os
import logging
from google.cloud import bigquery
import csv
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do logger para registrar logs em console e arquivo
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

# Impede propagação duplicada de logs
logger.propagate = False

# Define e cria diretório de saída para os arquivos CSV
pasta_destino = "DadosSQL"
output_base_path = os.path.join(os.getcwd(), pasta_destino)

if not os.path.exists(output_base_path):
    os.makedirs(output_base_path)
    logger.info(f"A pasta '{pasta_destino}' foi criada em: {output_base_path}")
else:
    logger.info(f"A pasta '{pasta_destino}' já existe em: {output_base_path}")

# Configura credenciais do Google Cloud a partir do .env
google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path
    logger.info(f"Credenciais carregadas de: {google_credentials_path}")
else:
    logger.error("A variável de ambiente GOOGLE_APPLICATION_CREDENTIALS não foi definida no arquivo .env")
    exit(1)

# Inicializa cliente do BigQuery
client = bigquery.Client()

# Define as tabelas a serem consultadas e os nomes dos arquivos de saída
tabelas_e_arquivos = [
    ("`basedosdados.br_me_caged.microdados_antigos`", "DataBase.csv")   
]

# Obtém os anos definidos no .env para filtrar os dados
anos = os.getenv("ANOS")

# Função para exportar dados da tabela do BigQuery para arquivo CSV
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

    # Executa a consulta no BigQuery
    query_job = client.query(query)
    results = query_job.result()

    # Gera arquivo CSV com os resultados
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        headers = [field.name for field in results.schema]
        writer.writerow(headers)

        for row in results:
            writer.writerow([str(row[field.name]) for field in results.schema])

    logger.info(f"Arquivo CSV gerado com sucesso: {output_file}")

# Inicia o processo de exportação para cada tabela especificada
for tabela, arquivo in tabelas_e_arquivos:
    output_file = os.path.join(output_base_path, arquivo)
    
    export_to_csv(tabela, output_file)
import subprocess
import os
import datetime
import logging

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

logger.info("ELT DOS DADOS CAGED")
logger.info("=" * 60)

def executar_script(nome_arquivo):

    caminho_absoluto = os.path.join(os.path.dirname(__file__), nome_arquivo)

    if os.path.isfile(caminho_absoluto):
        logger.info(f"Iniciando execução do script: {nome_arquivo}")
        try:
            subprocess.run(['python', caminho_absoluto], check=True)
            logger.info(f"Script '{nome_arquivo}' executado com sucesso.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar o script '{nome_arquivo}': {e}")
    else:
        logger.warning(f"O arquivo '{nome_arquivo}' não foi encontrado no diretório.")

def formatar_duracao(tempo_segundos):

    horas = int(tempo_segundos // 3600)
    minutos = int((tempo_segundos % 3600) // 60)
    segundos = int(tempo_segundos % 60)
    return f"{horas:02}:{minutos:02}:{segundos:02}"

def executar_funcoes(sequencia_funcoes):

    tempo_total = 0

    for func in sequencia_funcoes:
        inicio = datetime.datetime.now()
        func()
        fim = datetime.datetime.now()
        
        duracao_segundos = (fim - inicio).total_seconds()
        tempo_total += duracao_segundos
        
        duracao_formatada = formatar_duracao(duracao_segundos)
        log_message = f"Execução em: {inicio.strftime('%d/%m/%Y %H:%M:%S')} | Duração: {duracao_formatada}"
        logger.info(log_message)
        logger.info("-" * 60)

    tempo_total_formatado = formatar_duracao(tempo_total)

    logger.info(f"Fim do agendamento em: {fim.strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info(f"Tempo total de execução de todas as tabelas: {tempo_total_formatado}")
    logger.info(f"-- Aguardando o próximo agendamento --")
    logger.info("+" * 60)

sequencia_funcoes = [
    lambda: executar_script('dependencies.py'),
    lambda: executar_script('exportsSQL.py'),
    lambda: executar_script('dimensions.py'),
    lambda: executar_script('MinMax.py')
]

executar_funcoes(sequencia_funcoes)



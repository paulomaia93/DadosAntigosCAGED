# Use a imagem base do Python
FROM python:3.13-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante dos arquivos da aplicação para o diretório de trabalho
COPY . .

RUN ln -snf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && echo "America/Sao_Paulo" > /etc/timezone

# Defina o comando padrão para executar a aplicação
CMD ["python", "main.py"]
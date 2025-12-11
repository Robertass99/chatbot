# Dockerfile para Rick Sanchez Chatbot Backend
# Usa Python 3.11 slim para imagem otimizada

FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivo de requirements primeiro (melhor cache de camadas)
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do backend
COPY . .

# Expor porta (padrão 80, pode ser sobrescrita)
EXPOSE 80

# Variáveis de ambiente padrão (sobrescrever em produção)
ENV PORT=80
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health')"

# Comando para iniciar servidor
# Em produção, ajustar workers conforme necessário
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT} --workers 1

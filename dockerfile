FROM python:3.9

WORKDIR /app

# Instala dependências primeiro (cache mais eficiente)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto dos arquivos
COPY . .

# Garante que o .env seja ignorado (opcional, mas recomendado)
RUN echo ".env" >> .dockerignore

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
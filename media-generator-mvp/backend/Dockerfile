# Backend Dockerfile
FROM python:3.9-slim

# Imposta la directory di lavoro
WORKDIR /app

# Installa le dipendenze di sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copia i file dei requisiti
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice sorgente
COPY . .

# Crea le directory necessarie
RUN mkdir -p data/books data/uploads data/outputs logs

# Copia i file di configurazione
COPY config.yaml .

# Espone la porta
EXPOSE 8000

# Comando di avvio
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

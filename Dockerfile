# Usa l'immagine ufficiale di Python 3.12.9 con slim
FROM python:3.12.9-slim-bookworm

# Installa FFmpeg e aggiorna i pacchetti di sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libmagic1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Imposta la cartella di lavoro nel container
WORKDIR /app

# Copia i file del progetto dentro il container
COPY . .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Imposta la variabile d'ambiente XDG_CACHE_HOME per evitare problemi con la cache
ENV XDG_CACHE_HOME=/app/yt-cache

# Crea un utente non-root per eseguire l'applicazione
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/config && \
    chown -R appuser:appuser /app/config

USER appuser

# Comando per avviare il programma
CMD ["python", "-m", "src.main"]

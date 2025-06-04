# SpotifyDl

Un'applicazione Python per scaricare playlist, album e brani da Spotify come file MP3.

## Caratteristiche

- **Download Multi-thread**: Scarica più brani contemporaneamente configurando il numero di thread
- **Qualità Personalizzabile**: Configura la qualità audio desiderata
- **Supporto Metadati**: Ogni file MP3 viene salvato con i metadati corretti (titolo, artista, album, ecc.)
- **Aggiornamento Playlist**: Scarica automaticamente solo i nuovi brani aggiunti alle playlist

## Requisiti

- Credenziali API Spotify (Client ID e Client Secret)
  [spotify.com](https://developer.spotify.com/)
- Connessione Internet
- Python 3.8 o superiore
- FFmpeg

## Installazione

1. Clona il repository:
```bash
git clone https://github.com/tuousername/SpotifyDl.git
cd SpotifyDl
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

3. Installa FFmpeg:

**Windows**:
- Scarica FFmpeg da https://ffmpeg.org/download.html
- Aggiungi FFmpeg al PATH di sistema

**macOS**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
sudo apt update
sudo apt install ffmpeg
```

4. Esegui l'applicazione:
```bash
python -m src.main
```

## Configurazione

Al primo avvio, l'applicazione ti chiederà di inserire:
- SPOTIFY_CLIENT_ID
- SPOTIFY_CLIENT_SECRET
- MAX_THREADS (numero di download simultanei)
- PREFERRED_QUALITY (qualità audio preferita)

## Utilizzo

L'applicazione supporta i seguenti comandi:

- `download`: Scarica una playlist, album o brano da Spotify
- `update <numero>`: Aggiorna una playlist specifica o tutte le playlist
- `list`: Mostra la lista delle playlist scaricate
- `addmeta`: Aggiunge i metadati di un brano Spotify a un file audio
- `settings`: Modifica le impostazioni dell'applicazione
- `help`: Mostra la lista dei comandi disponibili
- `exit`: Chiude l'applicazione

## Docker

Per eseguire l'applicazione con Docker:

1. Costruisci l'immagine:
```bash
docker build -t spotifydl .
```

2. Esegui il container:
```bash
docker run -it spotifydl
```

## Struttura del Progetto

```
SpotifyDl/
├── src/
│   ├── core/
│   │   ├── spotify.py
│   │   ├── downloader.py
│   │   └── metadata.py
│   ├── utils/
│   │   ├── config.py
│   │   └── logger.py
│   ├── commands/
│   │   └── commands.py
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Note

- L'applicazione utilizza YouTube per il download dei brani
- I file vengono salvati in formato MP3
- I metadati vengono estratti direttamente da Spotify
- La cache di YouTube viene salvata nella cartella `yt-cache`

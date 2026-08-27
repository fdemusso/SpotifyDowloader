# 🎵 SpotifyDl

A Python CLI tool that downloads Spotify playlists, albums, and tracks as MP3 files — with metadata, multi-threading, and automatic playlist updates.

Built for personal use, offline listening, and learning how to work with the Spotify API, YouTube download pipelines, and audio metadata.

---

## ✨ Features

- **Multi-threaded downloads** — Configure how many tracks to download in parallel
- **Customizable audio quality** — Choose your preferred bitrate
- **Full metadata support** — Title, artist, album, cover art, and more pulled directly from Spotify
- **Smart playlist updates** — Only fetch new tracks added since your last download
- **Interactive CLI** — Simple commands to manage downloads, settings, and metadata
- **Docker-ready** — Run it in a container with a single command

---

## 📦 Requirements

- Spotify API credentials (Client ID and Client Secret) — get them at [developer.spotify.com](https://developer.spotify.com/)
- Internet connection
- Python 3.8+
- FFmpeg

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/fdemusso/SpotifyDowloader.git
cd SpotifyDl
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Windows**  
- Download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)  
- Add FFmpeg to your system PATH

**macOS**

```bash
brew install ffmpeg
```

**Linux**

```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. Run the app

```bash
python -m src.main
```

---

## ⚙️ Configuration

On first launch, you'll be prompted to set:

- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `MAX_THREADS` — number of parallel downloads
- `PREFERRED_QUALITY` — audio quality (e.g., 128, 192, 320 kbps)

These settings are saved locally and reused on subsequent runs.

---

## 🧭 Usage

Once inside the CLI, you can use:

- `download` — Download a playlist, album, or track from Spotify
- `update <number>` — Update a specific playlist (or all if no number is given)
- `list` — Show your downloaded playlists
- `addmeta` — Add Spotify metadata to an existing audio file
- `settings` — Change your configuration
- `help` — Show available commands
- `exit` — Quit the app

---

## 🐳 Docker

Run SpotifyDl in a container:

```bash
# Build the image
docker build -t spotifydl .

# Run the container
docker run -it spotifydl
```

---

## 🗂️ Project Structure

```text
SpotifyDl/
├── src/
│   ├── core/
│   │   ├── spotify.py      # Spotify API interactions
│   │   ├── downloader.py   # YouTube download logic
│   │   └── metadata.py     # MP3 tagging
│   ├── utils/
│   │   ├── config.py       # Settings management
│   │   └── logger.py       # Logging utilities
│   ├── commands/
│   │   └── commands.py     # CLI commands
│   └── main.py             # Entry point
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 📝 Notes

- Tracks are downloaded via YouTube and converted to MP3
- Metadata (title, artist, album, cover) comes from Spotify
- YouTube cache is stored in the `yt-cache` folder
- Downloaded files are organized by playlist/album

---

## ⚠️ Disclaimer

This project is for **educational and personal use only**.  
The developers are not responsible for any misuse of this software or for any copyright violations committed by users.  

Please ensure that you comply with **Spotify's Terms of Service** and all applicable laws in your jurisdiction.  
Downloading copyrighted material without permission may be illegal.  

**Use at your own risk.**

---

Made with ❤️ by [@fdemusso](https://github.com/fdemusso)

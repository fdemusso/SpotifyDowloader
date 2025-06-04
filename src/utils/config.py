import os
from pathlib import Path
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Inizializza colorama
init()

# Variabili globali riguardanti la cartella dell'applicazione
APP_NAME = "SpotifyDl"
DEFAULT_ENV_NAME = ".env"
CONFIG_FOLDER = os.path.join(os.path.expanduser("~"), f".{APP_NAME}")
ENV_PATH = os.path.join(CONFIG_FOLDER, DEFAULT_ENV_NAME)

def ensure_config_directory():
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)
        print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Configuration folder created: {CONFIG_FOLDER}")

def create_env_file():
    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + ".env file not found. Creating a new one.")
    spotify_client_id = input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Enter SPOTIFY_CLIENT_ID: ").strip()
    spotify_client_secret = input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Enter SPOTIFY_CLIENT_SECRET: ").strip()
    max_threads = input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Enter MAX_THREADS: ").strip()
    preferred_quality = input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Enter PREFERRED_QUALITY: ").strip()
    cache_yt = os.path.join(CONFIG_FOLDER, "yt-cache")

    env_content = f"""
SPOTIFY_CLIENT_ID={spotify_client_id}
SPOTIFY_CLIENT_SECRET={spotify_client_secret}
MAX_THREADS={max_threads}
PREFERRED_QUALITY={preferred_quality}
XDG_CACHE_HOME={cache_yt}
"""
    
    with open(ENV_PATH, "w") as f:
        f.write(env_content.strip())
    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f".env file created at {ENV_PATH}")

def load_config():
    ensure_config_directory()
    if os.path.exists(ENV_PATH):
        print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"File .env trovato in {ENV_PATH}. Loading...")
    else:
        create_env_file()
    
    load_dotenv(ENV_PATH, override=True)
    return {
        'client_id': os.getenv("SPOTIFY_CLIENT_ID"),
        'client_secret': os.getenv("SPOTIFY_CLIENT_SECRET"),
        'max_threads': int(os.getenv("MAX_THREADS", "4")),
        'preferred_quality': os.getenv("PREFERRED_QUALITY", "192")
    } 
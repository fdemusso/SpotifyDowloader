import os
import uuid
import yt_dlp
from pathlib import Path
from src.utils.logger import log_error
from colorama import Fore, Style, init

# Inizializza colorama
init()

def search_youtube(query, output_folder):
    """Cerca un video su YouTube e restituisce l'URL."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'default_search': 'ytsearch',
        'format': 'bestaudio/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if result and 'entries' in result and result['entries']:
                return result['entries'][0]['url']
    except Exception as e:
        log_error(f"Error searching YouTube for {query}: {e}", output_folder)
    
    return None

def download_track(track, output_folder, in_processing, track_already_downloaded, preferred_quality):
    """Scarica il brano da YouTube e restituisce il percorso del file temporaneo."""
    key = (track['name'].strip().lower(), track['artists'].strip().lower())
    if key in in_processing or track_already_downloaded(track, output_folder):
        print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Skipping, already exists or in processing: {track['name']} - {track['artists']}")
        return None

    in_processing.add(key)
    query = f"intitle:{track['name']} \"{track['artists']}\""
    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Searching: {query}")
    youtube_url = search_youtube(query, output_folder)
    if not youtube_url:
        log_error(f"Not found on YouTube: {query}", output_folder)
        in_processing.remove(key)
        return None

    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Downloading from: {youtube_url}")
    temp_name = uuid.uuid4().hex
    temp_output_path = Path(output_folder) / temp_name
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': "mp3",
            'preferredquality': preferred_quality,
        }],
        'outtmpl': str(temp_output_path),
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
    except Exception as e:
        log_error(f"Download error for {track['name']}: {e}", output_folder)
        in_processing.remove(key)
        return None

    temp_file = str(temp_output_path) + ".mp3"
    if not os.path.exists(temp_file):
        log_error(f"Temporary file not found for {track['name']}", output_folder)
        in_processing.remove(key)
        return None

    return temp_file 
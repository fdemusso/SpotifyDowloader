import os
import re
import time
import threading
from pathlib import Path
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from src.utils.logger import log_error
from colorama import Fore, Style, init

# Inizializza colorama
init()

file_lock = threading.Lock()

def add_metadata_to_file(temp_file, track_info, output_folder):
    """Aggiunge i metadati al file audio."""
    try:
        audio = MP3(temp_file, ID3=EasyID3)
        audio['title'] = track_info['name']
        audio['artist'] = track_info['artists']
        audio['album'] = track_info['album']
        if track_info['track_number']:
            audio['tracknumber'] = str(track_info['track_number'])
        audio.save()
        del audio
        return True
    except Exception as e:
        log_error(f"Error adding metadata for {track_info['name']}: {e}", output_folder)
        return False

def rename_file(temp_file, track_info, output_folder):
    """Rinomina il file temporaneo in base al titolo del brano."""
    final_name = re.sub(r'[\/:*?."<>|]', " ", track_info['name']).strip().rstrip('.')
    final_output_path = Path(output_folder) / final_name
    final_file = str(final_output_path) + ".mp3"

    max_retries = 5
    for attempt in range(max_retries):
        try:
            with file_lock:
                if not os.path.exists(final_file):
                    os.rename(temp_file, final_file)
                else:
                    alt_final_name = f"{final_name} - {track_info['artists']}"
                    alt_final_name = re.sub(r'[\/:*?."<>|]', " ", alt_final_name).strip().rstrip('.')
                    alt_final_output_path = Path(output_folder) / alt_final_name
                    alt_final_file = str(alt_final_output_path) + ".mp3"
                    if not os.path.exists(alt_final_file):
                        os.rename(temp_file, alt_final_file)
                        final_file = alt_final_file
                    else:
                        i = 1
                        while os.path.exists(f"{final_output_path}-{i}.mp3"):
                            i += 1
                        final_file = f"{final_output_path}-{i}.mp3"
                        os.rename(temp_file, final_file)
            break
        except OSError as e:
            if hasattr(e, "winerror") and e.winerror == 32:
                print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"File in use, retrying rename for {final_file} (attempt {attempt+1}/{max_retries})")
                time.sleep(0.5)
            else:
                raise e
    else:
        print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Failed to rename {temp_file} after {max_retries} attempts.")
        return None

    try:
        if os.path.exists(final_file):
            audio = MP3(final_file, ID3=EasyID3)
            metadata_title = audio.get('title', [final_name])[0]
            sanitized_title = re.sub(r'[\/:*?."<>|]', " ", metadata_title).strip().rstrip('.')
            current_name = Path(final_file).stem
            if sanitized_title != current_name:
                new_final_output_path = Path(output_folder) / sanitized_title
                new_final_file = str(new_final_output_path) + ".mp3"
                if not os.path.exists(new_final_file):
                    os.rename(final_file, new_final_file)
                    final_file = new_final_file
                else:
                    print(f"Post-rename target already exists: {new_final_file}. Keeping original file.")
    except Exception as e:
        print(f"Error in post-renaming check for {track_info['name']}: {e}")
        error_file = os.path.join(output_folder, "Error.txt")
        with open(error_file, 'a') as file:
            file.write(f"[ERROR] Post-renaming check for {track_info['name']}: {e}\n")

    return final_file

def get_file_metadata(file_path):
    """Ottiene i metadati di un file audio."""
    try:
        audio = MP3(file_path, ID3=EasyID3)
        title = audio.get('title', [''])[0]
        artist = audio.get('artist', [''])[0]
        return title, artist
    except Exception:
        return None, None

def track_already_downloaded(track, output_folder):
    """Controlla se il brano è già stato scaricato."""
    final_name = re.sub(r'[\/:*?."<>|]', " ", track['name']).strip().rstrip('.')
    final_output_path = Path(output_folder) / final_name
    final_file = str(final_output_path) + ".mp3"

    if os.path.exists(final_file):
        return True

    alt_final_name = f"{final_name} - {track['artists']}"
    alt_final_name = re.sub(r'[\/:*?."<>|]', " ", alt_final_name).strip().rstrip('.')
    alt_final_output_path = Path(output_folder) / alt_final_name
    alt_final_file = str(alt_final_output_path) + ".mp3"

    if os.path.exists(alt_final_file):
        return True

    i = 1
    while os.path.exists(f"{final_output_path}-{i}.mp3"):
        i += 1

    return False 
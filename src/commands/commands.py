import os
import shutil
from colorama import Fore, Style, init
from src.utils.config import CONFIG_FOLDER, create_env_file
from src.utils.logger import has_content
from src.core.spotify import get_spotify_client, get_spotify_playlist_tracks, get_spotify_album_tracks, get_spotify_single_track
from src.core.metadata import get_file_metadata

# Inizializza colorama
init()

DATA_FILE = os.path.join(CONFIG_FOLDER, "data.dat")

def clear_terminal():
    """Pulisce il terminale a seconda del sistema operativo."""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def check_ffmpeg():
    """Controlla se FFmpeg è installato correttamente nel sistema."""
    if shutil.which("ffmpeg") is None:
        print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "FFmpeg is not installed or not in the PATH.")
        print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Download it from: https://ffmpeg.org/download.html and install it.")
        input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "\nPress Enter to exit...")
        return False
    else:
        print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "FFmpeg is installed in the PATH.")
        clear_terminal()
        return True

def load_entries():
    """Legge tutte le righe del file e salva spotify_url e output_folder in due liste."""
    spotify_urls = []
    output_folders = []

    if not os.path.exists(DATA_FILE):
        return spotify_urls, output_folders

    with open(DATA_FILE, "r") as file:
        for line in file:
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                spotify_urls.append(parts[0])
                output_folders.append(parts[1])

    return spotify_urls, output_folders

def clean_entries(client_id, client_secret):
    """Rimuove dal file data.dat le voci non valide."""
    spotify_urls, output_folders = load_entries()
    sp = get_spotify_client(client_id, client_secret)
    valid_entries = []
    
    for url, folder in zip(spotify_urls, output_folders):
        if not os.path.exists(folder):
            continue
        
        playlist_id = None
        if "playlist/" in url:
            playlist_id = url.split("playlist/")[1].split('?')[0]
        
        if not playlist_id:
            print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"The link is no longer valid for the path: {folder}")
            continue
        
        try:
            sp.playlist(playlist_id)
        except Exception:
            print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"The link is no longer valid for the directory: {folder}")
            continue
        
        valid_entries.append((url, folder))
    
    with open(DATA_FILE, "w") as file:
        for url, folder in valid_entries:
            file.write(f"{url} {folder}\n")
    
    return valid_entries

def save_entry(spotify_url, output_folder):
    """Scrive spotify_url e output_folder nel file data.dat."""
    with open(DATA_FILE, "a") as file:
        file.write(f"{spotify_url} {output_folder}\n")

def check_playlist_files(playlist_url, folder, client_id, client_secret):
    """Controlla se i file della cartella corrispondono ai brani della playlist."""
    sp = get_spotify_client(client_id, client_secret)
    playlist_tracks_dict = get_spotify_playlist_tracks(playlist_url, 0, sp)
    found_tracks_lower = set()
    
    for file in os.listdir(folder):
        if file.endswith(".mp3"):
            file_path = os.path.join(folder, file)
            track_title, track_artist = get_file_metadata(file_path)
            
            if track_title:
                track_title_lower = track_title.lower()
                match = next((track for track in playlist_tracks_dict 
                            if track['name'].lower() == track_title_lower and 
                            track['artists'].lower() == track_artist.lower()), None)
                
                if match:
                    found_tracks_lower.add(track_title_lower)
                else:
                    choice = input(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"The song '{file}' is not in the playlist. Do you want to delete it? (y/n): ").strip().lower()
                    if choice == "y":
                        os.remove(file_path)
                        print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Song '{file}' deleted.")
                        clear_terminal()
            else:
                print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"The file '{file}' does not have a title metadata. I recommend adding it.")

    missing_tracks = [track for track in playlist_tracks_dict if track['name'].lower() not in found_tracks_lower]

    if missing_tracks:
        print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "These songs are missing from the folder:")
        for track in missing_tracks:
            print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"   - {track['name']} by {track['artists']}")

def settings():
    """Gestisce le impostazioni dell'applicazione."""
    sure = input(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Are you sure you want to modify the settings? You will have to overwrite them all at once, including the Spotify ID and Secret.(y/n): ").lower()
    if sure == 'y':
        create_env_file()
    else:
        clear_terminal()

def get_list(client_id, client_secret):
    """Mostra la lista delle playlist scaricate."""
    result = has_content(DATA_FILE)
    if result == 1:
        sp = get_spotify_client(client_id, client_secret)
        links = []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split()
                    if parts:
                        links.append(parts[0])
        except FileNotFoundError:
            print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "File Not Found.")
            return

        ID = 1
        for link in links:
            if "playlist" in link:
                playlist_id = link.split("/")[-1].split("?")[0]
            else:
                raise ValueError("Invalid playlist URL")

            playlist_info = sp.playlist(playlist_id)
            playlist_name = playlist_info['name']
            print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"{ID}: {playlist_name}")
            ID += 1
    elif result == 3:
        print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "The playlist database is corrupted.")
    elif result == 0:
        print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "No playlist has been downloaded yet.")
    else:
        print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Unexpected error.") 
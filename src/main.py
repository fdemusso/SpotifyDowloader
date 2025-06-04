import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init
from src.utils.config import load_config
from src.utils.logger import has_content
from src.core.spotify import get_spotify_client, get_spotify_playlist_tracks, get_spotify_album_tracks, get_spotify_single_track
from src.core.downloader import download_track
from src.core.metadata import add_metadata_to_file, rename_file, track_already_downloaded
from src.commands.commands import (
    clear_terminal, check_ffmpeg, save_entry, check_playlist_files,
    settings, get_list, clean_entries, DATA_FILE
)

# Inizializza colorama
init()

# Set globale per tracce in elaborazione
in_processing = set()

def spotifydl(spotify_url, output_folder, flag, config):
    """Funzione principale per il download dei brani."""
    if not output_folder:
        output_folder = "/app/downloads"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    clear_terminal()
    
    sp = get_spotify_client(config['client_id'], config['client_secret'])
    
    if "playlist" in spotify_url:
        print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Extracting tracks from the playlist...")
        tracks = get_spotify_playlist_tracks(spotify_url, 1, sp)
        if flag == 1:
            save_entry(spotify_url, output_folder)
    elif "album" in spotify_url:
        print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Extracting tracks from the album...")
        tracks = get_spotify_album_tracks(spotify_url, sp)
    elif "track" in spotify_url:
        print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Extracting track information...")
        tracks = get_spotify_single_track(spotify_url, sp)
    else:
        print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Unsupported Spotify URL.")
        return

    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"The songs will be saved in: {output_folder}")

    # Deduplica le tracce
    unique_tracks = []
    seen = set()
    for track in tracks:
        key = (track['name'].strip().lower(), track['artists'].strip().lower())
        if key not in seen:
            unique_tracks.append(track)
            seen.add(key)
    tracks = unique_tracks

    print(Fore.GREEN + Style.BRIGHT + "\n=== PHASE 1: Download tracks ===" + Style.RESET_ALL)
    downloaded_items = []
    with ThreadPoolExecutor(config['max_threads']) as executor:
        future_to_track = {
            executor.submit(
                download_track, 
                track, 
                output_folder, 
                in_processing, 
                track_already_downloaded,
                config['preferred_quality']
            ): track for track in tracks
        }
        for future in as_completed(future_to_track):
            track = future_to_track[future]
            try:
                temp_file = future.result()
                if temp_file:
                    downloaded_items.append({"track": track, "temp_file": temp_file})
                    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Downloaded: {track['name']} - Temp file: {temp_file}")
            except Exception as e:
                print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Error downloading track {track['name']}: {e}")

    print(Fore.GREEN + Style.BRIGHT + "\n=== PHASE 2: Adding metadata ===" + Style.RESET_ALL)
    with ThreadPoolExecutor(config['max_threads']) as executor:
        future_to_item = {
            executor.submit(add_metadata_to_file, item["temp_file"], item["track"], output_folder): item 
            for item in downloaded_items
        }
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                success = future.result()
                if success:
                    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Metadata added for: {item['track']['name']}")
                else:
                    print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Error adding metadata for: {item['track']['name']}")
            except Exception as e:
                print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Error adding metadata for {item['track']['name']}: {e}")

    print(Fore.GREEN + Style.BRIGHT + "\n=== PHASE 3: Renaming files ===" + Style.RESET_ALL)
    with ThreadPoolExecutor(config['max_threads']) as executor:
        future_to_item = {
            executor.submit(rename_file, item["temp_file"], item["track"], output_folder): item 
            for item in downloaded_items
        }
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                final_path = future.result()
                print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"File for {item['track']['name']} renamed to: {final_path}")
            except Exception as e:
                print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Error renaming file for {item['track']['name']}: {e}")
            finally:
                key = (item['track']['name'].strip().lower(), item['track']['artists'].strip().lower())
                in_processing.discard(key)

    clear_terminal()

def update(playlist_number, config):
    """Aggiorna una o tutte le playlist."""
    if playlist_number == 0:
        result = has_content(DATA_FILE)
        if result == 1:
            valid_entries = clean_entries(config['client_id'], config['client_secret'])
            for url, folder in valid_entries:
                spotifydl(url, folder, 0, config)
                check_playlist_files(url, folder, config['client_id'], config['client_secret'])
                print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Update complete!")
            return
        elif result == 3:
            print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "The playlist database is corrupted.")
        elif result == 0:
            print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "No playlist has been downloaded yet.")
        else:
            print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Unexpected error.")
    else:
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                lines = file.readlines()
                
                if 1 <= playlist_number <= len(lines):
                    line = lines[playlist_number - 1].strip()
                    parts = line.split(" ", 1)
                    
                    if len(parts) == 2:
                        url, folder = parts
                        spotifydl(url, folder, 0, config)
                        check_playlist_files(url, folder, config['client_id'], config['client_secret'])

                        sp = get_spotify_client(config['client_id'], config['client_secret'])
                        if "playlist" in url:
                            playlist_id = url.split("/")[-1].split("?")[0]
                        else:
                            raise ValueError("Invalid playlist URL")
                        
                        playlist_info = sp.playlist(playlist_id)
                        playlist_name = playlist_info['name']
                        print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"{playlist_name} is now updated")
                        return
                    else:
                        print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"Line {playlist_number} does not contain data in the correct format.")
                else:
                    print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Invalid playlist number.")
        except FileNotFoundError:
            print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "File Not Found.")

def addmeta(config):
    """Aggiunge metadati a un file audio."""
    file_path = input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Enter the file path: ").strip()

    if (file_path.startswith('"') and file_path.endswith('"')) or (file_path.startswith("'") and file_path.endswith("'")):
        file_path = file_path[1:-1]

    if os.path.exists(file_path):
        spotify_url = input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Enter the Spotify link: ").strip()
        if (spotify_url.startswith('"') and spotify_url.endswith('"')) or (spotify_url.startswith("'") and spotify_url.endswith("'")):
            spotify_url = spotify_url[1:-1]

        directory_path = os.path.dirname(file_path)
        
        if "track" in spotify_url:
            print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Extracting track information...")
            sp = get_spotify_client(config['client_id'], config['client_secret'])
            track_info = get_spotify_single_track(spotify_url, sp)
            
            if add_metadata_to_file(file_path, track_info[0], directory_path):
                print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Metadata added successfully.")
            else:
                print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Failed to add metadata.")
        else:
            print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"{spotify_url} is not a valid track link.")
    else:
        print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"{file_path} does not exist")

def main():
    """Funzione principale del programma."""
    if not check_ffmpeg():
        return

    config = load_config()
    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Welcome to SpotifyDl. To see the available commands, type help")
    
    while True:
        rss = input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Enter command: ").strip().lower()
        
        if rss == "download":
            clear_terminal()
            spotify_url = input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Enter the Spotify link: ").strip()
            output_folder = input(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Enter the destination folder: ").strip()
            spotifydl(spotify_url, output_folder, 1, config)
            print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Download complete!")
            log_file = os.path.join(output_folder, "log.txt")
            if has_content(log_file) == 1:
                print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "An error may have occurred. Please check the log file. If there are incorrect or incomplete files, delete the file and enter the \\update command to attempt to repair the playlist. If the error persists, the track cannot be downloaded.")
        
        elif rss == "help":
            clear_terminal()
            commands = {
                "download": "Download any item from Spotify.",
                "update <Playlist Number>": "Update a specific playlist using the number obtained from the list. If you don't enter a number, all playlists will be updated automatically with the latest changes.",
                "list": "Show a list of the downloaded playlists",
                "addMeta": "Add the metadata of a Spotify song to a specific file",
                "settings": "edit the .env file",
                "exit": "Closes the program."
            }

            print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Comandi disponibili:")
            for command, description in commands.items():
                print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"- {command}: {description}")
        
        elif rss == "exit":
            return
            
        elif rss.startswith("update"):
            clear_terminal()
            parts = rss.split()
            if len(parts) == 1:
                update(0, config)
            elif len(parts) == 2 and parts[1].isdigit():
                playlist_number = int(parts[1])
                update(playlist_number, config)
            else:
                print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Invalid update command.")
                
        elif rss == "addmeta":
            clear_terminal()
            addmeta(config)
            
        elif rss == "settings":
            clear_terminal()
            settings()
            
        elif rss == "list":
            clear_terminal()
            get_list(config['client_id'], config['client_secret'])
            
        else:
            print(Fore.RED + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"{rss} is not a command")

if __name__ == "__main__":
    main() 
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from src.utils.config import CONFIG_FOLDER
import os
from colorama import Fore, Style, init

# Inizializza colorama
init()

DATA_FILE = os.path.join(CONFIG_FOLDER, "data.dat")

def get_spotify_client(client_id, client_secret):
    """Crea e restituisce un client Spotify autenticato."""
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_spotify_playlist_tracks(playlist_url, caller, sp):
    """Ottiene la lista dei brani da una playlist di Spotify."""
    if "playlist" in playlist_url:
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid playlist URL")

    tracks = []
    offset = 0
    playlist_info = sp.playlist(playlist_id)
    playlist_name = playlist_info['name']

    if caller == 1:
        print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"You're downloading from: {playlist_name}")

    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset)
        for item in results['items']:
            track = item['track']
            if track:
                name = track.get('name', 'Unknown Track')
                artists = ', '.join([artist.get('name', 'Unknown Artist') for artist in track.get('artists', [])])
                album = track.get('album', {}).get('name', 'Unknown Album')
                track_number = track.get('track_number', None)
                release_date = track['album'].get('release_date', 'Unknown Year')
                year = release_date.split("-")[0]
                tracks.append({
                    'name': name,
                    'artists': artists,
                    'album': album,
                    'track_number': track_number,
                    'year': year  
                })
            else:
                if caller == 1:
                    print(Fore.YELLOW + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + "Track is None, skipping...")

        if len(results['items']) < 100:
            break
        offset += 100

    return tracks

def get_spotify_album_tracks(album_url, sp):
    """Ottiene la lista dei brani da un album di Spotify."""
    if "album" in album_url:
        album_id = album_url.split("/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid album URL")

    tracks = []
    offset = 0
    album_info = sp.album(album_id)
    album_name = album_info['name']
    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"You're downloading from: {album_name}")

    while True:
        results = sp.album_tracks(album_id, offset=offset)
        for track in results['items']:
            name = track.get('name', 'Unknown Track')
            artists = ', '.join([artist.get('name', 'Unknown Artist') for artist in track.get('artists', [])])
            album = album_name
            track_number = track.get('track_number', None)
            release_date = album_info.get('release_date', 'Unknown Year')
            year = release_date.split("-")[0]
            tracks.append({
                'name': name,
                'artists': artists,
                'album': album,
                'track_number': track_number,
                'year': year  
            })

        if len(results['items']) < 50:
            break
        offset += 50

    return tracks

def get_spotify_single_track(track_url, sp):
    """Ottiene le informazioni di un singolo brano di Spotify."""
    if "track" in track_url:
        track_id = track_url.split("/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid track URL")

    track = sp.track(track_id)
    name = track.get('name', 'Unknown Track')
    artists = ', '.join([artist.get('name', 'Unknown Artist') for artist in track.get('artists', [])])
    album = track.get('album', {}).get('name', 'Unknown Album')
    track_number = track.get('track_number', None)
    release_date = track.get('album', {}).get('release_date', 'Unknown Year')
    year = release_date.split("-")[0]

    print(Fore.GREEN + Style.BRIGHT + "[SpotifyDl] " + Style.RESET_ALL + f"You're downloading track: {name}")

    return [{
        'name': name,
        'artists': artists,
        'album': album,
        'track_number': track_number,
        'year': year  
    }] 
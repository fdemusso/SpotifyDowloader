import os
import uuid
import yt_dlp
from pathlib import Path
from src.utils.logger import log_error

def search_youtube(query, output_folder):
    """Cerca un video su YouTube utilizzando yt-dlp."""
    ydl_opts = {
        'quiet': True,
        'default_search': 'ytsearch5',
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
        except Exception as e:
            log_error(f"YouTube search error for query '{query}': {e}", output_folder)
            info = None
        if info and 'entries' in info and len(info['entries']) > 0:
            for entry in info['entries']:
                webpage_url = entry.get('webpage_url')
                if webpage_url:
                    return webpage_url
    
    alt_query = query + " lyrics"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(alt_query, download=False)
        except Exception as e:
            log_error(f"YouTube search error for alternative query '{alt_query}': {e}", output_folder)
            return None
        if info and 'entries' in info and len(info['entries']) > 0:
            for entry in info['entries']:
                webpage_url = entry.get('webpage_url')
                if webpage_url:
                    return webpage_url
    return None

def download_track(track, output_folder, in_processing, track_already_downloaded, preferred_quality):
    """Scarica il brano da YouTube e restituisce il percorso del file temporaneo."""
    key = (track['name'].strip().lower(), track['artists'].strip().lower())
    if key in in_processing or track_already_downloaded(track, output_folder):
        print(f"Skipping, already exists or in processing: {track['name']} - {track['artists']}")
        return None

    in_processing.add(key)
    query = f"{track['name']} \"{track['artists']}\""
    print(f"Searching: {query}")
    youtube_url = search_youtube(query, output_folder)
    if not youtube_url:
        log_error(f"Not found on YouTube: {query}", output_folder)
        in_processing.remove(key)
        return None

    print(f"Downloading from: {youtube_url}")
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
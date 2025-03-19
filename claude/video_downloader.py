import os
import random
import yt_dlp

def download_youtube_video(url, filename):
    ydl_opts = {
        "format": "bv*[height<=1080]+ba/b[height<=1080]",
        "outtmpl": filename,
        "merge_output_format": "mp4",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename if os.path.exists(filename) else None

def get_random_video_from_playlist(playlist_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "force_generic_extractor": False
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        if 'entries' in playlist_info:
            videos = [entry['url'] for entry in playlist_info['entries'] if entry.get('url')]
            if videos:
                return random.choice(videos)
    
    return None
import requests
# import subprocess
import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

from azure.storage.blob import BlobServiceClient
from yt_dlp import YoutubeDL
from configs.config import client_id, oauth_token, AZURE_CONNECTION_STRING


def get_data_from_url(url: str):

    response = requests.get(url, headers={
        'Client-ID': client_id,
        'Authorization': f'Bearer {oauth_token}'
    })
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Fehler beim Abrufen von Daten: {response.status_code}, {response.text}")

def get_videos(streamer_name: str) -> tuple:

    error_list = ["ERROR", "", "", "", ""], "ERROR"

    # Benutzer-ID abrufen
    user_data = get_data_from_url(f'https://api.twitch.tv/helix/users?login={streamer_name}')
    if not user_data['data']:
        return error_list

    user_id = user_data['data'][0]['id']
    streamer_display_name = user_data['data'][0]['display_name']

    # Videos des Streamers abrufen
    videos_data = get_data_from_url(f'https://api.twitch.tv/helix/videos?user_id={user_id}&first=40')
    if not videos_data['data']:
        return error_list

    # Videos anzeigen
    video_choices = []

    for _, video in enumerate(videos_data['data'], start=1):
        title = video['title']
        url = video['url']
        duration = video['duration']
        video_key = url.split("/")[-1]
        published_at = video.get('published_at', 'N/A')

        video_choices.append((title, url, video_key, duration, published_at))

    return video_choices, streamer_display_name

def get_clips(video_choices: list) -> list:
    
    return [f"{i[0]}, Dauer: {i[3]}" for i in video_choices]

def download_clip(num: int, video_choices: list, streamer_display_name: str) -> str:

    selected_video = video_choices[num]
    video_title, video_url, video_key, video_duration, video_published_at = selected_video

    # Zielordner definieren
    output_folder = os.getenv("twitch_request_dir")
    os.makedirs(output_folder, exist_ok=True)

    # Dateiname erstellen
    sanitized_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in video_title)
    sanitized_published_at = video_published_at.replace(":", "-").replace("T", "_").replace("Z", "")
    output_filename = f"{video_key}_{streamer_display_name}_{video_duration.replace(':', '-')}_{sanitized_published_at}.mp4"

    # Prüfen auf fehlende Daten
    if not all([video_key, sanitized_title, sanitized_published_at]):
        output_filename = f"INCOM_{output_filename}"

    output_path = os.path.join(output_folder, output_filename)

    # Pfad zu ffmpeg festlegen (angenommen, es befindet sich im übergeordneten Verzeichnis)
    ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg', 'ffmpeg.exe')  # Beispiel: ffmpeg liegt in einem Ordner 'ffmpeg' über dem aktuellen Verzeichnis

    if os.path.isfile(output_path):
        return "Twitch Clip bereits heruntergeladen."

    try:
        # Configure yt-dlp options
        ydl_opts = {
            'ffmpeg_location': ffmpeg_path,  # Specify the path to ffmpeg
            'outtmpl': output_path,          # Output template for downloaded video
        }
        
        # Use yt-dlp as a library
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return f"Video erfolgreich heruntergeladen und gespeichert in: {output_path}"

    except Exception as e:
        return f"Fehler beim Herunterladen: {e}"

def upload_clip():
    pass

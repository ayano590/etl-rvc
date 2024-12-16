import requests
import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

import numpy as np
import pandas as pd
from scipy.io.wavfile import write
from collections.abc import Generator
from azure.storage.blob import BlobServiceClient
from yt_dlp import YoutubeDL
from configs.config import (client_id,
                            oauth_token,
                            NUM_SEARCH_VIDEOS,
                            AZURE_CONNECTION_STRING)
from staging import audio_fft, combine_wav_mp4, extract_wav


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

    MAX_DURATION_MINUTES = 5
    MIN_DURATION_MINUTES = 2

    error_tup = ["ERROR", "", "", "", ""], "ERROR"

    # Benutzer-ID abrufen
    user_data = get_data_from_url(f'https://api.twitch.tv/helix/users?login={streamer_name}')
    if not user_data or not user_data['data']:
        return error_tup

    user_id = user_data['data'][0]['id']
    streamer_display_name = user_data['data'][0]['display_name']

    # Videos des Streamers abrufen
    videos_data = get_data_from_url(f'https://api.twitch.tv/helix/videos?user_id={user_id}&first={NUM_SEARCH_VIDEOS}')
    if not videos_data or not videos_data['data']:
        return error_tup

    video_choices = []

    for video in videos_data['data']:

        title = video['title']
        url = video['url']
        duration = video['duration']

        # Video-Dauer in Minuten konvertieren
        duration_parts = [int(x) for x in duration.replace("h", ":").replace("m", ":").replace("s", "").split(":")]
        total_minutes = sum(x * 60 ** i for i, x in enumerate(reversed(duration_parts))) / 60

        # Video überspringen, wenn es zu lang oder zu kurz ist
        if total_minutes > MAX_DURATION_MINUTES or total_minutes < MIN_DURATION_MINUTES:
            continue

        video_choices.append((title, duration, url))

        if len(video_choices) == 5:
            break

    return video_choices, f"Successfully found clips from {streamer_display_name}!"

def download_clip(num, video_choices: list) -> str:

    selected_video = video_choices.iloc[int(num) - 1].to_list()
    _, _, video_url = selected_video

    # Zielordner definieren
    output_folder = os.getenv("twitch_request_dir")
    os.makedirs(output_folder, exist_ok=True)

    # Dateiname erstellen
    output_filename = "video.mp4"

    output_path = output_folder + "/" + output_filename

    # Specify the path to ffmpeg
    ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')

    if os.path.isfile(output_path):
        return "The clip already exists in the staging area."

    try:
        # Configure yt-dlp options
        ydl_opts = {
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': output_path,
        }
        
        # Use yt-dlp as a library
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return f"Successfully downloaded the file in {output_path}"

    except Exception as e:
        return f"ERROR: Download failed, {e}"

def save_merge_fft(audio: list) -> Generator[str, None, None]:

    sample_rate, audio_data = audio[0], audio[1]

    output_folder = os.getenv("twitch_conv_dir2")

    output_path = output_folder + "/converted_audio.wav"

    write(output_path, sample_rate, audio_data)
    
    yield "Successfully saved the audio file!"

    video_path = os.getenv("twitch_request_dir") + "/video.mp4"

    audio_path_conv, output_path = output_path, os.getenv("twitch_conv_dir") + "/converted_video.mp4"

    combine_wav_mp4.merge_av(audio_path_conv, video_path, output_path)

    audio_path_orig = os.getenv("twitch_request_dir2") + "/audio.wav"

    extract_wav.extract(video_path, audio_path_orig)

    yield "Successfully extracted original audio!"
    yield "Successfully merged original video with converted audio!"

    fft_file_orig = audio_fft.fft_analysis(audio_path_orig, "wav")
    np.savetxt(audio_path_orig, fft_file_orig, delimiter=",")

    fft_file_conv = audio_fft.fft_analysis(audio_path_conv, "wav")
    np.savetxt(audio_path_conv, fft_file_conv, delimiter=",")

    yield "Successfully analyzed the frequency spectrum!"

def upload_clip() -> str:

    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

    twitch_conv_dir = os.getenv("twitch_conv_dir")

    container_client = blob_service_client.get_container_client("pres")

    local_file_path = twitch_conv_dir + "/converted_video.mp4"
    blob_path = os.path.relpath(local_file_path, "pres").replace("\\", "/")  # Relativer Pfad als Blob-Name
    blob_client = container_client.get_blob_client(blob_path)

    blob_properties = blob_client.get_blob_properties()
    blob_size = blob_properties.size
    local_file_size = os.path.getsize(local_file_path)

    if blob_size == local_file_size:
        return f"Datei '{blob_path}' ist bereits vorhanden und identisch. Überspringe Upload."

    # Datei hochladen
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
        return f"Datei '{blob_path}' wurde in den Container 'pres' hochgeladen."

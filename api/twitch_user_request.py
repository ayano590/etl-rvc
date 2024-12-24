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
from api.db_azure_con import upload_files_to_container


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

    MAX_DURATION_MINUTES = 2
    MIN_DURATION_MINUTES = 1

    error_tup = [], None

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
    count = 0

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

        count += 1
        video_choices.append((f"{count}: {title}", duration, url))

        if len(video_choices) == 5:
            break

    return video_choices, f"Successfully found clips from {streamer_display_name}!"

def download_clip(title_with_num: str, video_choices: list) -> str:

    selected_video = video_choices.iloc[int(title_with_num.split(":")[0]) - 1].to_list()
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
    os.makedirs(output_folder, exist_ok=True)

    output_path = output_folder + "/converted_audio.wav"

    write(output_path, sample_rate, audio_data)
    
    yield "Successfully saved the audio file!"

    video_path = os.getenv("twitch_request_dir") + "/video.mp4"

    audio_path_conv, output_path = output_path, os.getenv("twitch_conv_dir") + "/converted_video.mp4"
    os.makedirs(os.getenv("twitch_conv_dir"), exist_ok=True)

    combine_wav_mp4.merge_av(audio_path_conv, video_path, output_path)

    audio_path_orig = os.getenv("twitch_request_dir2") + "/audio.wav"
    os.makedirs(os.getenv("twitch_request_dir2"), exist_ok=True)

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

    CONTAINER_MAPPING = {
    "pres": [
        os.getenv("twitch_request_dir"),
        os.getenv("twitch_request_dir2"),
        os.getenv("twitch_conv_dir"),
        os.getenv("twitch_conv_dir2")
    ]
}

    for container_name, local_folders in CONTAINER_MAPPING.items():
        print(f"Starting upload of files into container: {container_name}")
        upload_files_to_container(container_name, local_folders, blob_service_client)
        print(f"Successfully uploaded files into container: {container_name}\n")

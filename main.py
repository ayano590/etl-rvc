import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

import requests
import subprocess
from api.config_tw import client_id, oauth_token  # Twitch-API-Zugangsdaten

# Globale Variablen
STREAMER_FILE = "api/streamers.txt"
OUTPUT_FOLDER = "api/downloads/twitch_clips"
MAX_DURATION_MINUTES = 5
MAX_VIDEOS_PER_STREAMER = 1

# Hilfsfunktion: Abrufen von API-Daten
def get_data_from_url(url):
    response = requests.get(url, headers={
        'Client-ID': client_id,
        'Authorization': f'Bearer {oauth_token}'
    })
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Fehler beim Abrufen von Daten: {response.status_code}, {response.text}")
        return None

# Hilfsfunktion: Überprüfen, ob ein Video bereits heruntergeladen wurde
def video_exists(video_key, streamer_display_name, video_duration, published_at):
    sanitized_published_at = published_at.replace(":", "-").replace("T", "_").replace("Z", "")
    filename = f"{video_key}_{streamer_display_name}_{video_duration.replace(':', '-')}_{sanitized_published_at}.mp4"
    return os.path.exists(os.path.join(OUTPUT_FOLDER, filename))

# Hauptfunktion: Videos verarbeiten
def process_streamer(streamer_name):
    # Benutzer-ID abrufen
    user_data = get_data_from_url(f'https://api.twitch.tv/helix/users?login={streamer_name}')
    if not user_data or not user_data['data']:
        print(f"Fehler: Kein Benutzer mit dem Namen '{streamer_name}' gefunden.")
        return

    user_id = user_data['data'][0]['id']
    streamer_display_name = user_data['data'][0]['display_name']

    # Videos abrufen
    videos_data = get_data_from_url(f'https://api.twitch.tv/helix/videos?user_id={user_id}&first=30')
    if not videos_data or not videos_data['data']:
        print(f"Keine Videos für den Streamer '{streamer_display_name}' gefunden.")
        return

    # Videos filtern und herunterladen
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Zielordner erstellen, falls nicht vorhanden
    downloaded_count = 0

    for video in videos_data['data']:
        if downloaded_count >= MAX_VIDEOS_PER_STREAMER:
            break

        title = video['title']
        url = video['url']
        duration = video['duration']
        video_key = url.split("/")[-1]
        published_at = video.get('published_at', 'N/A')

        # Video-Dauer in Minuten konvertieren
        try:
            duration_parts = [int(x) for x in duration.replace("h", ":").replace("m", ":").replace("s", "").split(":")]
            total_minutes = sum(x * 60 ** i for i, x in enumerate(reversed(duration_parts))) / 60
        except ValueError:
            print(f"Fehler beim Analysieren der Videodauer: {duration}")
            continue

        # Video überspringen, wenn es zu lang ist
        if total_minutes > MAX_DURATION_MINUTES:
            continue

        # Prüfen, ob das Video bereits existiert
        if video_exists(video_key, streamer_display_name, duration, published_at):
            continue

        # Dateiname erstellen
        sanitized_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title)
        sanitized_published_at = published_at.replace(":", "-").replace("T", "_").replace("Z", "")
        filename = f"{video_key}_{streamer_display_name}_{duration.replace(':', '-')}_{sanitized_published_at}.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        # Video herunterladen
        print(f"\nHerunterladen von: {title}")
        try:
            subprocess.run(["yt-dlp", url, "-o", output_path], check=True)
            print(f"Video erfolgreich heruntergeladen und gespeichert in: {output_path}")
            downloaded_count += 1
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Herunterladen des Videos: {e}")

# Streamer-Liste durchgehen
def main():
    with open(STREAMER_FILE, "r") as f:
        streamers = [line.strip() for line in f if line.strip()]

    for streamer_name in streamers:
        print(f"\nÜberprüfe Streamer: {streamer_name}")
        process_streamer(streamer_name)

if __name__ == "__main__":
    main()

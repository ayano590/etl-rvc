import requests
import subprocess
import os
from config_tw import client_id, oauth_token

# Streamer-Name als Parameter
streamer_name = input("Geben Sie den Namen des Streamers ein: ").strip()

# Funktion zum Abrufen von Daten von einer URL
def get_data_from_url(url):
    response = requests.get(url, headers={
        'Client-ID': client_id,
        'Authorization': f'Bearer {oauth_token}'
    })
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Fehler beim Abrufen von Daten: {response.status_code}, {response.text}")
        exit()

# Benutzer-ID abrufen
user_data = get_data_from_url(f'https://api.twitch.tv/helix/users?login={streamer_name}')
if not user_data['data']:
    print(f"Fehler: Kein Benutzer mit dem Namen '{streamer_name}' gefunden.")
    exit()

user_id = user_data['data'][0]['id']
streamer_display_name = user_data['data'][0]['display_name']

# Videos des Streamers abrufen
videos_data = get_data_from_url(f'https://api.twitch.tv/helix/videos?user_id={user_id}&first=5')
if not videos_data['data']:
    print(f"Keine Videos für den Streamer '{streamer_display_name}' gefunden.")
    exit()

# Videos anzeigen
print("\nDie ersten 5 Videos und ihre Details:")
video_choices = []
for i, video in enumerate(videos_data['data'], start=1):
    title = video['title']
    url = video['url']
    duration = video['duration']
    video_key = url.split("/")[-1]

    print(f"{i}. Titel: {title}")
    print(f"   URL: {url}")
    print(f"   Video_key: {video_key}")
    print(f"   Länge: {duration}")
    print(f"   Streamer: {streamer_display_name}")
    video_choices.append((title, url, video_key, duration))
    print()

# Benutzer wählt ein Video aus
choice = int(input(f"Wählen Sie ein Video (1-{len(video_choices)}): ").strip())
if choice < 1 or choice > len(video_choices):
    print("Ungültige Auswahl. Programm wird beendet.")
    exit()

selected_video = video_choices[choice - 1]
video_title, video_url, video_key, video_duration = selected_video

# Zielordner definieren
output_folder = "downloads/twitch_clips"
os.makedirs(output_folder, exist_ok=True)

# Dateiname erstellen
sanitized_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in video_title)
output_filename = f"{video_key}_{streamer_display_name}_{video_duration.replace(':', '-')}.mp4"
output_path = os.path.join(output_folder, output_filename)

# Video herunterladen
print(f"\nHerunterladen von: {video_title}")
try:
    subprocess.run(["yt-dlp", video_url, "-o", output_path], check=True)
    print(f"Video erfolgreich heruntergeladen und gespeichert in: {output_path}")
except subprocess.CalledProcessError as e:
    print("Fehler beim Herunterladen:", e)

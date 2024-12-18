import requests
import subprocess
import os
import sys
#from config_tw import client_id, oauth_tokenlulu
client_id = 'tb5e6sfh4ip5qboau88dk0lzh19fgb'
oauth_token = 'x1rpjkpms3ayndwupflg6i8wi7qxks'
# from dotenv import load_dotenv
# now_dir = os.getcwd()
# sys.path.append(now_dir)
# load_dotenv()
# from api.config_tw import client_id, oauth_token

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
videos_data = get_data_from_url(f'https://api.twitch.tv/helix/videos?user_id={user_id}&first=100')
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
    published_at = video.get('published_at', 'N/A')

    print(f"{i}. Titel: {title}")
    print(f"   URL: {url}")
    print(f"   Video_key: {video_key}")
    print(f"   Länge: {duration}")
    print(f"   Veröffentlicht am: {published_at}")
    print(f"   Streamer: {streamer_display_name}")
    video_choices.append((title, url, video_key, duration, published_at))
    print()

# Benutzer wählt ein Video aus
choice = int(input(f"Wählen Sie ein Video (1-{len(video_choices)}): ").strip())
if choice < 1 or choice > len(video_choices):
    print("Ungültige Auswahl. Programm wird beendet.")
    exit()

selected_video = video_choices[choice - 1]
video_title, video_url, video_key, video_duration, video_published_at = selected_video

# Zielordner definieren
output_folder = "twitch_clips"
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

# Video herunterladen mit yt-dlp und ffmpeg
print(f"\nHerunterladen von: {video_title}")
try:
    subprocess.run(
        ["yt-dlp", "--ffmpeg-location", ffmpeg_path, video_url, "-o", output_path],
        check=True
    )
    print(f"Video erfolgreich heruntergeladen und gespeichert in: {output_path}")
except subprocess.CalledProcessError as e:
    print("Fehler beim Herunterladen:", e)

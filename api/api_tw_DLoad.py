import subprocess
import os

# Twitch-Video-URL
video_url = "https://www.twitch.tv/videos/2314081935"

# Zielordner definieren
output_folder = "Downloads/TwitchClips"
os.makedirs(output_folder, exist_ok=True)  # Ordner erstellen, falls nicht vorhanden

# yt-dlp-Befehl ausführen
try:
    output_path = os.path.join(output_folder, "video.mp4")
    subprocess.run(["yt-dlp", video_url, "-o", output_path], check=True)
    print(f"Video erfolgreich heruntergeladen und gespeichert in: {output_path}")
except subprocess.CalledProcessError as e:
    print("Fehler beim Herunterladen:", e)

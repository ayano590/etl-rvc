import os
from playsound import playsound

# Beispiel-Pfad zu einer Audiodatei
audio_url = "<hier die URL aus den Daten einfügen>"

# Audiodatei lokal speichern
file_name = "temp_audio.mp3"
os.system(f"curl -o {file_name} {audio_url}")

# Audiodatei abspielen
playsound(file_name)

# Datei löschen (optional)
os.remove(file_name)

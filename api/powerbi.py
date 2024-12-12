import pandas as pd
from playsound import playsound
import os

# Daten aus Power BI laden (Power BI stellt die Tabelle als `dataset` bereit)
df = dataset  # Power BI-Tabelle wird automatisch als `dataset` bereitgestellt

# Durch die URLs iterieren
for index, row in df.iterrows():
    audio_url = row['File URL']  # Spalte mit den Audiodatei-URLs
    file_name = f"temp_audio_{index}.mp3"

    # Datei herunterladen
    os.system(f"curl -o {file_name} {audio_url}")

    # Audiodatei abspielen
    print(f"Spiele Datei: {file_name}")
    playsound(file_name)

    # Datei löschen (optional)
    os.remove(file_name)

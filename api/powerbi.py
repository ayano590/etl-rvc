import pygame
import urllib.request

# Beispiel URL einer Audiodatei
audio_url = "https://example.com/path/to/audiofile.mp3"

# Herunterladen der Datei
audio_file = "audiofile.mp3"
urllib.request.urlretrieve(audio_url, audio_file)

# Initialisierung von pygame für die Audiowiedergabe
pygame.mixer.init()
pygame.mixer.music.load(audio_file)

# Abspielen der Audiodatei
pygame.mixer.music.play()

# Warten, bis die Audiodatei fertig ist
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)


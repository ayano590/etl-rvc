import os

# Liste der Ordnerpfade relativ zum Arbeitsverzeichnis "etl-rvc"
folder_paths = [
    "audios/lv_clips_converted/audio",
    "audios/lv_clips_converted/fft",
    "audios/lv_clips_original/audio",
    "audios/lv_clips_original/fft",
    "audios/tw_clips_original_mp4",
    "audios/tw_clips_converted_mp4",
    "audios/tw_clips_original_wav/audio",
    "audios/tw_clips_original_wav/fft",
    "audios/tw_clips_converted_wav/audio",
    "audios/tw_clips_converted_wav/fft",
    "audios/twitch_user_request_mp4",
    "audios/twitch_user_request_wav",
    "audios/twitch_user_converted_mp4",
    "audios/twitch_user_converted_wav"
]

def find_base_directory(directory_name):

    current_path = os.path.abspath(__file__)

    while True:
        current_path = os.path.dirname(current_path)

        if os.path.basename(current_path) == directory_name:
            return current_path
        
        if current_path == os.path.dirname(current_path):
            return None

def create_folders(base_path, paths):

    for path in paths:
        full_path = os.path.join(base_path, path)

        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"Ordner erstellt: {full_path}")
        else:
            print(f"Ordner existiert bereits: {full_path}")

def main():
    # Suche nach dem Arbeitsverzeichnis "etl-rvc"
    base_directory = find_base_directory("etl-rvc")
    if base_directory is None:
        print("Das Arbeitsverzeichnis 'etl-rvc' wurde nicht gefunden.")
    else:
        # Ordner erstellen
        create_folders(base_directory, folder_paths)

if __name__ == "__main__":
    main()

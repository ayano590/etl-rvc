import os
from azure.storage.blob import BlobServiceClient
# Azure Storage-Verbindungszeichenfolge
AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=dbaraf;AccountKey=TVriYLZAn/S2exKGDxOmt5L2wCrPEs1uPp9URaUQqyYna3CrBq6Q+sQW8pC2H2o+CAQUSMDE/0gg+AStAFBN7A==;EndpointSuffix=core.windows.net"

# Aktuelles Arbeitsverzeichnis finden und nach "etl-rvc" suchen
current_dir = os.getcwd()

# Suche nach dem Verzeichnis 'etl-rvc'
while os.path.basename(current_dir) != "etl-rvc" and current_dir != "/":
    current_dir = os.path.dirname(current_dir)

# Prüfen, ob das Verzeichnis gefunden wurde
if os.path.basename(current_dir) == "etl-rvc":
    print(f"Das Arbeitsverzeichnis 'etl-rvc' wurde gefunden: {current_dir}")
else:
    raise RuntimeError("Das Hauptverzeichnis 'etl-rvc' konnte nicht gefunden werden.")

# Lokale Ordner und zugehörige Container (relativ zum Arbeitsverzeichnis)
CONTAINER_MAPPING = {
    "lv-c-c": [
        os.path.join(current_dir, "audios", "lv_clips_converted", "audio"),
        os.path.join(current_dir, "audios", "lv_clips_converted", "fft")
    ],
    "lv-c-o": [
        os.path.join(current_dir, "audios", "lv_clips_original", "audio"),
        os.path.join(current_dir, "audios", "lv_clips_original", "fft")
    ],
    "tw-c-c": [
        os.path.join(current_dir, "audios", "tw_clips_converted_mp4"),
        os.path.join(current_dir, "audios", "tw_clips_converted_wav", "fft")
    ],
    "tw-c-o": [
        os.path.join(current_dir, "audios", "tw_clips_original_wav", "audio"),
        os.path.join(current_dir, "audios", "tw_clips_original_wav", "fft")
    ]
}

# Funktion: Dateien von lokalen Ordnern in Container kopieren
def upload_files_to_container(container_name, local_folders, blob_service_client):
    container_client = blob_service_client.get_container_client(container_name)

    for local_folder in local_folders:
        # Erstellen des lokalen Ordners, falls er nicht existiert
        if not os.path.exists(local_folder):
            print(f"Lokaler Ordner {local_folder} existiert nicht. Erstelle ihn.")
            os.makedirs(local_folder, exist_ok=True)  # Ordner erstellen

        # Dateien im lokalen Ordner durchgehen
        for root, _, files in os.walk(local_folder):
            for file_name in files:
                local_file_path = os.path.join(root, file_name)
                blob_path = os.path.relpath(local_file_path, local_folder).replace("\\", "/")  # Relativer Pfad als Blob-Name
                blob_client = container_client.get_blob_client(blob_path)

                # Überprüfen, ob die Datei bereits vorhanden ist
                try:
                    blob_properties = blob_client.get_blob_properties()
                    blob_size = blob_properties.size
                    local_file_size = os.path.getsize(local_file_path)

                    if blob_size == local_file_size:
                        print(f"Datei '{blob_path}' ist bereits vorhanden und identisch. Überspringe Upload.")
                        continue
                except Exception:
                    # Blob existiert nicht
                    pass

                # Datei hochladen
                with open(local_file_path, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)
                    print(f"Datei '{blob_path}' wurde in den Container '{container_name}' hochgeladen.")


# Hauptfunktion
def main():
    # Verbindung zum Blob Service herstellen
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

    # Für jeden Container die zugehörigen Dateien hochladen
    for container_name, local_folders in CONTAINER_MAPPING.items():
        print(f"Beginne mit dem Hochladen von Dateien für Container: {container_name}")
        upload_files_to_container(container_name, local_folders, blob_service_client)
        print(f"Fertig mit dem Hochladen für Container: {container_name}\n")

if __name__ == "__main__":
    main()

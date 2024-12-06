from azure.storage.blob import BlobServiceClient

# Connection String deines Storage Accounts
connection_string = "DefaultEndpointsProtocol=https;AccountName=dbaraf;AccountKey=TVriYLZAn/S2exKGDxOmt5L2wCrPEs1uPp9URaUQqyYna3CrBq6Q+sQW8pC2H2o+CAQUSMDE/0gg+AStAFBN7A==;EndpointSuffix=core.windows.net"  # Ersetze dies mit deinem Connection String
container_name = "test1"  # Der Name deines Containers
blob_name = "2294323437_Trymacs_2m23s_2024-11-05_15-38-56.mp4"  # Name, unter dem die Datei gespeichert wird
lokale_datei = "downloads/twitch_clips/2294323437_Trymacs_2m23s_2024-11-05_15-38-56.mp4"  # Pfad zur lokalen Datei

try:
    # BlobServiceClient initialisieren
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Container erstellen, falls dieser nicht existiert
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    # Datei hochladen
    blob_client = container_client.get_blob_client(blob_name)
    with open(lokale_datei, "rb") as data:
        blob_client.upload_blob(data)

    print(f"Datei '{lokale_datei}' erfolgreich hochgeladen als '{blob_name}'.")

except Exception as ex:
    print(f"Fehler: {ex}")

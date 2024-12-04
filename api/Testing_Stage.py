import requests
import os


# Funktion: Suche nach Hörbüchern in LibriVox
def search_librivox_books(title=None, author=None, genre=None, language=None, format="json", extended=1):
    base_url = "https://librivox.org/api/feed/audiobooks/"
    params = {
        "title": title,
        "author": author,
        "genre": genre,
        "language": language,
        "format": format,
        "extended": extended
    }

    try:
        response = requests.get(base_url, params=params)
        print(f"Request URL: {response.url}")  # Debugging-Ausgabe der URL
        response.raise_for_status()
        return response.json() if format == "json" else response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


# Funktion: Audiodateien von LibriVox herunterladen
def download_librivox_audio(book_id, save_path="./audiobooks"):
    base_url = f"https://librivox.org/api/feed/audiobooks/?id={book_id}&format=json"

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        book_data = response.json()

        if 'books' in book_data and book_data['books']:
            book = book_data['books'][0]  # Nehme das erste Buch (bei ID ist es eindeutig)
            title = book.get('title', 'unknown_title')
            language = book.get('language', 'unknown_language')
            zip_url = book.get('url_zip_file')

            print(f"Selected Book: {title} (Language: {language})")

            if zip_url:
                # Erstelle den Zielordner, falls er nicht existiert
                os.makedirs(save_path, exist_ok=True)

                # Lade die ZIP-Datei herunter
                zip_path = os.path.join(save_path, f"{title}.zip")
                print(f"Downloading '{title}'...")
                with requests.get(zip_url, stream=True) as zip_response:
                    zip_response.raise_for_status()
                    with open(zip_path, "wb") as zip_file:
                        for chunk in zip_response.iter_content(chunk_size=8192):
                            zip_file.write(chunk)
                print(f"Downloaded: {zip_path}")
            else:
                print("No downloadable audio file found for this book.")
        else:
            print("No book data found for the provided ID.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


# Hauptprogramm
if __name__ == "__main__":
    # Schritt 1: Suche nach Hörbüchern
    books = search_librivox_books(format="json", extended=1)
    if books and "books" in books:
        print("\nAvailable Books:\n")
        for i, book in enumerate(books.get("books", []), start=1):
            title = book.get("title", "No title")
            language = book.get("language", "Unknown")
            book_id = book.get("id")
            print(f"{i}. Title: {title}, Language: {language}, ID: {book_id}")

        # Schritt 2: Benutzer wählt ein Buch aus
        try:
            choice = int(input("\nEnter the number of the book you want to download: ")) - 1
            selected_book = books['books'][choice]
            book_id = selected_book['id']

            # Schritt 3: Lade Audiodateien des ausgewählten Buches herunter
            download_librivox_audio(book_id)
        except (IndexError, ValueError):
            print("Invalid selection.")
    else:
        print("No books found.")

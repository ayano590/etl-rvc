import requests
import os


# Funktion: Suche nach Hörbüchern in LibriVox
def search_librivox_books(title=None, author=None, genre=None, format="json"):
    base_url = "https://librivox.org/api/feed/audiobooks"
    params = {
        "title": title,
        "author": author,
        "genre": genre,
        "format": format
    }

    try:
        response = requests.get(base_url, params=params)
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
            zip_url = book.get('url_zip_file')

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


# Beispiel: Suche nach einem Buch und lade die Audiodateien herunter
if __name__ == "__main__":
    # Schritt 1: Suche nach einem Buch
    books = search_librivox_books(author="Mark Twain", format="json")
    if books:
        for i, book in enumerate(books.get('books', []), start=1):
            print(f"{i}. Title: {book['title']}, ID: {book['id']}")

        # Schritt 2: Benutzer wählt ein Buch aus
        try:
            choice = int(input("Enter the number of the book you want to download: ")) - 1
            selected_book = books['books'][choice]
            book_id = selected_book['id']

            # Schritt 3: Lade Audiodateien des ausgewählten Buches herunter
            download_librivox_audio(book_id)
        except (IndexError, ValueError):
            print("Invalid selection.")
    else:
        print("No books found.")

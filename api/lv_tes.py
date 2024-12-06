import requests

# Basis-URL der API
BASE_URL = "https://librivox.org/api/feed/audiobooks"


# Funktion zum Suchen nach Hörbüchern mit Sprachfilterung
def search_audiobooks(keyword, language):
    """
    Sucht nach Hörbüchern, die ein bestimmtes Keyword im Titel enthalten und in der angegebenen Sprache sind.
    """
    params = {
        "format": "json",
        "extended": 1,
        "limit": 1000
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        books = response.json().get("books", [])

        # Filtere Bücher nach der gewählten Sprache
        filtered_books = [book for book in books if book.get("language") == language]

        # Keyword-Filter anwenden
        keyword_lower = keyword.lower()
        matching_books = [
            book for book in filtered_books
            if keyword_lower in book["title"].lower() and len(book.get("sections", [])) >= 5
        ]

        return matching_books[:5]  # Maximal 5 Bücher zurückgeben
    else:
        print("Fehler bei der API-Anfrage:", response.status_code)
        return []


# Funktion zum Abrufen von Kapitelinformationen
def get_chapter_info(book_id):
    """
    Ruft Kapitelinformationen für ein spezifisches Buch ab.
    """
    book_url = f"https://librivox.org/api/feed/audiobooks/?id={book_id}&format=json&extended=1"
    response = requests.get(book_url)
    if response.status_code == 200:
        book = response.json()
        if str(book_id) != str(book["books"][0]["id"]):
            print("Fehler: Abgerufene Buch-ID stimmt nicht mit der Auswahl überein.")
            return []
        chapters = book["books"][0].get("sections", [])
        if chapters:
            return chapters[:5]
        else:
            print("Keine Kapitelinformationen gefunden.")
            return []
    else:
        print("Fehler beim Abrufen der Kapitelinformationen:", response.status_code)
        return []


# Funktion zum Herunterladen eines Kapitels
def download_chapter(audio_url, filename):
    """
    Lädt ein Kapitel herunter und speichert es in einer Datei.
    """
    response = requests.get(audio_url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Kapitel wurde heruntergeladen: {filename}")
    else:
        print("Fehler beim Herunterladen des Kapitels:", response.status_code)


# Hauptprogramm
if __name__ == "__main__":
    # Eingabe: Keyword
    keyword = input("Geben Sie ein Schlagwort für den Titel ein: ")

    # Auswahl der Sprache aus der Liste
    print("\nWählen Sie die Sprache der Hörbücher aus:")
    LANGUAGES = {
        "English": "English",
        "German": "German",
        "French": "French",
        "Spanish": "Spanish",
        "Chinese": "Chinese"
    }

    for idx, language in enumerate(LANGUAGES.keys(), 1):
        print(f"{idx}. {language}")

    # Benutzer wählt eine Sprache
    language_choice = int(input("Wählen Sie eine Zahl aus (1-5): "))
    selected_language = list(LANGUAGES.values())[language_choice - 1]

    # Suche nach Hörbüchern
    books = search_audiobooks(keyword, selected_language)
    if not books:
        print("Keine Hörbücher gefunden.")
        exit()

    # Gefundene Hörbücher anzeigen
    print("\nGefundene Hörbücher:")
    for i, book in enumerate(books, 1):
        print(f"{i}. {book['title']} (ID: {book['id']})")

    # Auswahl eines Hörbuchs
    choice = int(input("\nWählen Sie ein Hörbuch aus (1-5): "))
    selected_book = books[choice - 1]

    print(f"\nKapitel von '{selected_book['title']}':")
    chapters = get_chapter_info(selected_book["id"])
    if not chapters:
        print("Keine Kapitel gefunden.")
        exit()

    # Kapitel anzeigen
    for i, chapter in enumerate(chapters, 1):
        print(f"{i}. {chapter['title']} - Dauer: {chapter['playtime']}")

    # Auswahl eines Kapitels
    chapter_choice = int(input("\nWählen Sie ein Kapitel aus (1-5): "))
    selected_chapter = chapters[chapter_choice - 1]

    # Herunterladen des ausgewählten Kapitels
    audio_url = selected_chapter["listen_url"]
    filename = f"{selected_chapter['title'].replace(' ', '_')}.mp3"
    download_chapter(audio_url, filename)

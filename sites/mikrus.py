import requests
from notifier import send_message
from storage import load_state, save_state

SITE_URL = "https://mikr.us/recykling.txt"
SITE_NAME = "mikrus"

def fetch_content():
    """Pobiera zawartość pliku tekstowego."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    r = requests.get(SITE_URL, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def check_and_notify():
    """Sprawdza, czy zawartość mikr.us/recykling.txt się zmieniła."""
    try:
        content = fetch_content()
        content_hash = str(hash(content))

        previous_hash = load_state(SITE_NAME)

        if previous_hash is None:
            save_state(SITE_NAME, content_hash)
            print("[Mikrus] Zapisano stan początkowy")
            return

        if content_hash != previous_hash:
            print("[Mikrus] Wykryto zmianę!")
            send_message(
                f"🐹 <b>Mikrus do wzięcia!</b>\n\n"
                f"Zmieniła się zawartość strony recyklingu.\n"
                f"🔗 {SITE_URL}"
            )
            save_state(SITE_NAME, content_hash)
        else:
            print("[Mikrus] Brak zmian")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("[Mikrus] Błąd 403 – strona blokuje dostęp. "
                  "Spróbuj dodać inne nagłówki (User-Agent, Referer) "
                  "lub sprawdź, czy strona nie wymaga logowania.")
        else:
            print(f"[Mikrus] Błąd HTTP: {e}")
    except Exception as e:
        print(f"[Mikrus] Błąd: {e}")
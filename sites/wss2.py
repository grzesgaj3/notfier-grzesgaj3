import re
from notifier import send_message
from storage import load_wss2_raw, save_wss2_raw

SITE_URL = "https://www.wss2.pl/ogloszenia/ogloszenia-gospodarcze/"
SITE_NAME = "wss2"

def fetch_content():
    """Pobiera surowy HTML strony."""
    import requests
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(SITE_URL, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def extract_first_announcement(html: str) -> str | None:
    """
    Wycina treść pierwszego (najnowszego) ogłoszenia.
    Szuka pierwszego wystąpienia słowa 'OGŁOSZENIE' i zwraca
    wszystko do kolejnego 'OGŁOSZENIE' lub końca strony.
    """
    # Znajdź wszystkie pozycje słowa OGŁOSZENIE
    pattern = r'(OGŁOSZENIE)'
    matches = list(re.finditer(pattern, html, re.IGNORECASE))
    if len(matches) < 2:
        return None  # Tylko jedno ogłoszenie na stronie

    start = matches[0].start()
    end = matches[1].start()
    return html[start:end].strip()

def parse_announcement(block: str) -> list[dict]:
    """
    Z bloku ogłoszenia wyciąga listę przedmiotów:
    [{nazwa, wadium}, ...]
    """
    items = []
    # Szukamy tabeli (wiersze między <tr> i </tr> zawierające <td>)
    # W praktyce HTML jest dość prosty – tabela ma kolumny
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', block, re.DOTALL | re.IGNORECASE)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
        # W tabeli mamy 8 kolumn: Lp, Nr inw., Nazwa, Ilość, Rok, Wart. pocz., Wycena, Wadium
        if len(cells) >= 8:
            nazwa = re.sub(r'<[^>]+>', '', cells[2]).strip()  # Usuń ewentualne tagi HTML
            wadium = re.sub(r'<[^>]+>', '', cells[7]).strip()
            if nazwa and wadium:
                items.append({"nazwa": nazwa, "wadium": wadium})
    return items

def check_and_notify():
    """Główna funkcja sprawdzająca zmiany na WSS2."""
    try:
        html = fetch_content()
        first_block = extract_first_announcement(html)
        if not first_block:
            print("[WSS2] Nie znaleziono ogłoszeń")
            return

        previous_block = load_wss2_raw()

        if previous_block is None:
            # Pierwsze uruchomienie – zapisujemy stan
            save_wss2_raw(first_block)
            print("[WSS2] Zapisano stan początkowy")
            return

        if first_block != previous_block:
            print("[WSS2] Wykryto zmianę!")
            items = parse_announcement(first_block)
            # Buduj wiadomość
            msg_parts = ["<b>🆕 Nowe ogłoszenie na WSS2!</b>\n"]
            for item in items:
                msg_parts.append(
                    f"📦 <b>{item['nazwa']}</b>\n"
                    f"💰 Wysokość wadium: {item['wadium']}\n"
                )
            msg_parts.append(f"\n🔗 {SITE_URL}")
            send_message("\n".join(msg_parts))
            save_wss2_raw(first_block)
        else:
            print("[WSS2] Brak zmian")
    except Exception as e:
        print(f"[WSS2] Błąd: {e}")
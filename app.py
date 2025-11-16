import streamlit as st
from datetime import datetime, timedelta
import requests
from icalendar import Calendar
from io import BytesIO

ICAL_URL = "https://ical.booking.com/v1/export?t=641d7a68-4a90-4d73-b223-2668d2d33476"

# --- Načtení obsazených dní z iCal ---
def nacti_obsazene():
    obsazene = set()
    try:
        response = requests.get(ICAL_URL)
        cal = Calendar.from_ical(response.content)
        for event in cal.walk('VEVENT'):
            start = event.get('dtstart').dt
            end = event.get('dtend').dt
            # Převod na date (pro bezpečí, pokud je datetime)
            if isinstance(start, datetime):
                start = start.date()
            if isinstance(end, datetime):
                end = end.date()
            # Přidáme všechny dny v rozsahu do setu
            den = start
            while den < end:
                obsazene.add(den)
                den += timedelta(days=1)
    except Exception as e:
        st.error(f"Chyba načítání iCal: {e}")
    return obsazene

obsazene_dny = nacti_obsazene()

# --- Zobrazení kalendáře ---
st.title("Rezervace Apartmán Tyršova")
dnes = datetime.today().date()
vyber = st.date_input(
    "Vyberte den pobytu",
    min_value=dnes,
    value=dnes
)

if vyber in obsazene_dny:
    st.warning("Tento den je již obsazen.")
else:
    st.success(f"Den {vyber} je volný!")

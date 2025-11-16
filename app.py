import streamlit as st
from datetime import datetime, timedelta, date
import requests
from icalendar import Calendar

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
            if isinstance(start, datetime):
                start = start.date()
            if isinstance(end, datetime):
                end = end.date()
            den = start
            while den < end:
                obsazene.add(den)
                den += timedelta(days=1)
    except Exception as e:
        st.error(f"Chyba načítání iCal: {e}")
    return obsazene

obsazene_dny = nacti_obsazene()

# --- Zobrazení měsíce ---
st.title("Rezervace Apartmán Tyršova")

dnes = datetime.today()
start_mesic = date(dnes.year, dnes.month, 1)
end_mesic = (start_mesic + timedelta(days=32)).replace(day=1)

den = start_mesic
while den < end_mesic:
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    for i in range(7):
        if den >= end_mesic:
            break
        label = f"{den.day}"
        if den in obsazene_dny:
            if col1:
                col = [col1, col2, col3, col4, col5, col6, col7][i]
                col.button(f"❌ {label}", disabled=True, key=str(den))
        else:
            col = [col1, col2, col3, col4, col5, col6, col7][i]
            if col.button(f"✅ {label}", key=str(den)):
                st.success(f"Vybrali jste den: {den}")
        den += timedelta(days=1)

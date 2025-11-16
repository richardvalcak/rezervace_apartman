import streamlit as st
from datetime import datetime, timedelta, date
import requests
from icalendar import Calendar

st.set_page_config(page_title="Rezervace Apartmánu", layout="centered")

st.title("Rezervační kalendář – Apartmán Tyršova")

# --- iCal feed z Booking.com ---
ICAL_URL = "TVŮJ_ICAL_FEED_URL"

# --- Načtení obsazených dní z iCal ---
def get_obsazene_dny(url):
    try:
        resp = requests.get(url)
        cal = Calendar.from_ical(resp.content)
        obsazene = set()
        for event in cal.walk('VEVENT'):
            start = event.get('dtstart').dt
            end = event.get('dtend').dt
            # převést na date pokud je datetime
            if isinstance(start, datetime):
                start = start.date()
            if isinstance(end, datetime):
                end = end.date()
            delta = (end - start).days
            for i in range(delta):
                obsazene.add((start + timedelta(days=i)).strftime("%Y-%m-%d"))
        return obsazene
    except Exception as e:
        st.error(f"Chyba načítání iCal: {e}")
        return set()

if "obsazene_dny" not in st.session_state:
    st.session_state.obsazene_dny = get_obsazene_dny(ICAL_URL)

# --- Výběr období ---
st.subheader("Vyberte období pobytu")
start_date = st.date_input("Od:", min_value=date.today())
end_date = st.date_input("Do:", min_value=start_date)

# --- Kontrola dostupnosti ---
selected_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
conflict = [d for d in selected_range if d.strftime("%Y-%m-%d") in st.session_state.obsazene_dny]

if conflict:
    st.error(f"Některé dny jsou již obsazené: {', '.join([d.strftime('%d.%m.%Y') for d in conflict])}")
    vyber_ok = False
else:
    vyber_ok = True

# --- Tlačítko potvrzení ---
if st.button("Rezervovat"):
    if vyber_ok:
        for d in selected_range:
            st.session_state.obsazene_dny.add(d.strftime("%Y-%m-%d"))
        st.success(f"Rezervace potvrzena od {start_date} do {end_date}")
    else:
        st.warning("Vyberte jiné volné dny.")

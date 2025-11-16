import streamlit as st
from datetime import datetime, timedelta, date
import requests
from icalendar import Calendar

st.set_page_config(page_title="Rezervace Apartmán Tyršova", layout="centered")

# --- Načtení obsazených dní z iCal ---
ICAL_URL = "https://ical.booking.com/v1/export?t=641d7a68-4a90-4d73-b223-2668d2d33476"

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

# --- Nápis nahoře ---
st.title("Kniha hostů – Rezervace")
st.markdown("""
Prosíme vás o vyplnění této knihy hostů.  
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.  
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.  
Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo
""")

# --- Kalendář aktuálního měsíce ---
dnes = datetime.today()
start_mesic = date(dnes.year, dnes.month, 1)
end_mesic = (start_mesic + timedelta(days=32)).replace(day=1)

st.subheader(f"Dostupné dny v {dnes.strftime('%B %Y')}")

den = start_mesic
while den < end_mesic:
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    for i in range(7):
        if den >= end_mesic:
            break
        col = [col1, col2, col3, col4, col5, col6, col7][i]
        label = f"{den.day}"
        if den in obsazene_dny:
            col.button(f"❌ {label}", disabled=True, key=str(den))
        else:
            if col.button(f"✅ {label}", key=str(den)):
                st.session_state['vybrany_den'] = den
        den += timedelta(days=1)

# --- Zobrazení vybraného dne a formulář žádosti ---
if 'vybrany_den' in st.session_state:
    st.success(f"Vybrali jste den: {st.session_state['vybrany_den'].strftime('%d.%m.%Y')}")
    with st.form("rezervace_form"):
        jmeno = st.text_input("Jméno a příjmení *")
        email = st.text_input("Email *")
        zprava = st.text_area("Zpráva / žádost o cenu")
        souhlas = st.checkbox("Souhlasím se zpracováním osobních údajů podle výše uvedeného textu")
        submitted = st.form_submit_button("Odeslat žádost")
        if submitted:
            if not all([jmeno.strip(), email.strip(), souhlas]):
                st.error("Vyplňte všechny povinné údaje a souhlas.")
            else:
                st.success("Žádost byla odeslána. Brzy vás budeme kontaktovat!")

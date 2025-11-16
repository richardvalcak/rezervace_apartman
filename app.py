import streamlit as st
from datetime import datetime, timedelta, date
import requests
from icalendar import Calendar

st.set_page_config(page_title="Rezervace Apartmán Tyršova", layout="centered")

ICAL_URL = "https://ical.booking.com/v1/export?t=641d7a68-4a90-4d73-b223-2668d2d33476"

# --- Načtení obsazených dní ---
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
    except:
        pass
    return obsazene

obsazene_dny = nacti_obsazene()

# --- Úvodní text ---
st.title("Kniha hostů – Rezervace")
st.markdown("""
Prosíme vás o vyplnění této knihy hostů.  
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.  
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.  
Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo
""")

# --- Výběr období ---
if 'start_den' not in st.session_state:
    st.session_state['start_den'] = None
if 'end_den' not in st.session_state:
    st.session_state['end_den'] = None

def zobraz_mesic(start_date):
    import calendar
    cal = calendar.Calendar(firstweekday=0)
    days = list(cal.itermonthdates(start_date.year, start_date.month))
    
    st.markdown(f"### {start_date.strftime('%B %Y')}")
    
    # Dny týdne
    dni_tydne = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
    cols = st.columns(7)
    for i, d in enumerate(dni_tydne):
        cols[i].markdown(f"<b>{d}</b>", unsafe_allow_html=True)
    
    # Grid dní
    for i, den in enumerate(days):
        if i % 7 == 0:
            cols = st.columns(7)
        datum_str = den.strftime("%Y-%m-%d")
        color = "#d4edda" if den not in obsazene_dny and den.month == start_date.month else "#f8d7da"
        text = f"{den.day}"
        if st.session_state.get('start_den') == den or st.session_state.get('end_den') == den:
            color = "#cce5ff"
        if den.month != start_date.month:
            cols[i%7].markdown(" ", unsafe_allow_html=True)
            continue
        
        if cols[i%7].button(text, key=datum_str):
            if den in obsazene_dny:
                return
            if st.session_state['start_den'] is None:
                st.session_state['start_den'] = den
                st.session_state['end_den'] = None
            elif st.session_state['end_den'] is None:
                if den < st.session_state['start_den']:
                    st.session_state['start_den'], st.session_state['end_den'] = den, st.session_state['start_den']
                else:
                    st.session_state['end_den'] = den
            else:
                st.session_state['start_den'] = den
                st.session_state['end_den'] = None

# --- Zobrazení 3 měsíců ---
dnes = date.today()
for m in range(3):
    mesic = (dnes.replace(day=1) + timedelta(days=32*m)).replace(day=1)
    zobraz_mesic(mesic)

# --- Vybrané období ---
if st.session_state['start_den']:
    text = f"Vybrané období: {st.session_state['start_den'].strftime('%d.%m.%Y')}"
    if st.session_state['end_den']:
        text += f" - {st.session_state['end_den'].strftime('%d.%m.%Y')}"
    st.success(text)

# --- Formulář žádosti ---
if st.session_state['start_den']:
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

# --- CSS pro hezký vzhled ---
st.markdown("""
<style>
div.stButton > button:first-child {
    height: 2.5em;
    margin: 2px;
    border-radius: 8px;
    border: none;
    font-weight: bold;
    color: #212529;
}
</style>
""", unsafe_allow_html=True)

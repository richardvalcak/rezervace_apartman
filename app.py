# app.py
import streamlit as st
from datetime import datetime, timedelta
import calendar
import requests
from icalendar import Calendar
from io import BytesIO

st.set_page_config(page_title="Dostupnost Apartmánu", layout="wide")
st.title("Kniha hostů – Dostupnost Apartmánu Tyršova")

st.markdown("""
Prosíme vás o vyplnění této knihy hostů.  
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.  
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.  
**Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo**
""")

# === Načtení iCal obsazených dnů ===
ICAL_URL = "https://ical.booking.com/v1/export?t=641d7a68-4a90-4d73-b223-2668d2d33476"
obsazene_dny = []

try:
    response = requests.get(ICAL_URL)
    cal = Calendar.from_ical(response.content)
    for component in cal.walk():
        if component.name == "VEVENT":
            start = component.get('dtstart').dt
            end = component.get('dtend').dt
            # přidej každý den v rozsahu
            current = start
            while current < end:
                obsazene_dny.append(current)
                current += timedelta(days=1)
except Exception as e:
    st.error(f"Chyba při načítání iCal: {e}")

# === Parametry kalendáře ===
pocet_mesicu = 2
dnes = datetime.today()

def zobraz_kalendar(start_date, months=2):
    for m in range(months):
        mesic_date = start_date.replace(day=1) + timedelta(days=30*m)
        rok = mesic_date.year
        mesic = mesic_date.month

        st.markdown(f"### {calendar.month_name[mesic]} {rok}")
        cal = calendar.Calendar(firstweekday=0)
        dni_mesice = list(cal.itermonthdates(rok, mesic))

        # hlavička týdne
        cols = st.columns(7)
        for i, day_name in enumerate(['Po','Út','St','Čt','Pá','So','Ne']):
            cols[i].markdown(f"**{day_name}**", unsafe_allow_html=True)

        col_index = 0
        cols = st.columns(7)
        for den in dni_mesice:
            if den.month != mesic:
                cols[col_index].markdown(" ", unsafe_allow_html=True)
            else:
                datum_str = den.strftime("%Y-%m-%d")
                if den in obsazene_dny:
                    # červené = obsazeno
                    cols[col_index].markdown(
                        f"<div style='background-color:#f28b82; color:white; padding:5px; border-radius:5px; text-align:center;' title='{datum_str}'>{den.day}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    # zelené = volno
                    cols[col_index].markdown(
                        f"<div style='background-color:#81c995; color:white; padding:5px; border-radius:5px; text-align:center;' title='{datum_str}'>{den.day}</div>",
                        unsafe_allow_html=True
                    )
            col_index += 1
            if col_index == 7:
                col_index = 0
                st.markdown("---")  # čára mezi týdny
                cols = st.columns(7)

zobraz_kalendar(dnes, months=pocet_mesicu)

st.markdown("""
#### Poznámka pro zákazníky:
Zelené dny jsou volné, červené dny jsou již obsazené.  
Po výběru termínu vás budeme kontaktovat s cenou a potvrzením rezervace.
""")

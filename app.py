# app.py
import streamlit as st
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Dostupnost Apartmánu", layout="wide")

st.title("Kniha hostů – Dostupnost Apartmánu Tyršova")

st.markdown("""
Prosíme vás o vyplnění této knihy hostů.  
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.  
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.  
**Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo**
""")

# === Nastavení dostupnosti ===
# obsazené dny – např. z iCal nebo databáze
obsazene_dny = [
    datetime.today() + timedelta(days=1),
    datetime.today() + timedelta(days=3),
    datetime.today() + timedelta(days=7)
]

# počet měsíců k zobrazení
pocet_mesicu = 2
dnes = datetime.today()

def zobraz_kalendar(start_date, months=2):
    for m in range(months):
        rok = (start_date.replace(day=1) + timedelta(days=30*m)).year
        mesic = (start_date.replace(day=1) + timedelta(days=30*m)).month
        cal = calendar.Calendar(firstweekday=0)  # pondělí
        dni_mesice = list(cal.itermonthdates(rok, mesic))

        st.markdown(f"### {calendar.month_name[mesic]} {rok}")
        # vytvoření mřížky dnů
        cols = st.columns(7)
        # hlavička týdnů
        for i, day_name in enumerate(['Po','Út','St','Čt','Pá','So','Ne']):
            cols[i].markdown(f"**{day_name}**", unsafe_allow_html=True)

        # dny
        col_index = 0
        cols = st.columns(7)
        for den in dni_mesice:
            if den.month != mesic:
                # dny mimo měsíc
                cols[col_index].markdown(" ", unsafe_allow_html=True)
            else:
                datum_str = den.strftime("%Y-%m-%d")
                if den in obsazene_dny:
                    # červené = obsazeno
                    cols[col_index].markdown(f"<div style='background-color:#f28b82; color:white; padding:8px; border-radius:5px; text-align:center;' title='{datum_str}'>{den.day}</div>", unsafe_allow_html=True)
                else:
                    # zelené = volno
                    cols[col_index].markdown(f"<div style='background-color:#81c995; color:white; padding:8px; border-radius:5px; text-align:center;' title='{datum_str}'>{den.day}</div>", unsafe_allow_html=True)
            col_index += 1
            if col_index == 7:
                col_index = 0
                cols = st.columns(7)

zobraz_kalendar(dnes, months=pocet_mesicu)

st.markdown("""
#### Poznámka pro zákazníky:
Zelené dny jsou volné, červené dny jsou již obsazené.  
Po výběru termínu vás budeme kontaktovat s cenou a potvrzením rezervace.
""")

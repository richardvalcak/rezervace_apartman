import streamlit as st
from datetime import date, timedelta
import calendar
import requests
from icalendar import Calendar
from io import BytesIO

st.set_page_config(page_title="Dostupnost Apartmánu", layout="wide")

# --- iCal URL z Booking ---
ical_url = "https://ical.booking.com/v1/export?t=641d7a68-4a90-4d73-b223-2668d2d33476"

# --- Načtení obsazených dnů z iCal ---
def get_obsazene_dny(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        cal = Calendar.from_ical(r.content)
        obsazene = set()
        for component in cal.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                end = component.get('dtend').dt
                if isinstance(start, date) and isinstance(end, date):
                    delta = (end - start).days
                    for i in range(delta):
                        obsazene.add(start + timedelta(days=i))
        return obsazene
    except:
        st.error("Nepodařilo se načíst iCal.")
        return set()

obsazene_dny = get_obsazene_dny(ical_url)

# --- Zobrazení měsíce ---
def zobraz_mesic(year, month):
    st.markdown(f"### {calendar.month_name[month]} {year}")
    dni_tydne = ["Po","Út","St","Čt","Pá","So","Ne"]
    cols = st.columns(7)
    for i,d in enumerate(dni_tydne):
        cols[i].markdown(f"**{d}**")
    
    cal = calendar.Calendar(firstweekday=0)
    days = list(cal.itermonthdates(year, month))
    
    rows = []
    for i in range(0, len(days), 7):
        rows.append(days[i:i+7])
    
    for tyd in rows:
        cols = st.columns(7)
        for i, den in enumerate(tyd):
            if den.month != month:
                cols[i].markdown(" ")
                continue
            color = "#d4edda" if den not in obsazene_dny else "#f8d7da"
            cols[i].markdown(
                f"<div style='background-color:{color}; text-align:center; padding:4px; border-radius:4px;'>{den.day}</div>",
                unsafe_allow_html=True
            )

# --- Zobrazení aktuálního a dvou dalších měsíců ---
dnes = date.today()
for m in range(3):
    mesic = (dnes.replace(day=1) + timedelta(days=32*m)).replace(day=1)
    zobraz_mesic(mesic.year, mesic.month)

st.markdown("""
**Legenda:**  
<div style='display:inline-block; width:20px; height:20px; background-color:#d4edda; border:1px solid #ccc; margin-right:5px;'></div> Volné  
<div style='display:inline-block; width:20px; height:20px; background-color:#f8d7da; border:1px solid #ccc; margin-right:5px;'></div> Obsazené
""", unsafe_allow_html=True)

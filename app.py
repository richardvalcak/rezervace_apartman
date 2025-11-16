import streamlit as st
from datetime import date, timedelta
import calendar

st.set_page_config(page_title="Rezervace Apartmán Tyršova", layout="centered")

# --- Dummy obsazené dny pro test ---
obsazene_dny = {date.today() + timedelta(days=2), date.today() + timedelta(days=5)}

# --- Session pro vybrané období ---
if 'start_den' not in st.session_state:
    st.session_state['start_den'] = None
if 'end_den' not in st.session_state:
    st.session_state['end_den'] = None

# --- Funkce pro zobrazení měsíce ---
def zobraz_mesic(year, month):
    st.markdown(f"### {calendar.month_name[month]} {year}")
    dni_tydne = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
    
    cols = st.columns(7)
    for i, d in enumerate(dni_tydne):
        cols[i].markdown(f"**{d}**")
    
    cal = calendar.Calendar(firstweekday=0)
    days = list(cal.itermonthdates(year, month))
    
    for i, den in enumerate(days):
        if i % 7 == 0:
            cols = st.columns(7)
        if den.month != month:
            cols[i % 7].markdown(" ")
            continue

        # Barva podle stavu
        if den in obsazene_dny:
            color = "#f8d7da"  # červená obsazeno
        else:
            color = "#d4edda"  # zelená volno

        if st.session_state['start_den'] == den or st.session_state['end_den'] == den:
            color = "#cce5ff"  # modrá vybráno

        # Kliknutí
        if st.columns([1])[0].button(str(den.day), key=str(den)):
            if den in obsazene_dny:
                st.warning("Den je obsazený")
            else:
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

        st.columns([1])[0].markdown(f"<div style='background-color:{color}; text-align:center; padding:6px; border-radius:4px;'>{den.day}</div>", unsafe_allow_html=True)

# --- Zobrazení aktuálního a dalších 2 měsíců ---
dnes = date.today()
for m in range(3):
    mesic = (dnes.replace(day=1) + timedelta(days=32*m)).replace(day=1)
    zobraz_mesic(mesic.year, mesic.month)

# --- Vybrané období ---
if st.session_state['start_den']:
    text = f"Vybrané období: {st.session_state['start_den'].strftime('%d.%m.%Y')}"
    if st.session_state['end_den']:
        text += f" - {st.session_state['end_den'].strftime('%d.%m.%Y')}"
    st.success(text)

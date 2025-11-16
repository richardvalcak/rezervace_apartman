import streamlit as st
from datetime import date, timedelta
import calendar

st.set_page_config(page_title="Rezervace Apartmán Tyršova", layout="centered")

# --- Dummy obsazené dny pro test ---
obsazene_dny = {date.today() + timedelta(days=2), date.today() + timedelta(days=5)}

# --- Výběr období ---
if 'start_den' not in st.session_state:
    st.session_state['start_den'] = None
if 'end_den' not in st.session_state:
    st.session_state['end_den'] = None

def zobraz_mesic(start_date):
    dni_tydne = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
    st.markdown(f"### {start_date.strftime('%B %Y')}")
    
    # Dny týdne
    cols = st.columns(7)
    for i, d in enumerate(dni_tydne):
        cols[i].markdown(f"<b>{d}</b>", unsafe_allow_html=True)
    
    # Dny měsíce
    cal = calendar.Calendar(firstweekday=0)
    days = list(cal.itermonthdates(start_date.year, start_date.month))
    
    for i, den in enumerate(days):
        if i % 7 == 0:
            cols = st.columns(7)
        if den.month != start_date.month:
            cols[i % 7].markdown(" ", unsafe_allow_html=True)
            continue
        
        # Barva dle stavu
        if den in obsazene_dny:
            color = "#f8d7da"  # červená obsazeno
        else:
            color = "#d4edda"  # zelená volno

        if st.session_state.get('start_den') == den or st.session_state.get('end_den') == den:
            color = "#cce5ff"  # modrá vybráno

        # HTML div pro barvu
        btn_html = f"""
        <div style='background-color:{color}; text-align:center; border-radius:6px; padding:6px; margin:2px; cursor:pointer;'>
            {den.day}
        </div>
        """

        if cols[i % 7].button("", key=str(den), help=str(den)):
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

        cols[i % 7].markdown(btn_html, unsafe_allow_html=True)

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

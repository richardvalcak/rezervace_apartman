import streamlit as st
from datetime import date, timedelta, datetime
import calendar

st.title("Kniha hostů – Rezervace Apartmánu Tyršova")

# --- Obsazené dny ---
if "obsazene_dny" not in st.session_state:
    st.session_state.obsazene_dny = {"2025-11-20", "2025-11-21", "2025-11-23"}

# --- Výběr období (mimo form) ---
st.subheader("Vyberte období pobytu")
dnes = date.today()
vybrane_start = st.date_input("Od", value=dnes)
vybrane_end = st.date_input("Do", value=dnes + timedelta(days=1))

# Kontrola, zda jsou dny volné
delta = (vybrane_end - vybrane_start).days + 1
obsazene = []
for i in range(delta):
    den = vybrane_start + timedelta(days=i)
    if den.strftime("%Y-%m-%d") in st.session_state.obsazene_dny:
        obsazene.append(den)
if obsazene:
    st.error(f"Tyto dny jsou již obsazené: {', '.join([d.strftime('%d.%m.%Y') for d in obsazene])}")

# --- Formulář osobních údajů ---
with st.form("rezervace_form"):
    st.subheader("Osobní údaje")
    jmeno = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
    narozeni = st.text_input("Datum narození *", placeholder="15. 6. 1985")
    adresa = st.text_input("Adresa *", placeholder="Hlavní 123, Brno")
    doklad = st.text_input("Doklad *", placeholder="123456789 (OP)")
    souhlas = st.checkbox(
        "Souhlasím se zpracováním osobních údajů podle výše uvedeného textu."
    )
    odeslat = st.form_submit_button("ODESLAT REZERVACI")

    if odeslat:
        errors = []
        if not all([jmeno.strip(), narozeni.strip(), adresa.strip(), doklad.strip()]):
            errors.append("Vyplňte všechna povinná pole.")
        if not souhlas:
            errors.append("Souhlas je povinný.")
        if obsazene:
            errors.append("Nelze rezervovat obsazené dny.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            # Označení dní jako obsazené
            for i in range(delta):
                den = vybrane_start + timedelta(days=i)
                st.session_state.obsazene_dny.add(den.strftime("%Y-%m-%d"))
            st.success(
                f"Rezervace od {vybrane_start.strftime('%d.%m.%Y')} do {vybrane_end.strftime('%d.%m.%Y')} byla úspěšná!"
            )

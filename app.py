# app.py – Rezervace | Apartmán Tyršova | 2025
import streamlit as st
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Rezervace – Apartmán Tyršova", layout="centered")
st.title("Kniha hostů")

st.markdown("""
Prosíme vás o vyplnění této knihy hostů.  
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.  
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.  
**Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo**
""")

# --- Inicializace obsazených dní ---
if "obsazene_dny" not in st.session_state:
    st.session_state.obsazene_dny = set()  # např. "2025-11-20"

# --- Funkce pro zobrazení kalendáře ---
def zobraz_kalendar(start_date, dny=30):
    czech_dny = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
    dnes = start_date
    dostupne_dny = []
    for i in range(dny):
        den = dnes + timedelta(days=i)
        den_str = den.strftime("%Y-%m-%d")
        dostupne_dny.append(den_str)

    # Tlačítka pro každý den
    vybrany_den = None
    for den_str in dostupne_dny:
        den = datetime.strptime(den_str, "%Y-%m-%d")
        den_display = den.strftime("%d. %m. %Y")
        if den_str in st.session_state.obsazene_dny:
            st.button(f"❌ {den_display}", disabled=True)
        else:
            if st.button(f"✅ {den_display}"):
                vybrany_den = den_str
    return vybrany_den

# --- Formulář rezervace ---
with st.form("rezervace_form"):
    st.subheader("1. Osoba")
    j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
    n1 = st.text_input("Datum narození *", placeholder="15. 6. 1985")
    a1 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno")
    d1 = st.text_input("Doklad *", placeholder="123456789 (OP)")

    st.markdown("---")
    st.subheader("Výběr dne pobytu")
    dnes = datetime.today()
    vybrany_den = zobraz_kalendar(dnes, dny=60)

    st.markdown("---")
    souhlas = st.checkbox("Souhlasím se zpracováním osobních údajů podle výše uvedeného textu.")

    submitted = st.form_submit_button("ODESLAT REZERVACI")

    if submitted:
        errors = []
        if not all([j1.strip(), n1.strip(), a1.strip(), d1.strip()]):
            errors.append("Vyplňte všechna povinná pole.")
        if not vybrany_den:
            errors.append("Vyberte den pobytu.")
        if not souhlas:
            errors.append("Souhlas je povinný.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            st.session_state.obsazene_dny.add(vybrany_den)
            st.success(f"Rezervace na den {vybrany_den} byla úspěšná! 🏡")

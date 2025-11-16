# app.py – Rezervace | Apartmán Tyršova | 2025
import streamlit as st
from datetime import datetime, timedelta

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

# --- Generování seznamu dostupných dní ---
dnes = datetime.today()
dostupne_dny = []
for i in range(60):  # následujících 60 dní
    den = dnes + timedelta(days=i)
    den_str = den.strftime("%Y-%m-%d")
    if den_str not in st.session_state.obsazene_dny:
        dostupne_dny.append(den_str)

# --- Formulář rezervace ---
with st.form("rezervace_form"):
    st.subheader("1. Osoba")
    j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
    n1 = st.text_input("Datum narození *", placeholder="15. 6. 1985")
    a1 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno")
    d1 = st.text_input("Doklad *", placeholder="123456789 (OP)")

    st.markdown("---")
    st.subheader("Výběr dní pobytu")

    if dostupne_dny:
        vybrane_dny = st.multiselect("Vyberte volné dny", dostupne_dny)
    else:
        st.warning("Momentálně nejsou volné žádné termíny.")
        vybrane_dny = []

    st.markdown("---")
    souhlas = st.checkbox("Souhlasím se zpracováním osobních údajů podle výše uvedeného textu.")

    submitted = st.form_submit_button("ODESLAT REZERVACI")

    if submitted:
        errors = []
        if not all([j1.strip(), n1.strip(), a1.strip(), d1.strip()]):
            errors.append("Vyplňte všechna povinná pole.")
        if not vybrane_dny:
            errors.append("Vyberte alespoň jeden den pobytu.")
        if not souhlas:
            errors.append("Souhlas je povinný.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # Označení dní jako obsazené
            for den in vybrane_dny:
                st.session_state.obsazene_dny.add(den)
            st.success(f"Rezervace na dny {', '.join(vybrane_dny)} byla úspěšná! 🏡")

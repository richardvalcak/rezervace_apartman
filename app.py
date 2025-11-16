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

# --- Formulář rezervace ---
with st.form("rezervace_form"):
    st.subheader("1. Osoba")
    j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
    n1 = st.text_input("Datum narození *", placeholder="15. 6. 1985")
    a1 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno")
    d1 = st.text_input("Doklad *", placeholder="123456789 (OP)")

    st.markdown("---")
    st.subheader("Výběr období pobytu")
    
    # Výběr období pomocí dvojice date_input
    dnes = datetime.today().date()
    default_start = dnes
    default_end = dnes + timedelta(days=1)
    
    start_date, end_date = st.date_input(
        "Vyberte období pobytu",
        value=(default_start, default_end),
        min_value=dnes
    )

    st.markdown("---")
    souhlas = st.checkbox("Souhlasím se zpracováním osobních údajů podle výše uvedeného textu.")

    submitted = st.form_submit_button("ODESLAT REZERVACI")

    if submitted:
        errors = []
        if not all([j1.strip(), n1.strip(), a1.strip(), d1.strip()]):
            errors.append("Vyplňte všechna povinná pole.")
        if start_date > end_date:
            errors.append("Konec období musí být po začátku.")
        if not souhlas:
            errors.append("Souhlas je povinný.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # Generování všech dní v období
            rezervovane_dny = []
            delta = end_date - start_date
            for i in range(delta.days + 1):
                den = start_date + timedelta(days=i)
                den_str = den.strftime("%Y-%m-%d")
                st.session_state.obsazene_dny.add(den_str)
                rezervovane_dny.append(den_str)
            
            st.success(f"Rezervace na dny {', '.join(rezervovane_dny)} byla úspěšná! 🏡")

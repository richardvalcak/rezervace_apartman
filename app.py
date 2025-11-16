# app.py – Rezervační systém Apartmán Tyršova
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Rezervace Apartmán Tyršova",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Kniha hostů – Rezervace Apartmánu Tyršova")

# === Úvodní text ===
st.markdown("""
Prosíme vás o vyplnění této knihy hostů.  
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.  
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.  
**Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo**
""")

# === Session storage ===
if "rezervace_data" not in st.session_state:
    # příklad dostupnosti a cen – později načíst z Google Sheets
    dnes = datetime.today()
    st.session_state.rezervace_data = {}
    for i in range(30):  # příštích 30 dní
        den = (dnes + timedelta(days=i)).strftime("%Y-%m-%d")
        st.session_state.rezervace_data[den] = {"cena": 1000 + i*10, "volno": True}

# === Admin sekce (nastavení cen a dostupnosti) ===
with st.expander("🔧 Admin – Správa cen a dostupnosti", expanded=False):
    den_admin = st.selectbox("Vyber den", list(st.session_state.rezervace_data.keys()))
    cena_admin = st.number_input("Cena za noc (Kč)", min_value=0, value=st.session_state.rezervace_data[den_admin]["cena"])
    volno_admin = st.checkbox("Volný", value=st.session_state.rezervace_data[den_admin]["volno"])
    if st.button("Uložit nastavení", key="save_admin"):
        st.session_state.rezervace_data[den_admin]["cena"] = cena_admin
        st.session_state.rezervace_data[den_admin]["volno"] = volno_admin
        st.success(f"Nastavení pro {den_admin} bylo uloženo.")

# === Host – výběr data ===
st.subheader("Rezervace pobytu")
volne_dny = [den for den, info in st.session_state.rezervace_data.items() if info["volno"]]

if not volne_dny:
    st.warning("Všechny dny jsou již obsazené.")
else:
    vybrany_den = st.selectbox("Vyberte den pobytu", volne_dny)
    cena = st.session_state.rezervace_data[vybrany_den]["cena"]
    st.info(f"Cena za noc: {cena} Kč")

    # Formulář hosta
    with st.form("rezervace_form"):
        jmeno = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
        telefon = st.text_input("Telefon *", placeholder="+420 777 123 456")
        email = st.text_input("Email *", placeholder="jan@seznam.cz")
        souhlas = st.checkbox(
            "Souhlasím se zpracováním osobních údajů podle výše uvedeného textu.",
            value=False
        )
        poznamka = st.text_area("Poznámka (volitelné)")

        submitted = st.form_submit_button("Potvrdit rezervaci")
        if submitted:
            errors = []
            if not jmeno.strip():
                errors.append("Zadejte jméno a příjmení.")
            if not telefon.strip():
                errors.append("Zadejte telefon.")
            if not email.strip():
                errors.append("Zadejte platný email.")
            if not souhlas:
                errors.append("Souhlas je povinný.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                # označíme den jako obsazený
                st.session_state.rezervace_data[vybrany_den]["volno"] = False
                st.success(f"Rezervace na den {vybrany_den} byla potvrzena! Cena: {cena} Kč")
                st.write("Údaje hosta:")
                st.write(f"- Jméno: {jmeno}")
                st.write(f"- Telefon: {telefon}")
                st.write(f"- Email: {email}")
                if poznamka.strip():
                    st.write(f"- Poznámka: {poznamka}")

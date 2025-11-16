# app.py – Rezervační systém | Apartmán Tyršova | 2025
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

# === Formulář ===
with st.form("rezervace_form"):

    pocet_osob = st.selectbox("Počet osob *", [1, 2], index=0)

    st.subheader("1. Osoba")
    j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
    n1 = st.text_input("Datum narození *", placeholder="15. 6. 1985")
    a1 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno")
    d1 = st.text_input("Doklad *", placeholder="123456789 (OP)")

    if pocet_osob == 2:
        st.subheader("2. Osoba")
        j2 = st.text_input("Jméno a příjmení *", placeholder="Marie Nováková", key="j2")
        n2 = st.text_input("Datum narození *", placeholder="20. 8. 1990", key="n2")
        a2 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno", key="a2")
        d2 = st.text_input("Doklad *", placeholder="987654321 (OP)", key="d2")

    st.markdown("---")
    st.subheader("Výběr dne pobytu")

    # Výběr měsíce
    dnes = datetime.today()
    mesic = st.selectbox(
        "Vyberte měsíc",
        [dnes.strftime("%Y-%m"), (dnes.replace(day=1) + timedelta(days=30)).strftime("%Y-%m")]
    )

    # Inicializace dat – volné dny (demo)
    if "rezervace_data" not in st.session_state:
        st.session_state.rezervace_data = {}  # klíč = "YYYY-MM-DD", hodnota = True/False
    rok, mesic_c = map(int, mesic.split("-"))
    _, pocet_dni = calendar.monthrange(rok, mesic_c)
    for d in range(1, pocet_dni + 1):
        den = datetime(rok, mesic_c, d).strftime("%Y-%m-%d")
        if den not in st.session_state.rezervace_data:
            st.session_state.rezervace_data[den] = True  # True = volno

    st.subheader(f"Dostupné dny v {mesic}")

    # Rozdělení dnů do týdnů
    dny_mesice = [datetime(rok, mesic_c, i+1).strftime("%Y-%m-%d") for i in range(pocet_dni)]
    weeks = [dny_mesice[i:i+7] for i in range(0, len(dny_mesice), 7)]
    vybrane_dny = []

    for week in weeks:
        cols = st.columns(7)
        for idx, den_str in enumerate(week):
            den_date = datetime.strptime(den_str, "%Y-%m-%d")
            weekday = calendar.day_name[den_date.weekday()][:3]
            label = f"{den_date.day} ({weekday})"

            # Volno / obsazeno
            if st.session_state.rezervace_data[den_str]:
                if cols[idx].checkbox(label, key=den_str):
                    vybrane_dny.append(den_str)
            else:
                cols[idx].markdown(f"<span style='color:red'>❌ {den_date.day}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.checkbox(
        "**Souhlasím se zpracováním osobních údajů podle výše uvedeného textu**",
        key="souhlas"
    )

    submitted = st.form_submit_button("ODESLAT REZERVACI")

    if submitted:
        errors = []
        if not j1.strip() or not n1.strip() or not a1.strip() or not d1.strip():
            errors.append("Vyplňte všechna povinná pole 1. osoby.")
        if pocet_osob == 2:
            if not j2.strip() or not n2.strip() or not a2.strip() or not d2.strip():
                errors.append("Vyplňte všechna povinná pole 2. osoby.")
        if not vybrane_dny:
            errors.append("Vyberte alespoň jeden den pobytu.")
        if not st.session_state.get("souhlas", False):
            errors.append("Souhlas je povinný.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # Označíme vybrané dny jako obsazené
            for den in vybrane_dny:
                st.session_state.rezervace_data[den] = False

            st.success("Rezervace byla úspěšně odeslána!")
            st.write("Vybrané dny:", vybrane_dny)
            st.write("Osoba 1:", j1, n1, a1, d1)
            if pocet_osob == 2:
                st.write("Osoba 2:", j2, n2, a2, d2)

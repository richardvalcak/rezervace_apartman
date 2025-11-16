import streamlit as st
from datetime import datetime, timedelta, date
import calendar

st.set_page_config(page_title="Rezervace – Apartmán Tyršova", layout="wide")
st.title("Kniha hostů")

st.markdown("""
Prosíme vás o vyplnění této knihy hostů.  
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.  
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.  
**Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo**
""")

# --- Inicializace obsazených dní ---
if "obsazene_dny" not in st.session_state:
    st.session_state.obsazene_dny = set()
    # Příklad: obsazené dny
    st.session_state.obsazene_dny.update(["2025-11-20", "2025-11-21", "2025-11-23"])

# --- Formulář rezervace ---
with st.form("rezervace_form"):
    st.subheader("1. Osoba")
    j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
    n1 = st.text_input("Datum narození *", placeholder="15. 6. 1985")
    a1 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno")
    d1 = st.text_input("Doklad *", placeholder="123456789 (OP)")

    st.markdown("---")
    st.subheader("Kalendář dostupnosti (volné a obsazené dny)")

    # --- Nastavení období pro zobrazení kalendáře ---
    dnes = date.today()
    mesice = []
    for i in range(3):  # zobrazíme 3 měsíce
        rok = (dnes.replace(day=1) + timedelta(days=30*i)).year
        mesic = (dnes.replace(day=1) + timedelta(days=30*i)).month
        mesice.append((rok, mesic))

    # --- Zobrazení kalendáře po měsících ---
    vybrane_start = None
    vybrane_end = None
    for rok, mesic in mesice:
        st.markdown(f"### {calendar.month_name[mesic]} {rok}")
        cal = calendar.Calendar(firstweekday=0)
        dni_tydne = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]

        cols = st.columns(7)
        for idx, d in enumerate(dni_tydne):
            cols[idx].markdown(f"**{d}**")

        # generování dní
        dni = cal.itermonthdays(rok, mesic)
        row = []
        for d in dni:
            if d == 0:
                row.append(st.empty())
            else:
                datum = date(rok, mesic, d)
                datum_str = datum.strftime("%Y-%m-%d")
                if datum_str in st.session_state.obsazene_dny:
                    btn = st.button(f"❌ {d}", disabled=True, key=f"{datum_str}")
                else:
                    btn = st.button(f"✅ {d}", key=f"{datum_str}")
                    if btn:
                        if not vybrane_start:
                            vybrane_start = datum
                            vybrane_end = datum
                        else:
                            if datum < vybrane_start:
                                vybrane_start = datum
                            else:
                                vybrane_end = datum

    st.markdown("---")
    souhlas = st.checkbox("Souhlasím se zpracováním osobních údajů podle výše uvedeného textu.")

    submitted = st.form_submit_button("ODESLAT REZERVACI")

    if submitted:
        errors = []
        if not all([j1.strip(), n1.strip(), a1.strip(), d1.strip()]):
            errors.append("Vyplňte všechna povinná pole.")
        if not vybrane_start or not vybrane_end:
            errors.append("Vyberte období pobytu.")
        if not souhlas:
            errors.append("Souhlas je povinný.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # označení rezervovaných dní
            delta = vybrane_end - vybrane_start
            rezervovane_dny = []
            for i in range(delta.days + 1):
                den = vybrane_start + timedelta(days=i)
                den_str = den.strftime("%Y-%m-%d")
                st.session_state.obsazene_dny.add(den_str)
                rezervovane_dny.append(den_str)
            st.success(f"Rezervace na dny {', '.join(rezervovane_dny)} byla úspěšná! 🏡")

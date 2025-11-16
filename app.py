# app.py – Rezervační systém Apartmán Tyršova s měsíčním kalendářem
import streamlit as st
from datetime import datetime, timedelta
import calendar

st.set_page_config(
    page_title="Rezervace Apartmán Tyršova",
    layout="wide",
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

# === Inicializace session ===
if "rezervace_data" not in st.session_state:
    dnes = datetime.today()
    st.session_state.rezervace_data = {}
    # vytvoření dat pro příští 2 měsíce
    for i in range(60):
        den = dnes + timedelta(days=i)
        den_str = den.strftime("%Y-%m-%d")
        st.session_state.rezervace_data[den_str] = {"cena": 1000 + i*10, "volno": True}

# === Admin sekce ===
with st.expander("🔧 Admin – Správa cen a dostupnosti", expanded=False):
    den_admin = st.selectbox("Vyber den", list(st.session_state.rezervace_data.keys()))
    cena_admin = st.number_input("Cena za noc (Kč)", min_value=0, value=st.session_state.rezervace_data[den_admin]["cena"])
    volno_admin = st.checkbox("Volný", value=st.session_state.rezervace_data[den_admin]["volno"])
    if st.button("Uložit nastavení", key="save_admin"):
        st.session_state.rezervace_data[den_admin]["cena"] = cena_admin
        st.session_state.rezervace_data[den_admin]["volno"] = volno_admin
        st.success(f"Nastavení pro {den_admin} bylo uloženo.")

# === Výběr měsíce ===
st.subheader("Rezervace pobytu")

dnes = datetime.today()
mesic = st.selectbox("Vyberte měsíc", [dnes.strftime("%Y-%m"), (dnes + timedelta(days=30)).strftime("%Y-%m")])

# filtrovat dny pro vybraný měsíc
vybrane_dny_m = [den for den in st.session_state.rezervace_data.keys() if den.startswith(mesic)]
volne_dny = [den for den in vybrane_dny_m if st.session_state.rezervace_data[den]["volno"]]

# === Kalendar – checkboxy po dnech ===
st.markdown(f"### Dostupné dny v {mesic}")
vybrane_dny_host = []
col_count = 7
for i, den_str in enumerate(volne_dny):
    den_date = datetime.strptime(den_str, "%Y-%m-%d")
    weekday = calendar.day_name[den_date.weekday()][:3]  # např. Mon, Tue
    col = st.columns(col_count)[i % col_count]
    with col:
        if st.checkbox(f"{weekday} {den_date.day}", key=den_str):
            vybrane_dny_host.append(den_str)

# === Dynamická cena ===
celkova_cena = sum([st.session_state.rezervace_data[den]["cena"] for den in vybrane_dny_host])
st.info(f"Celková cena za pobyt: {celkova_cena} Kč")

# === Formulář hosta ===
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
        if not jmeno.strip(): errors.append("Zadejte jméno a příjmení.")
        if not telefon.strip(): errors.append("Zadejte telefon.")
        if not email.strip(): errors.append("Zadejte platný email.")
        if not souhlas: errors.append("Souhlas je povinný.")
        if not vybrane_dny_host: errors.append("Vyberte alespoň jeden den pobytu.")

        if errors:
            for e in errors: st.error(e)
        else:
            # označit dny jako obsazené
            for den in vybrane_dny_host:
                st.session_state.rezervace_data[den]["volno"] = False

            st.success(f"Rezervace potvrzena na {len(vybrane_dny_host)} dní, celková cena: {celkova_cena} Kč")
            st.write("Údaje hosta:")
            st.write(f"- Jméno: {jmeno}")
            st.write(f"- Telefon: {telefon}")
            st.write(f"- Email: {email}")
            if poznamka.strip(): st.write(f"- Poznámka: {poznamka}")

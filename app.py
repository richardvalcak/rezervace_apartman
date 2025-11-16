import streamlit as st
from datetime import date, datetime, timedelta

st.set_page_config(page_title="Rezervace Apartmánu Tyršova", layout="centered")

# --- Nadpis a úvod ---
st.title("Kniha hostů – Rezervace Apartmánu Tyršova")
st.markdown("""
Prosíme vás o vyplnění této knihy hostů.  
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.  
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.  
**Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo**
""")

st.markdown("---")

# --- Inicializace session ---
if 'rezervace_data' not in st.session_state:
    st.session_state['rezervace_data'] = {}

# --- Formulář rezervace ---
with st.form("rezervace_form"):

    # --- Osobní údaje ---
    st.subheader("1️⃣ Osobní údaje hosta")
    col1, col2 = st.columns(2)
    with col1:
        jmeno = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
        telefon = st.text_input("Telefon *", placeholder="+420 777 123 456")
    with col2:
        email = st.text_input("Email *", placeholder="jan@seznam.cz")
        adresa = st.text_input("Adresa (volitelné)", placeholder="Hlavní 123, Brno")

    # --- Počet osob ---
    pocet_osob = st.number_input("Počet osob", min_value=1, max_value=10, value=1)

    # --- Dynamicky zobrazit pole pro druhou osobu, pokud je více osob ---
    osoby = [{"jmeno": jmeno, "telefon": telefon, "email": email, "adresa": adresa}]
    for i in range(2, pocet_osob + 1):
        st.markdown(f"---\n### Osoba {i}")
        col1, col2 = st.columns(2)
        with col1:
            j = st.text_input(f"Jméno a příjmení {i}", placeholder=f"Marie Nováková {i}")
            t = st.text_input(f"Telefon {i}", placeholder=f"+420 777 123 45{i}")
        with col2:
            e = st.text_input(f"Email {i}", placeholder=f"m{i}@seznam.cz")
            a = st.text_input(f"Adresa {i} (volitelné)", placeholder=f"Hlavní 123, Brno")
        osoby.append({"jmeno": j, "telefon": t, "email": e, "adresa": a})

    # --- Informace o pobytu ---
    st.subheader("2️⃣ Informace o pobytu")
    col1, col2 = st.columns(2)
    with col1:
        prichod = st.date_input("Příjezd *", min_value=date.today())
    with col2:
        odjezd = st.date_input("Odjezd *", min_value=date.today() + timedelta(days=1))

    cena_noc = st.number_input("Cena za noc (Kč)", min_value=500, value=1200)
    cena_celkem = st.number_input("Individuální cena (Kč)", min_value=0, value=cena_noc * ((odjezd - prichod).days) * pocet_osob)

    poznamka = st.text_area("Poznámka / speciální požadavky")

    # --- Souhlas ---
    st.markdown("---")
    st.subheader("3️⃣ Souhlas")
    st.markdown("""
Souhlasím se zpracováním mých osobních údajů (jméno, příjmení, adresa, datum narození a údaje o pobytu)  
pro účely evidence ubytování v Apartmánu Tyršova, v souladu se zákonem č. 101/2000 Sb., o ochraně osobních údajů, a nařízení GDPR (EU) 2016/679.  
Souhlas je udělen dobrovolně a lze jej kdykoli odvolat.
""")
    souhlas = st.checkbox("Souhlasím se zpracováním osobních údajů podle výše uvedeného textu.")

    submitted = st.form_submit_button("Rezervovat")

    # --- Validace ---
    if submitted:
        errors = []
        for idx, osoba in enumerate(osoby, start=1):
            if not osoba["jmeno"] or not osoba["telefon"] or not osoba["email"]:
                errors.append(f"Vyplňte všechny kontaktní údaje pro osobu {idx}.")
        if prichod >= odjezd:
            errors.append("Odjezd musí být po příjezdu.")
        if cena_celkem <= 0:
            errors.append("Cena musí být větší než 0.")
        if not souhlas:
            errors.append("Souhlas je povinný.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # --- Uložíme do session ---
            st.session_state['rezervace_data'] = {
                "osoby": osoby,
                "prichod": prichod,
                "odjezd": odjezd,
                "cena_noc": cena_noc,
                "cena_celkem": cena_celkem,
                "poznamka": poznamka,
                "cas_rezervace": datetime.now()
            }

            # --- Souhrn pro hosta i majitele ---
            st.success("✅ Rezervace byla zaznamenána!")
            st.markdown("### Souhrn rezervace")
            st.write(f"**Počet osob:** {pocet_osob}")
            for idx, osoba in enumerate(osoby, start=1):
                st.write(f"**Osoba {idx}:** {osoba['jmeno']}, {osoba['telefon']}, {osoba['email']}, {osoba['adresa']}")
            st.write(f"**Příjezd:** {prichod}")
            st.write(f"**Odjezd:** {odjezd}")
            st.write(f"**Cena za noc:** {cena_noc} Kč")
            st.write(f"**Individuální cena:** {cena_celkem} Kč")
            st.write(f"**Poznámka:** {poznamka}")
            st.write(f"**Čas rezervace:** {datetime.now().strftime('%d.%m.%Y %H:%M')}")

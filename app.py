import streamlit as st
from datetime import datetime
import calendar

# Příklad měsíce – může být nahrazen výběrem uživatele
dnes = datetime.today()
mesic = st.selectbox("Vyberte měsíc", [dnes.strftime("%Y-%m"), (dnes.replace(day=1) + timedelta(days=30)).strftime("%Y-%m")])

# Inicializace dat pro demo
if "rezervace_data" not in st.session_state:
    st.session_state.rezervace_data = {}
    rok, mesic_c = map(int, mesic.split("-"))
    _, pocet_dni = calendar.monthrange(rok, mesic_c)
    for d in range(1, pocet_dni + 1):
        den = datetime(rok, mesic_c, d).strftime("%Y-%m-%d")
        st.session_state.rezervace_data[den] = {"volno": True, "cena": 1000}

# === Kalendář ===
st.subheader(f"Dostupné dny v {mesic}")

rok, mesic_c = map(int, mesic.split("-"))
prvni_den_mesice, pocet_dni_mesice = calendar.monthrange(rok, mesic_c)

dny_mesice = [datetime(rok, mesic_c, i+1).strftime("%Y-%m-%d") for i in range(pocet_dni_mesice)]
weeks = [dny_mesice[i:i+7] for i in range(0, len(dny_mesice), 7)]
vybrane_dny_host = []

for week in weeks:
    cols = st.columns(7)
    for idx, den_str in enumerate(week):
        den_date = datetime.strptime(den_str, "%Y-%m-%d")
        weekday = calendar.day_name[den_date.weekday()][:3]
        label = f"{den_date.day} ({weekday})"
        if st.session_state.rezervace_data[den_str]["volno"]:
            if cols[idx].checkbox(label, key=den_str):
                vybrane_dny_host.append(den_str)
        else:
            cols[idx].write(f"❌ {den_date.day}")

st.write("Vybrané dny:", vybrane_dny_host)

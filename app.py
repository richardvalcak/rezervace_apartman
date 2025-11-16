import calendar

st.subheader(f"Dostupné dny v {mesic}")

# Parsování měsíce
rok, mesic_c = map(int, mesic.split("-"))
prvni_den_mesice, pocet_dni_mesice = calendar.monthrange(rok, mesic_c)

# připravit list dní
dny_mesice = []
for i in range(pocet_dni_mesice):
    den = datetime(rok, mesic_c, i+1)
    den_str = den.strftime("%Y-%m-%d")
    dny_mesice.append(den_str)

# Vytvoření kalendáře po týdnech
weeks = [dny_mesice[i:i+7] for i in range(0, len(dny_mesice), 7)]
vybrane_dny_host = []

for week in weeks:
    cols = st.columns(7)
    for idx, den_str in enumerate(week):
        den_date = datetime.strptime(den_str, "%Y-%m-%d")
        weekday = calendar.day_name[den_date.weekday()][:3]  # např. Mon, Tue
        label = f"{den_date.day} ({weekday})"
        if st.session_state.rezervace_data[den_str]["volno"]:
            if cols[idx].checkbox(label, key=den_str):
                vybrane_dny_host.append(den_str)
        else:
            cols[idx].write(f"❌ {den_date.day}")

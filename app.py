import streamlit as st
from datetime import datetime, timedelta
import calendar
import requests
from icalendar import Calendar

st.set_page_config(page_title="Dostupnost Apartmánu", layout="wide")
st.title("Dostupnost Apartmánu Tyršova")

# iCal URL z Booking.com
ICAL_URL = "https://ical.booking.com/v1/export?t=641d7a68-4a90-4d73-b223-2668d2d33476"

# načtení obsazených dní
obsazene_dny = []
try:
    response = requests.get(ICAL_URL)
    cal = Calendar.from_ical(response.content)
    for component in cal.walk():
        if component.name == "VEVENT":
            start = component.get('dtstart').dt
            end = component.get('dtend').dt
            current = start
            while current < end:
                obsazene_dny.append(current)
                current += timedelta(days=1)
except:
    st.warning("Nepodařilo se načíst iCal z Booking.com")

# české názvy dnů a měsíců
dny_tydne = ['Po','Út','St','Čt','Pá','So','Ne']
mesice_cz = ["","leden","únor","březen","duben","květen","červen","červenec","srpen","září","říjen","listopad","prosinec"]

def zobraz_kalendar(start_date, months=3):  # změněno na 3 měsíce
    for m in range(months):
        # posun o m měsíců od start_date
        year = start_date.year + ((start_date.month + m -1)//12)
        month = (start_date.month + m -1)%12 +1
        st.markdown(f"### {mesice_cz[month]} {year}")

        cal = calendar.Calendar(firstweekday=0)
        dni_mesice = list(cal.itermonthdates(year, month))

        table_html = """
        <style>
            .calendar-table {border-collapse: collapse; width: 100%; text-align: center;}
            .calendar-table th, .calendar-table td {padding:5px;}
            .calendar-table td {border-radius:5px; color:white; margin:2px;}
            @media (max-width: 600px) {
                .calendar-table td {padding: 5px; font-size:12px;}
            }
        </style>
        <table class='calendar-table'>
        """

        # hlavička dnů
        table_html += "<tr>"
        for dn in dny_tydne:
            table_html += f"<th>{dn}</th>"
        table_html += "</tr>"

        # řádky týdnů
        for i in range(0, len(dni_mesice), 7):
            table_html += "<tr>"
            for den in dni_mesice[i:i+7]:
                if den.month != month:
                    table_html += "<td></td>"
                else:
                    barva = "#81c995" if den not in obsazene_dny else "#f28b82"
                    table_html += f"<td style='background-color:{barva}; padding:8px;'>{den.day}</td>"
            table_html += "</tr>"

        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)

# zobrazit kalendář 3 měsíce od dneška
zobraz_kalendar(datetime.today(), months=6)

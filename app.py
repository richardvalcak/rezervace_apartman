import streamlit as st
from datetime import datetime, timedelta, date
import calendar 
import requests
from icalendar import Calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Rezervace Apartmánu Tyršova", layout="wide")

ICAL_URL = "https://ical.booking.com/v1/export?t=641d7a68-4a90-4d73-b223-2668d2d33476"
SMTP_HOST = st.secrets.get("SMTP_HOST", "smtp.wedos.net")
SMTP_PORT = int(st.secrets.get("SMTP_PORT", 465))
SMTP_USER = st.secrets.get("SMTP_USER", "info@apartmantyrsova.cz")
SMTP_PASS = st.secrets.get("SMTP_PASS", "")
NOTIFY_EMAIL = st.secrets.get("NOTIFY_EMAIL", "info@apartmantyrsova.cz")

@st.cache_data(ttl=900)
def nacti_obsazene_dny():
    obsazene = set()
    try:
        response = requests.get(ICAL_URL, timeout=10)
        cal = Calendar.from_ical(response.content)
        for component in cal.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                end = component.get('dtend').dt
                if isinstance(start, datetime):
                    start = start.date()
                if isinstance(end, datetime):
                    end = end.date()
                current = start
                while current < end:
                    obsazene.add(current)
                    current += timedelta(days=1)
    except Exception as e:
        st.warning(f"Nepodařilo se načíst obsazenost: {e}")
    return obsazene

if "lokalni_rezervace" not in st.session_state:
    st.session_state.lokalni_rezervace = set()

def vsechny_obsazene():
    return nacti_obsazene_dny() | st.session_state.lokalni_rezervace

def posli_email(jmeno, email_hosta, telefon, prijezd, odjezd, pocet_osob, zprava):
    if not SMTP_PASS:
        return False, "SMTP heslo není nastaveno"
    try:
        pocet_noci = (odjezd - prijezd).days
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Nova poptavka - {prijezd.strftime('%d.%m.%Y')} az {odjezd.strftime('%d.%m.%Y')}"
        msg["From"] = SMTP_USER
        msg["To"] = NOTIFY_EMAIL
        text = f"Jmeno: {jmeno}\nEmail: {email_hosta}\nTelefon: {telefon}\nPrijezd: {prijezd}\nOdjezd: {odjezd}\nNoci: {pocet_noci}\nOsob: {pocet_osob}\nZprava: {zprava}"
        msg.attach(MIMEText(text, "plain", "utf-8"))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, NOTIFY_EMAIL, msg.as_string())
        return True, "OK"
    except Exception as e:
        return False, str(e)

dny_tydne_cz = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
mesice_cz = ["","leden","únor","březen","duben","květen","červen",
             "červenec","srpen","září","říjen","listopad","prosinec"]

def zobraz_kalendar(obsazene, start_date, months=6):
    for m in range(months):
        year = start_date.year + ((start_date.month + m - 1) // 12)
        month = (start_date.month + m - 1) % 12 + 1
        st.markdown(f"### {mesice_cz[month]} {year}")
        cal = calendar.Calendar(firstweekday=0)
        dni_mesice = list(cal.itermonthdates(year, month))
        table_html = "<style>.cal-table{border-collapse:collapse;width:100%;text-align:center;max-width:400px;}.cal-table th{padding:6px;font-size:13px;color:#555;}.cal-table td{padding:8px;border-radius:6px;font-size:14px;font-weight:500;}</style>"
        table_html += "<table class='cal-table'><tr>" + "".join(f"<th>{d}</th>" for d in dny_tydne_cz) + "</tr>"
        dnes = date.today()
        for i in range(0, len(dni_mesice), 7):
            table_html += "<tr>"
            for den in dni_mesice[i:i+7]:
                if den.month != month:
                    table_html += "<td></td>"
                elif den < dnes:
                    table_html += f"<td style='color:#ccc;'>{den.day}</td>"
                elif den in obsazene:
                    table_html += f"<td style='background:#f28b82;color:white;'>{den.day}</td>"
                else:
                    table_html += f"<td style='background:#81c995;color:white;'>{den.day}</td>"
            table_html += "</tr>"
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)

st.title("Apartmán Tyršova – Znojmo")
st.markdown("**Přímá rezervace bez poplatků**")

obsazene = vsechny_obsazene()

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("Obsazenost")
    st.markdown("""
    <div style='display:flex;gap:16px;margin-bottom:12px;font-size:14px;'>
      <span style='background:#81c995;color:white;padding:3px 10px;border-radius:4px;'>volno</span>
      <span style='background:#f28b82;color:white;padding:3px 10px;border-radius:4px;'>obsazeno</span>
    </div>
    """, unsafe_allow_html=True)
    zobraz_kalendar(obsazene, datetime.today(), months=6)

with col2:
    st.subheader("Poptávka rezervace")
    st.info("Vyplňte formulář a ozveme se vám do 24 hodin s potvrzením a platebními údaji.")

    if st.session_state.get("odeslano"):
        st.success("Poptávka odeslána! Brzy se vám ozveme s potvrzením a platebními údaji.")
        if st.button("Nová rezervace"):
            st.session_state.odeslano = False
            st.rerun()
    else:
        dnes = date.today()

        jmeno = st.text_input("Jméno a příjmení *")
        email_hosta = st.text_input("Email *")
        telefon = st.text_input("Telefon *")
        prijezd = st.date_input("Datum příjezdu *",
                                 value=dnes + timedelta(days=7),
                                 min_value=dnes,
                                 format="DD/MM/YYYY")
        odjezd = st.date_input("Datum odjezdu *",
                                value=dnes + timedelta(days=10),
                                min_value=dnes + timedelta(days=1),
                                format="DD/MM/YYYY")
        pocet_osob = st.selectbox("Počet osob *", [1, 2])
        zprava = st.text_area("Zpráva / dotaz (nepovinné)", height=80)

        if st.button("Odeslat poptávku", type="primary", use_container_width=True):
            chyby = []
            if not jmeno:
                chyby.append("Jméno je povinné")
            if not email_hosta or "@" not in email_hosta:
                chyby.append("Zadejte platný email")
            if not telefon:
                chyby.append("Telefon je povinný")
            if prijezd >= odjezd:
                chyby.append("Datum odjezdu musí být po datu příjezdu")

            konflikt = []
            current = prijezd
            while current < odjezd:
                if current in obsazene:
                    konflikt.append(current.strftime('%d. %m.'))
                current += timedelta(days=1)
            if konflikt:
                chyby.append(f"Termín není volný – obsazené dny: {', '.join(konflikt)}")

            if chyby:
                for ch in chyby:
                    st.error(ch)
            else:
                ok, msg = posli_email(jmeno, email_hosta, telefon, prijezd, odjezd, pocet_osob, zprava)
                if ok:
                    current = prijezd
                    while current < odjezd:
                        st.session_state.lokalni_rezervace.add(current)
                        current += timedelta(days=1)
                    st.session_state.odeslano = True
                    st.rerun()
                else:
                    st.error(f"Chyba při odesílání emailu: {msg}")

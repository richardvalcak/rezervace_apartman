import streamlit as st
from datetime import datetime, timedelta, date
import calendar 
import requests
from icalendar import Calendar
import sendgrid
from sendgrid.helpers.mail import Mail

st.set_page_config(page_title="Rezervace Apartmánu Tyršova", layout="wide")

ICAL_URL = "https://ical.booking.com/v1/export?t=641d7a68-4a90-4d73-b223-2668d2d33476"
NOTIFY_EMAIL = st.secrets.get("NOTIFY_EMAIL", "info@apartmantyrsova.cz")
FROM_EMAIL = st.secrets.get("FROM_EMAIL", "info@apartmantyrsova.cz")

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
    api_key = st.secrets.get("SENDGRID_API_KEY", "")
    if not api_key:
        return False, "SENDGRID_API_KEY není nastaven v secrets"

    try:
        pocet_noci = (odjezd - prijezd).days

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #1a73e8; padding: 20px; border-radius: 8px 8px 0 0;">
                <h2 style="color: white; margin: 0;">🏠 Nová poptávka rezervace</h2>
                <p style="color: #d2e3fc; margin: 5px 0 0 0;">Apartmán Tyršova, Znojmo</p>
            </div>
            <div style="background: #fff; border: 1px solid #dee2e6; border-top: none; border-radius: 0 0 8px 8px; padding: 20px;">
                <table style="width:100%; border-collapse: collapse;">
                    <tr style="background:#f8f9fa;">
                        <td style="padding:8px; color:#666; width:40%;">Jméno</td>
                        <td style="padding:8px;"><b>{jmeno}</b></td>
                    </tr>
                    <tr>
                        <td style="padding:8px; color:#666;">Email</td>
                        <td style="padding:8px;"><a href="mailto:{email_hosta}">{email_hosta}</a></td>
                    </tr>
                    <tr style="background:#f8f9fa;">
                        <td style="padding:8px; color:#666;">Telefon</td>
                        <td style="padding:8px;">{telefon}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px; color:#666;">Příjezd</td>
                        <td style="padding:8px;"><b>{prijezd.strftime('%d.%m.%Y')}</b></td>
                    </tr>
                    <tr style="background:#f8f9fa;">
                        <td style="padding:8px; color:#666;">Odjezd</td>
                        <td style="padding:8px;"><b>{odjezd.strftime('%d.%m.%Y')}</b></td>
                    </tr>
                    <tr>
                        <td style="padding:8px; color:#666;">Počet nocí</td>
                        <td style="padding:8px;">{pocet_noci}</td>
                    </tr>
                    <tr style="background:#f8f9fa;">
                        <td style="padding:8px; color:#666;">Počet osob</td>
                        <td style="padding:8px;">{pocet_osob}</td>
                    </tr>
                    {"<tr><td style='padding:8px; color:#666; vertical-align:top;'>Zpráva</td><td style='padding:8px;'>" + zprava + "</td></tr>" if zprava.strip() else ""}
                </table>
                <p style="color:#888; font-size:12px; margin-top:20px;">
                    Odesláno: {datetime.now().strftime("%d.%m.%Y %H:%M")} | apartmantyrsova.cz
                </p>
            </div>
        </div>
        """

        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=NOTIFY_EMAIL,
            subject=f"Nová poptávka – {jmeno} ({prijezd.strftime('%d.%m.%Y')} – {odjezd.strftime('%d.%m.%Y')}, {pocet_noci} nocí)",
            html_content=html_content
        )

        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        sg.send(message)
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
    st.info("XXXXVyplňte formulář a ozveme se vám do 24 hodin s potvrzením a platebními údaji.")

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
                st.write(f"DEBUG: ok={ok}, msg={msg}")  # dočasně
                if ok:
                    current = prijezd
                    while current < odjezd:
                        st.session_state.lokalni_rezervace.add(current)
                        current += timedelta(days=1)
                    st.session_state.odeslano = True
                    st.rerun()
                else:
                    st.error(f"Chyba při odesílání emailu: {msg}")

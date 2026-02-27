from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import datetime
import time

STREAMLIT_APPS = [
    "https://ubytovani.streamlit.app",
    "https://kniha-tyrsova-znojmo.streamlit.app"
]

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')

def probudit_app(url):
    cas = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    print(f"[{cas}] Zkouším → {url}")
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        driver.get(url)
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        xpath = "//button[contains(., 'Yes, get this app back up') or contains(., 'get this app back up')]"
        try:
            tlacitko = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            tlacitko.click()
            print("   → Kliknuto!")
            time.sleep(10)
            print("   → Probuzeno")
        except TimeoutException:
            print("   → Tlačítko nenalezeno → už běží")
    except Exception as e:
        print(f"   → Chyba: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("=== START ===")
    for url in STREAMLIT_APPS:
        probudit_app(url)
        time.sleep(5)
    print("=== KONEC ===")

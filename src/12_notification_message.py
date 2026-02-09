# src/12_notification_message.py
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")
TASK = "012_notification_message"
PNG_PATH = OUTPUTS_DIR / f"{TS}_{TASK}_success.png"

URL = "https://the-internet.herokuapp.com/notification_message_rendered"

opts = Options()
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 20)

try:
    driver.get(URL)

    intentos = 0
    while True:
        intentos += 1

        # Re-encontrar el link en cada intento (evita stale tras refresh)
        link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Click here")))

        try:
            link.click()
        except StaleElementReferenceException:
            # El DOM cambió justo al click; reintenta el ciclo
            continue

        # Esperar a que exista el mensaje y leerlo
        flash = wait.until(EC.presence_of_element_located((By.ID, "flash")))
        msg = flash.text.strip()

        if "Action successful" in msg:
            driver.save_screenshot(str(PNG_PATH))
            print("OK: notificación exitosa")
            print("INTENTOS:", intentos)
            print("MENSAJE:", msg)
            print("EVIDENCIA:", PNG_PATH)
            break

finally:
    driver.quit()

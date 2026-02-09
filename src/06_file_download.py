from pathlib import Path
from datetime import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = BASE_DIR / "outputs" / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

opts = Options()
opts.add_argument("--start-maximized")
prefs = {
    "download.default_directory": str(DOWNLOADS_DIR),
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
}
opts.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://the-internet.herokuapp.com/download")

    # Toma el primer archivo disponible
    link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#content a")))
    filename = link.text.strip()
    link.click()

    # Espera activa a que el archivo exista (sin sleep fijo)
    target = DOWNLOADS_DIR / filename
    wait.until(lambda d: target.exists())

    print("OK: archivo descargado")
    print("EVIDENCIA:", target)

finally:
    driver.quit()

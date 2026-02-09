# 11_multiple_windows.py
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")
TASK = "011_multiple_windows"

TXT_PATH = OUTPUTS_DIR / f"{TS}_{TASK}_new_window_text.txt"
PNG_PATH = OUTPUTS_DIR / f"{TS}_{TASK}_evidence.png"

URL = "https://the-internet.herokuapp.com/windows"


opts = Options()
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 20)

try:
    driver.get(URL)

    original = driver.current_window_handle

    # Click en "Click Here" para abrir nueva ventana
    click_here = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Click Here")))
    click_here.click()

    # Esperar a que exista una segunda ventana
    wait.until(lambda d: len(d.window_handles) == 2)

    new_handle = [h for h in driver.window_handles if h != original][0]
    driver.switch_to.window(new_handle)

    # Extraer texto de la nueva ventana (normalmente h3 = "New Window")
    header = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h3")))
    text = header.text.strip()

    # Evidencia visual
    driver.save_screenshot(str(PNG_PATH))

    # Exportar texto a .txt (UTF-8)
    TXT_PATH.write_text(text + "\n", encoding="utf-8")

    print("OK: texto extraído de New Window")
    print("TEXTO:", text)
    print("EVIDENCIAS:")
    print(" -", TXT_PATH)
    print(" -", PNG_PATH)

finally:
    driver.quit()

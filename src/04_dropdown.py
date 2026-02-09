from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

def stamp(prefix: str, ext: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return OUTPUTS_DIR / f"{ts}_004_{prefix}.{ext}"

opts = Options()
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://the-internet.herokuapp.com/dropdown")

    dd = wait.until(EC.element_to_be_clickable((By.ID, "dropdown")))
    Select(dd).select_by_value("2")

    shot = stamp("dropdown_option_2", "png")
    driver.save_screenshot(str(shot))

    print("OK: opción 2 seleccionada")
    print("EVIDENCIA:", shot)

finally:
    driver.quit()

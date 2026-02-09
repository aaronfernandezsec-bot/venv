from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

def stamp(prefix: str, ext: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return OUTPUTS_DIR / f"{ts}_001_{prefix}.{ext}"

opts = Options()
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://the-internet.herokuapp.com/add_remove_elements/")

    # Agregar 1 elemento
    add_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick='addElement()']")))
    add_btn.click()

    # Esperar el botón Delete (listo para click)
    delete_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#elements button.added-manually")))

    # Evidencia después de agregar
    shot_added = stamp("add_remove_added", "png")
    driver.save_screenshot(str(shot_added))

    # Borrar 1 elemento
    delete_btn.click()

    # Confirmar que ya no exista ningún Delete
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#elements button.added-manually")) == 0)

    # Evidencia después de borrar
    shot_deleted = stamp("add_remove_deleted", "png")
    driver.save_screenshot(str(shot_deleted))

    print("OK: se agregó 1 elemento y se borró 1 elemento")
    print("EVIDENCIAS:")
    print(" -", shot_added)
    print(" -", shot_deleted)

finally:
    driver.quit()

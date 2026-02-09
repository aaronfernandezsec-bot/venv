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
    return OUTPUTS_DIR / f"{ts}_002_{prefix}.{ext}"

opts = Options()
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://the-internet.herokuapp.com/checkboxes")

    boxes = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='checkbox']"))
    )

    # Objetivo: marcar 1 y desmarcar 2
    if not boxes[0].is_selected():
        boxes[0].click()

    if boxes[1].is_selected():
        boxes[1].click()

    shot = stamp("checkboxes_ok", "png")
    driver.save_screenshot(str(shot))

    print("OK: checkbox 1 marcado, checkbox 2 desmarcado")
    print("EVIDENCIA:", shot)

finally:
    driver.quit()

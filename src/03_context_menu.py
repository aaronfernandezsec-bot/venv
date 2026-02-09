from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

def stamp(prefix: str, ext: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return OUTPUTS_DIR / f"{ts}_003_{prefix}.{ext}"

opts = Options()
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://the-internet.herokuapp.com/context_menu")

    box = wait.until(EC.presence_of_element_located((By.ID, "hot-spot")))

    ActionChains(driver).context_click(box).perform()

    alert = wait.until(EC.alert_is_present())
    alert.accept()

    shot = stamp("context_menu_ok", "png")
    driver.save_screenshot(str(shot))

    print("OK: context menu ejecutado y alerta aceptada")
    print("EVIDENCIA:", shot)

finally:
    driver.quit()

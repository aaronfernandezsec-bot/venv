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

def stamp(prefix: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return OUTPUTS_DIR / f"{ts}_006_dynamic_loading_2_{prefix}.png"

opts = Options()
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://the-internet.herokuapp.com/dynamic_loading/2")

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#start button"))).click()

    hello = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#finish h4")))
    assert hello.text.strip() == "Hello World!", f"Texto inesperado: {hello.text!r}"

    shot = stamp("hello_world")
    driver.save_screenshot(str(shot))

    print("OK: Dynamic Loading 2 -> Hello World!")
    print("EVIDENCIA:", shot)

finally:
    driver.quit()

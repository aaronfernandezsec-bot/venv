# src/08_form_authentication.py

from pathlib import Path
from datetime import datetime
import yaml

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
OUTPUTS_DIR = BASE_DIR / "outputs"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

CRED_FILE = CONFIG_DIR / "credentials.yml"


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# Leer credenciales desde YAML
if not CRED_FILE.exists():
    raise FileNotFoundError(f"No existe el archivo: {CRED_FILE}")

with CRED_FILE.open("r", encoding="utf-8") as f:
    creds = yaml.safe_load(f)

username = creds.get("username")
password = creds.get("password")

if not username or not password:
    raise ValueError("El archivo YAML debe contener username y password")


opts = Options()
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://the-internet.herokuapp.com/login")

    user_input = wait.until(EC.visibility_of_element_located((By.ID, "username")))
    pass_input = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

    user_input.clear()
    user_input.send_keys(username)

    pass_input.clear()
    pass_input.send_keys(password)

    login_btn.click()

    flash = wait.until(EC.visibility_of_element_located((By.ID, "flash")))
    message = flash.text

    if "You logged into a secure area!" not in message:
        raise RuntimeError("Login fallido")

    screenshot_login = OUTPUTS_DIR / f"{timestamp()}_008_login_ok.png"
    driver.save_screenshot(str(screenshot_login))
    print("OK: login correcto")
    print("EVIDENCIA:", screenshot_login)

    logout_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/logout']")))
    logout_btn.click()

    flash_logout = wait.until(EC.visibility_of_element_located((By.ID, "flash")))
    if "You logged out of the secure area!" not in flash_logout.text:
        raise RuntimeError("Logout fallido")

    screenshot_logout = OUTPUTS_DIR / f"{timestamp()}_008_logout_ok.png"
    driver.save_screenshot(str(screenshot_logout))
    print("OK: logout correcto")
    print("EVIDENCIA:", screenshot_logout)

finally:
    driver.quit()

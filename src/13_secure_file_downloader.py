# 13_secure_file_downloader.py
# Descarga testFile.zip desde /download_secure (Basic Auth), extrae DemoFile.txt y genera un PDF con el texto.
# Sin sleeps fijos: usa esperas explícitas/polling.

from __future__ import annotations

import base64
import re
import zipfile
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DOWNLOADS_DIR = OUTPUTS_DIR / "downloads"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://the-internet.herokuapp.com/download_secure"
USERNAME = "admin"
PASSWORD = "admin"


def ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def wait_for_download_complete(wait: WebDriverWait, target_path: Path) -> Path:
    """
    Espera a que:
    - exista el archivo
    - no exista .crdownload
    - el tamaño se estabilice (2 lecturas iguales)
    """
    tmp = target_path.with_suffix(target_path.suffix + ".crdownload")

    def _done(_driver) -> bool:
        if tmp.exists():
            return False
        if not target_path.exists():
            return False
        try:
            s1 = target_path.stat().st_size
        except OSError:
            return False
        if s1 <= 0:
            return False

        # estabilización rápida de tamaño (sin sleep fijo; el wait reintenta)
        try:
            s2 = target_path.stat().st_size
        except OSError:
            return False
        return s1 == s2

    wait.until(_done)
    return target_path


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    return name or "download.bin"


def make_simple_pdf(text: str, out_path: Path) -> None:
    """
    PDF mínimo (sin librerías externas).
    Escribe 1 página con Helvetica y el texto (multilínea).
    """
    # Escapar caracteres especiales de PDF strings
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines:
        lines = [""]

    # Construir el stream de texto (posición inicial y salto de línea)
    y_start = 760
    x_start = 50
    line_h = 14

    content_lines = [f"BT /F1 12 Tf {x_start} {y_start} Td"]
    for i, line in enumerate(lines[:55]):  # límite razonable para una página
        if i == 0:
            content_lines.append(f"({esc(line)}) Tj")
        else:
            content_lines.append(f"0 -{line_h} Td ({esc(line)}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    # Objetos PDF
    objects: list[bytes] = []

    # 1) Catalog
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")

    # 2) Pages
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")

    # 3) Page
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> "
        b"/Contents 5 0 R >>"
    )

    # 4) Font
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    # 5) Contents
    objects.append(
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
    )

    # Escribir archivo con xref
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for i, obj in enumerate(objects, start=1):
            offsets.append(f.tell())
            f.write(f"{i} 0 obj\n".encode())
            f.write(obj)
            f.write(b"\nendobj\n")

        xref_pos = f.tell()
        f.write(b"xref\n")
        f.write(f"0 {len(objects)+1}\n".encode())
        f.write(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            f.write(f"{off:010d} 00000 n \n".encode())

        f.write(b"trailer\n")
        f.write(f"<< /Size {len(objects)+1} /Root 1 0 R >>\n".encode())
        f.write(b"startxref\n")
        f.write(f"{xref_pos}\n".encode())
        f.write(b"%%EOF\n")


def main() -> None:
    opts = Options()
    opts.add_argument("--start-maximized")
    prefs = {
        "download.default_directory": str(DOWNLOADS_DIR),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    opts.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=opts)
    wait = WebDriverWait(driver, 20)

    stamp = ts()
    screenshot_path = OUTPUTS_DIR / f"{stamp}_013_secure_file_downloader_page.png"

    try:
        # ---- Basic Auth sin popup (CDP headers) ----
        token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode("utf-8")).decode("utf-8")
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd(
            "Network.setExtraHTTPHeaders",
            {"headers": {"Authorization": f"Basic {token}"}},
        )

        driver.get(URL)

        # Evidencia de que entró (lista de links)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content a")))
        driver.save_screenshot(str(screenshot_path))

        # ---- Encontrar el link correcto del ZIP (testFile.zip / .zip) ----
        links = driver.find_elements(By.CSS_SELECTOR, "#content a")
        zip_link = None
        zip_name = None

        for a in links:
            name = (a.text or "").strip()
            if name.lower().endswith(".zip") and "testfile" in name.lower().replace("-", ""):
                zip_link = a
                zip_name = name
                break

        # fallback: primer .zip disponible
        if zip_link is None:
            for a in links:
                name = (a.text or "").strip()
                if name.lower().endswith(".zip"):
                    zip_link = a
                    zip_name = name
                    break

        if zip_link is None or not zip_name:
            raise RuntimeError("No encontré ningún archivo .zip en la lista (revisa la página).")

        zip_name = sanitize_filename(zip_name)
        target_zip = DOWNLOADS_DIR / zip_name

        zip_link.click()
        wait_for_download_complete(wait, target_zip)

        # ---- Extraer DemoFile.txt del ZIP ----
        demo_text = None
        demo_member = None

        with zipfile.ZipFile(target_zip, "r") as z:
            members = z.namelist()
            # buscar DemoFile.txt (case-insensitive)
            for m in members:
                if m.lower().endswith("demofile.txt"):
                    demo_member = m
                    break
            if demo_member is None:
                # fallback: cualquier .txt que tenga "demo"
                for m in members:
                    if m.lower().endswith(".txt") and "demo" in m.lower():
                        demo_member = m
                        break
            if demo_member is None:
                raise RuntimeError("El ZIP no contiene DemoFile.txt (ni un .txt con 'demo').")

            demo_text = z.read(demo_member).decode("utf-8", errors="replace")

        # ---- Generar PDF con el texto ----
        pdf_path = OUTPUTS_DIR / f"{stamp}_013_DemoFile_text.pdf"
        make_simple_pdf(demo_text, pdf_path)

        print("OK: login (Basic Auth) + ZIP descargado + DemoFile extraído + PDF generado")
        print("ZIP:", target_zip)
        print("DemoFile:", demo_member)
        print("PDF:", pdf_path)
        print("EVIDENCIA (screenshot):", screenshot_path)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()

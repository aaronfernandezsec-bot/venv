from __future__ import annotations

import os
import sys
import mimetypes
import smtplib
import traceback
from pathlib import Path
from datetime import datetime

from email.message import EmailMessage
from email.utils import formatdate


# =========================
# Config base del proyecto
# =========================
REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"
OUTPUTS_DIR = REPO_ROOT / "outputs"

# Scripts esperados (ajusta si cambias nombres)
SCRIPT_ORDER = [
    "01_add_remove_elements.py",
    "02_checkboxes.py",
    "03_context_menu.py",
    "04_dropdown.py",
    "05_dynamic_loading_1.py",
    "05.2_dynamic_loading_2.py",
    "06_file_download.py",
    "07_file_upload.py",
    "08_form_authentication.py",
    "09_frames_nested_frames.py",
    "10_large_deep_dom.py",
    "11_multiple_windows.py",
    "12_notification_message.py",
    "13_secure_file_downloader.py",
]

# Extensiones / rutas que NO se adjuntan (para no mandar código/repo)
EXCLUDE_EXTS = {
    ".py", ".pyc",
    ".ps1", ".bat", ".cmd",
    ".gitignore", ".gitattributes",
    ".md",  # si quieres adjuntar reportes .md, quita esta línea
}
EXCLUDE_DIR_NAMES = {".git", "venv", ".venv", "__pycache__"}


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def ensure_outputs_folder() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def validate_scripts() -> list[Path]:
    scripts: list[Path] = []
    for name in SCRIPT_ORDER:
        p = SRC_DIR / name
        if not p.exists():
            raise FileNotFoundError(f"No existe el script esperado: {p}")
        scripts.append(p)
    return scripts


def run_script(script_path: Path) -> tuple[int, str]:
    """
    Ejecuta un script en un subproceso para aislar drivers/sesiones.
    Retorna (exit_code, error_text).
    """
    env = os.environ.copy()
    env["PROJECT_ROOT"] = str(REPO_ROOT)
    env["OUTPUT_DIR"] = str(OUTPUTS_DIR)

    # Si estás usando Chrome portable, recomiendo setear esto antes de correr:
    # env["CHROME_BIN"] = r"C:\ruta\chrome.exe"
    # env["CHROMEDRIVER_BIN"] = r"C:\ruta\chromedriver.exe"

    import subprocess

    cmd = [sys.executable, str(script_path)]
    log(f"Ejecutando: {script_path.name}")
    p = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
        capture_output=True,
    )

    # Para que quede registro, imprimimos stdout/stderr del script
    if p.stdout.strip():
        print(p.stdout, end="" if p.stdout.endswith("\n") else "\n", flush=True)

    if p.returncode != 0:
        err = p.stderr.strip() if p.stderr else "(sin stderr)"
        if err:
            print(err, flush=True)
        return p.returncode, err

    return 0, ""


def iter_output_files() -> list[Path]:
    """
    Recolecta todo lo de outputs/ recursivo, excluyendo carpetas y extensiones no deseadas.
    """
    files: list[Path] = []
    if not OUTPUTS_DIR.exists():
        return files

    for p in OUTPUTS_DIR.rglob("*"):
        if p.is_dir():
            continue

        # Excluir directorios “prohibidos” si por alguna razón están adentro
        if any(part in EXCLUDE_DIR_NAMES for part in p.parts):
            continue

        # Excluir por extensión
        if p.suffix.lower() in EXCLUDE_EXTS:
            continue

        files.append(p)

    # Orden estable
    files.sort(key=lambda x: (x.parent.as_posix(), x.name.lower()))
    return files


def build_email(attachments: list[Path], summary: str) -> EmailMessage:
    """
    Arma el correo usando variables de entorno.
    """
    # Requeridos
    mail_to = os.getenv("MAIL_TO", "").strip()
    mail_from = os.getenv("MAIL_FROM", "").strip()
    smtp_user = os.getenv("SMTP_USER", "").strip()  # puede ser igual a MAIL_FROM
    subject = os.getenv("MAIL_SUBJECT", "").strip() or "Entrega automática - outputs Selenium"

    if not mail_to or not mail_from:
        raise RuntimeError("Falta MAIL_TO o MAIL_FROM en variables de entorno.")

    msg = EmailMessage()
    msg["From"] = mail_from
    msg["To"] = mail_to
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    body = (
        "Entrega automática generada por main.py.\n\n"
        f"Resumen:\n{summary}\n\n"
        f"Archivos adjuntos: {len(attachments)}\n"
        f"Timestamp: {datetime.now().isoformat(timespec='seconds')}\n"
    )
    msg.set_content(body)

    for f in attachments:
        ctype, encoding = mimetypes.guess_type(str(f))
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        msg.add_attachment(
            f.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=f.name,
        )

    return msg


def send_email(msg: EmailMessage) -> None:
    """
    Envía correo SMTP (TLS). Credenciales por variables de entorno.
    """
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587").strip())
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASS", "").strip()

    if not smtp_host or not smtp_user or not smtp_pass:
        raise RuntimeError("Faltan SMTP_HOST/SMTP_USER/SMTP_PASS en variables de entorno.")

    log("Enviando correo…")
    with smtplib.SMTP(smtp_host, smtp_port, timeout=60) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    log("Correo enviado correctamente ✅")


def main() -> int:
    """
    Flujo:
      1) Prepara outputs/
      2) Corre scripts
      3) Adjunta todo outputs/
      4) Envía correo al final
    """
    log("Iniciando ejecución del pipeline…")
    ensure_outputs_folder()

    # Nota: aquí NO detectamos Chrome instalado.
    # Si tus scripts dependen de Chrome portable, debes setear CHROME_BIN/CHROMEDRIVER_BIN
    # o manejarlo dentro de tu test_driver.py
    if os.getenv("CHROME_BIN"):
        log("CHROME_BIN configurado (Chrome portable).")
    else:
        log("CHROME_BIN NO configurado. Se espera Chrome portable si así lo requiere tu proyecto.")

    scripts = validate_scripts()

    results: list[tuple[str, int]] = []
    failures: list[str] = []

    for s in scripts:
        code, err = run_script(s)
        results.append((s.name, code))
        if code != 0:
            failures.append(f"{s.name} (exit={code})")
            log(f"⚠️ Falló: {s.name} (exit={code})")

    # =========================
    # Correo SIEMPRE al final
    # =========================
    log("Preparando archivos para correo…")
    files = iter_output_files()
    log(f"Adjuntando {len(files)} archivos…")

    summary_lines = []
    summary_lines.append("Ejecución de scripts:")
    for name, code in results:
        status = "OK" if code == 0 else f"FAIL({code})"
        summary_lines.append(f"- {name}: {status}")

    if failures:
        summary_lines.append("\nFallos detectados:")
        summary_lines.extend([f"- {x}" for x in failures])
    else:
        summary_lines.append("\nSin fallos.")

    summary = "\n".join(summary_lines)

    try:
        msg = build_email(files, summary)
        send_email(msg)
    except Exception as e:
        log("❌ Error enviando correo.")
        print(str(e), flush=True)
        traceback.print_exc()
        # Si el correo es obligatorio para aprobar, devuelve error
        return 2

    log("Proceso terminado ✅")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

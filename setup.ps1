# setup.ps1
# Objetivo: preparar el entorno y VALIDAR requisitos (sin autodetectar Chrome del sistema).
# Requiere: Chrome Portable colocado en .\tools\chrome\chrome.exe

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Step($msg) {
  Write-Host "`n==> $msg" -ForegroundColor Cyan
}

function Ok($msg) {
  Write-Host "✔ $msg" -ForegroundColor Green
}

function Warn($msg) {
  Write-Host "⚠ $msg" -ForegroundColor Yellow
}

function Fail($msg) {
  Write-Host "✖ $msg" -ForegroundColor Red
  exit 1
}

# =========================
# Configuración requerida
# =========================
$REQUIRED_PYTHON_VERSION = "3.10"
$REQUIRED_CHROME_VERSION = "144.0.7559.133"

# RUTA FIJA (Chrome Portable / “móvil” dentro del proyecto)
$CHROME_PORTABLE_PATH = ".\tools\chrome\chrome.exe"

# =========================
# 1) Validar Python
# =========================
Step "Validando Python ($REQUIRED_PYTHON_VERSION.x) y venv..."
$py = & python --version 2>$null
if (-not $py) { Fail "No se pudo ejecutar 'python'. Instala Python $REQUIRED_PYTHON_VERSION.x y asegúrate de tenerlo en PATH." }

Write-Host "Python detectado: $py" -ForegroundColor Gray
if ($py -notmatch "Python $REQUIRED_PYTHON_VERSION(\.\d+)?") {
  Fail "Versión de Python incorrecta. Requerida: $REQUIRED_PYTHON_VERSION.x | Detectada: $py"
}

# Guardar versión exacta detectada en archivo
$pythonExact = ($py -replace "Python\s+", "").Trim()
Set-Content -Path ".\PYTHON_VERSION.txt" -Value $pythonExact
Ok "PYTHON_VERSION.txt actualizado ($pythonExact)"

# =========================
# 2) Activar venv si existe
# =========================
if (Test-Path ".\venv\Scripts\Activate.ps1") {
  Step "Activando venv..."
  . ".\venv\Scripts\Activate.ps1"
  Ok "venv activado"
} else {
  Warn "No existe .\venv\. Si tu flujo requiere venv: crea uno con `n  python -m venv venv"
}

# =========================
# 3) Instalar dependencias (si hay requirements.txt)
# =========================
if (Test-Path ".\requirements.txt") {
  Step "Instalando dependencias desde requirements.txt..."
  python -m pip install --upgrade pip | Out-Null
  python -m pip install -r .\requirements.txt
  Ok "Dependencias instaladas"
} else {
  Warn "No existe requirements.txt (se omitió instalación de dependencias)."
}

# =========================
# 4) Validar Chrome Portable requerido (NO Chrome del sistema)
# =========================
Step "Validando Google Chrome Portable requerido (NO se usa Chrome del sistema)..."
Write-Host "Ruta esperada: $CHROME_PORTABLE_PATH" -ForegroundColor Gray
Write-Host "Versión requerida: $REQUIRED_CHROME_VERSION" -ForegroundColor Gray

if (-not (Test-Path $CHROME_PORTABLE_PATH)) {
  Fail "No se encontró Chrome Portable en: $CHROME_PORTABLE_PATH`nColoca el ejecutable ahí. Se requiere versión $REQUIRED_CHROME_VERSION."
}

$portableVersion = (Get-Item $CHROME_PORTABLE_PATH).VersionInfo.ProductVersion
Write-Host "Chrome Portable encontrado: $portableVersion" -ForegroundColor Gray

if ($portableVersion -ne $REQUIRED_CHROME_VERSION) {
  Fail "Versión incorrecta de Chrome Portable.`nRequerida: $REQUIRED_CHROME_VERSION`nEncontrada: $portableVersion"
}

Set-Content -Path ".\CHROME_VERSION.txt" -Value $portableVersion
Ok "CHROME_VERSION.txt actualizado ($portableVersion)"


# =========================
# 6) Estado final
# =========================
Step "Resumen"
Write-Host "Python exacto:  $pythonExact" -ForegroundColor Gray
Write-Host "Chrome portable: $portableVersion" -ForegroundColor Gray
Ok "Setup completado"

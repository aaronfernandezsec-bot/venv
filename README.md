
---

## 2️⃣ Script automático (opcional pero PRO)

Esto hace que **una sola instrucción** prepare todo.

Crea el archivo:  
📄 `setup.ps1`

Pega esto:

```powershell
Write-Host "Creando entorno virtual..."
python -m venv venv

Write-Host "Activando entorno virtual..."
.\venv\Scripts\Activate.ps1

Write-Host "Actualizando pip..."
pip install --upgrade pip

Write-Host "Instalando dependencias..."
pip install -r requirements.txt

Write-Host "Setup completo. Entorno listo."

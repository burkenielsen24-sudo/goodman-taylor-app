# PowerShell helper to create/activate venv, install deps and run the Streamlit app (local-only)
Set-Location -Path $PSScriptRoot

# Create a virtual environment if it doesn't exist
if (-not (Test-Path -Path ".venv")) {
    Write-Output "Creating virtual environment .venv..."
    python -m venv .venv
}

# Activate the virtual environment if activation script exists
$activateScript = Join-Path -Path $PSScriptRoot -ChildPath ".venv\Scripts\Activate.ps1"
if (Test-Path -Path $activateScript) {
    Write-Output "Activating virtual environment..."
    & $activateScript
} else {
    Write-Output "No virtualenv activate script found; continuing with system Python."
}

# Install requirements if the file exists
if (Test-Path -Path "requirements.txt") {
    Write-Output "Installing requirements (may skip already-installed packages)..."
    pip install -r requirements.txt
}

# Ensure repo root is on PYTHONPATH so `tools.*` imports succeed when running from `app/`
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$repoRoot;$($env:PYTHONPATH)"
} else {
    $env:PYTHONPATH = $repoRoot
}

Write-Output "Starting Streamlit app (local-only) on http://127.0.0.1:8501..."
python -m streamlit run goodman_taylor_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true

if ($LASTEXITCODE -ne 0) {
    Write-Error "Streamlit failed to start. If Streamlit is not installed, run: pip install -r requirements.txt"
    exit $LASTEXITCODE
}

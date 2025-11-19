@echo off
REM Move to the script directory
cd /d "%~dp0"

REM Prefer activating a virtual environment if present
if exist "%~dp0\.venv\Scripts\activate.bat" (
	call "%~dp0\.venv\Scripts\activate.bat"
) else if exist "%~dp0\venv\Scripts\activate.bat" (
	call "%~dp0\venv\Scripts\activate.bat"
) else (
	echo No virtualenv found; continuing with system Python.
)

rem Ensure the repository root is on PYTHONPATH so top-level packages like `tools` import correctly
set "PYTHONPATH=%~dp0..;%PYTHONPATH%"

echo Starting Streamlit app (local-only)...
python -m streamlit run goodman_taylor_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
if %errorlevel% neq 0 (
	echo.
	echo Failed to start Streamlit. If Streamlit is not installed, run:
	echo    pip install -r requirements.txt
	pause
)
exit /b %errorlevel%
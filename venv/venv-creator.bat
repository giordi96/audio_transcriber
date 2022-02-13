@echo off

REM Virtual environment creation
echo Virtual environment creation
python -m venv socomecenv

REM Virtual environment activation
echo Virtual environment activation
call "socomecenv\Scripts\activate"

REM Required libraries installation from requirements.txt
echo Libraries Upgrade/Installation
python -m pip install --upgrade -r requirements/requirements.txt
echo ===================================================
echo Project virtual environment is created and updated: 
echo use it to correctly run Socomec projects.
echo ===================================================
pause
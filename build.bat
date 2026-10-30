call ./.venv/Scripts/activate
pip install -r ./requirements.txt
pyinstaller --onedir --collect-all playwright main.py -y
pause
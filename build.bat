if not exist .venv python -m venv .venv
call .venv\Scripts\activate
python build_release.py
pause

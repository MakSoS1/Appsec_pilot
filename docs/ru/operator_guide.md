# Руководство оператора

## Быстрый запуск

```powershell
cd C:\Users\maksi\Documents\work\appsec-pilot
uv venv .venv
uv pip install -e agent -e backend -e cli
cd frontend
npm install
```

Backend:

```powershell
cd C:\Users\maksi\Documents\work\appsec-pilot\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Frontend:

```powershell
cd C:\Users\maksi\Documents\work\appsec-pilot\frontend
npm run dev -- --host 0.0.0.0 --port 3001
```

## Проверки без Playwright

```powershell
cd C:\Users\maksi\Documents\work\appsec-pilot
.\.venv\Scripts\python.exe -m pytest agent backend cli -q
.\.venv\Scripts\python.exe -m ruff check agent backend cli
cd frontend
npm run build
npm run lint
```

UI smoke можно делать через `curl` и headless Edge screenshots, без Playwright.

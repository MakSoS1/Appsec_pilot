.PHONY: install backend frontend test lint smoke cli-demo lab-up lab-down docker-up docker-down

install:
	uv venv .venv
	uv pip install -e agent -e backend -e cli
	cd frontend && npm install

backend:
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 3001

test:
	cd backend && uv run pytest
	cd agent && uv run pytest
	cd cli && uv run pytest
	cd frontend && npm run build

lint:
	cd backend && uv run ruff check .
	cd agent && uv run ruff check .
	cd cli && uv run ruff check .
	cd frontend && npm run lint

smoke:
	uv run python scripts/smoke_api.py

cli-demo:
	uv run appsec scan --base-url http://localhost:8008 --scope benchmarks/custom_vuln_apps/fastapi_vuln/scope.yaml --wait

lab-up:
	docker compose -f docker-compose.lab.yml up -d

lab-down:
	docker compose -f docker-compose.lab.yml down

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

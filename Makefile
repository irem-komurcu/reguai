install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; source ~/.bashrc; }
	uv sync --dev  --extra jupyter --frozen && npm --prefix frontend install

test:
	uv run pytest tests/unit && uv run pytest tests/integration

playground:
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload &
	npm --prefix frontend start

backend:
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

ui:
	npm --prefix frontend start

setup-dev-env:
	@if [ -z "$$PROJECT_ID" ]; then echo "Error: PROJECT_ID environment variable is not set"; exit 1; fi
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

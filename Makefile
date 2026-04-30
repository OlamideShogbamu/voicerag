.PHONY: install dev dev-frontend dev-backend dev-agents dev-livekit livekit-down build lint bootstrap docker-up docker-down

install:
	pnpm install
	cd apps/backend && uv sync
	cd apps/agents && uv sync

dev:
	pnpm dev

dev-frontend:
	pnpm dev:frontend

dev-backend:
	cd apps/backend && uv run uvicorn app.main:app --reload --port 8000

dev-livekit:
	docker run --rm \
		-p 7890:7880 \
		-p 7891:7881 \
		-p 7892:7882/udp \
		-e LIVEKIT_KEYS="test-devkey: test-secret" \
		livekit/livekit-server --dev

livekit-down:
	docker stop $$(docker ps -q --filter ancestor=livekit/livekit-server) 2>/dev/null || true

dev-agents:
	cd apps/agents && uv run python -m agent.worker download-files
	cd apps/agents && uv run python -m agent.worker dev

build:
	pnpm build

lint:
	pnpm lint

docker-up:
	docker-compose -f infra/compose/docker-compose.dev.yml up postgres

docker-down:
	docker-compose -f infra/compose/docker-compose.dev.yml down

bootstrap:
	@echo "Setting up VoiceRAG development environment..."
	@which pnpm > /dev/null || (echo "Install pnpm: https://pnpm.io/installation" && exit 1)
	@which uv > /dev/null || (echo "Install uv: https://docs.astral.sh/uv/getting-started/installation/" && exit 1)
	cp -n .env.example apps/frontend/.env.local || true
	cp -n .env.example apps/backend/.env || true
	cp -n .env.example apps/agents/.env || true
	pnpm install
	cd apps/backend && uv sync
	cd apps/agents && uv sync
	@echo "Done."

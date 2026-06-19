COMPOSE_FILE := docker-compose.yml
COMPOSE_CMD := podman-compose -f $(COMPOSE_FILE)
APP_CONTAINER := backend

help:
	@echo "Hypertube - Available commands:"
	@echo ""
	@echo "  make run             - Start all services"
	@echo "  make stop            - Stop all services"
	@echo "  make logs            - Show service logs (Ctrl+C to exit)"
	@echo "  make logs-app        - Show app logs only"
	@echo "  make logs-db         - Show database logs only"
	@echo "  make build           - Rebuild all images"
	@echo "  make clean           - Stop and remove containers, volumes, images"
	@echo "  make shell           - Access app container shell"
	@echo "  make test            - Run unit tests (95%+ coverage)"
	@echo "  make test-docker     - Run tests inside Docker container - (unavailable)"
	@echo "  make test-coverage   - Run tests with HTML coverage report"
	@echo "  make migrate         - Run database migrations"
	@echo ""

run:
	$(COMPOSE_CMD) up --build
	@echo "✓ Services started"

stop:
	$(COMPOSE_CMD) down
	@echo "✓ Services removed"

logs:
	$(COMPOSE_CMD) logs -f

logs-app:
	$(COMPOSE_CMD) logs -f app

logs-db:
	$(COMPOSE_CMD) logs -f db

build:
	$(COMPOSE_CMD) build
	@echo "✓ Images rebuilt"

clean:
	if docker container ls -q | grep -q .; then \
		$(COMPOSE_CMD) down -v --remove-orphans; \
		echo "✓ Containers and volumes removed"; \
	else \
		echo "No running containers to remove. Cleanup completed."; \
	fi
	$(COMPOSE_CMD) down -v --remove-orphans
	@echo "✓ All containers and volumes removed"

fclean: clean
	if docker images -q | grep -q .; then \
		docker rmi -f $$(docker images -q); \
		docker system prune -af --volumes && docker network prune -f; \
		echo "✓ Full cleanup completed"; \
	else \
		echo "No Docker images to remove. Full cleanup completed."; \
	fi

shell:
	docker exec -it $(APP_CONTAINER) /bin/sh

test:
	@if command -v pytest &> /dev/null; then \
		pytest tests/ -v --tb=short; \
	else \
		echo "pytest not found in PATH. Would you like to:"; \
		echo "  1. Run: pip install -r app/requirements.txt"; \
# 		echo "  2. Or use Docker: make dockers-test"; \
		exit 1; \
	fi

# test-docker:
# 	docker exec $(APP_CONTAINER) pytest tests/ -v --tb=short

test-coverage:
	@if command -v pytest &> /dev/null; then \
		pytest tests/ --cov=app --cov-report=html --cov-report=term-missing; \
		echo "✓ Coverage report generated in htmlcov/"; \
	else \
		echo "pytest not found. Run: pip install -r app/requirements.txt"; \
		exit 1; \
	fi

test-coverage-docker:
	docker exec $(APP_CONTAINER) pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
	@echo "✓ Coverage report generated in htmlcov/"

migrate:
	docker exec $(APP_CONTAINER) flask db upgrade

.PHONY: help run stop logs logs-app logs-db build clean shell test test-coverage migrate
.DEFAULT_GOAL := help
.SILENT:
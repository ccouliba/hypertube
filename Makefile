COMPOSE_FILE := docker-compose.yml

ifndef COMPOSE_CMD
ifneq ($(shell if command -v podman-compose >/dev/null 2>&1 && command -v podman >/dev/null 2>&1; then echo yes; fi),)
COMPOSE_CMD := podman-compose -f $(COMPOSE_FILE)
else
COMPOSE_CMD := docker compose -f $(COMPOSE_FILE)
endif
endif
APP_SERVICE := app

ifeq ($(NO_COLOR),1)
GREEN :=
RED :=
RESET :=
else
GREEN := \033[0;32m
RED := \033[0;31m
RESET := \033[0m
endif

define RUN
	@printf "[RUN] %s...\n" "$(1)"
	@if $(2); then \
		printf "$(GREEN)[OK]$(RESET) %s\n" "$(1)"; \
	else \
		printf "$(RED)[NO]$(RESET) %s\n" "$(1)"; \
		exit 1; \
	fi
endef

help:
	@echo "Hypertube - Available commands:"
	@echo ""
	@echo "  make run             - Start all services"
	@echo "  make stop            - Stop all services"
	@echo "  make logs            - Show service logs (Ctrl+C to exit)"
	@echo "  make logs-app        - Show app logs only"
	@echo "  make logs-db         - Show database logs only"
	@echo "  make build           - Rebuild all images"
	@echo "  make clean           - Stop and remove containers and volumes"
	@echo "  make fclean          - Stop services, remove volumes and local images"
	@echo "  make shell           - Access app container shell"
	@echo "  make test            - Run unit tests (95%+ coverage)"
	@echo "  make test-coverage   - Run tests with HTML coverage report"
	@echo "  make migrate         - Run database migrations"
	@echo ""

run:
	$(call RUN,Démarrage des services,$(COMPOSE_CMD) up --build)

stop:
	$(call RUN,Arrêt des services,$(COMPOSE_CMD) down)

logs:
	$(call RUN,Affichage des logs,$(COMPOSE_CMD) logs -f)

logs-app:
	$(call RUN,Affichage des logs du backend,$(COMPOSE_CMD) logs -f app)

logs-db:
	$(call RUN,Affichage des logs de la base de données,$(COMPOSE_CMD) logs -f database)

build:
	$(call RUN,Reconstruction des images,$(COMPOSE_CMD) build)

clean:
	$(call RUN,Nettoyage des conteneurs et volumes,$(COMPOSE_CMD) down -v --remove-orphans)

fclean:
	$(call RUN,Nettoyage complet du projet,$(COMPOSE_CMD) down -v --remove-orphans --rmi local)

shell:
	$(call RUN,Ouvrir un shell dans le backend,$(COMPOSE_CMD) exec $(APP_SERVICE) /bin/sh)

test:
	$(call RUN,Exécution des tests,pytest tests/ -v --tb=short)

test-coverage:
	$(call RUN,Exécution des tests avec couverture,pytest tests/ --cov=app --cov-report=html --cov-report=term-missing)

migrate:
	$(call RUN,Application des migrations,$(COMPOSE_CMD) exec $(APP_SERVICE) flask db upgrade)

.PHONY: help run stop logs logs-app logs-db build clean fclean shell test test-coverage migrate
.DEFAULT_GOAL := help
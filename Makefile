.PHONY: help build up down logs shell migrate makemigrations collectstatic test coverage coverage-local coverage-report clean restart logs-test install

# Ajuda - mostra todos os comandos disponíveis
help:
	@echo "=== Comandos disponíveis ==="
	@echo ""
	@echo "🐳 Docker:"
	@echo "  build           - Constroi as imagens Docker" 
	@echo "  up              - Sobe os containers em background"
	@echo "  down            - Para e remove os containers"
	@echo "  restart         - Para e sobe os containers novamente"
	@echo "  logs            - Mostra logs do container web"
	@echo "  logs-test       - Mostra logs do container de teste"
	@echo "  shell           - Abre terminal no container web"
	@echo "  clean           - Remove containers, volumes e imagens órfãs"
	@echo ""
	@echo "🎯 Django:"
	@echo "  migrate         - Executa migrações do Django"
	@echo "  makemigrations  - Cria novas migrações"
	@echo "  collectstatic   - Coleta arquivos estáticos"
	@echo ""
	@echo "🧪 Testes:"
	@echo "  test            - Executa todos os testes"
	@echo "  coverage        - Executa testes com relatório de coverage"
	@echo "  coverage-local  - Coverage fora do Docker"
	@echo "  coverage-report - Abre relatório HTML do coverage"
	@echo ""
	@echo "⚡ Desenvolvimento:"
	@echo "  install         - Setup inicial do projeto"

# Docker commands
build:
	@echo "🔨 Construindo imagens Docker..."
	docker-compose build

up:
	@echo "🚀 Subindo containers..."
	docker-compose up -d
	@echo "✅ Containers rodando!"

down:
	@echo "🛑 Parando containers..."
	docker-compose down
	@echo "✅ Containers parados!"

logs:
	@echo "📋 Logs do container web:"
	docker-compose logs -f web

logs-test:
	@echo "📋 Logs do container de teste:"
	docker-compose logs -f test

shell:
	@echo "🐚 Abrindo shell no container web..."
	docker-compose exec web bash

# Django commands
migrate:
	@echo "📊 Executando migrações..."
	docker-compose exec web python manage.py migrate
	@echo "✅ Migrações concluídas!"

makemigrations:
	@echo "📝 Criando migrações..."
	docker-compose exec web python manage.py makemigrations
	@echo "✅ Migrações criadas!"

collectstatic:
	@echo "📦 Coletando arquivos estáticos..."
	docker-compose exec web python manage.py collectstatic --noinput
	@echo "✅ Arquivos estáticos coletados!"

# Testing
test:
	@echo "🧪 Executando testes..."
	docker-compose run --rm test
	@echo "✅ Testes concluídos!"

# Coverage dentro do Docker (usando pytest)
coverage:
	@echo "📊 Executando testes com coverage..."
	docker-compose run --rm test pytest --cov=. --cov-report=html --cov-report=term
	@echo "✅ Coverage concluído! Veja o relatório em htmlcov/index.html"

# Coverage local (se quiser rodar fora do Docker)
coverage-local:
	@echo "📊 Executando coverage local..."
	coverage erase
	coverage run --source='.' manage.py test
	coverage report
	coverage html
	@echo "✅ Relatório HTML gerado em htmlcov/index.html"

# Ver relatório de coverage
coverage-report:
	@echo "🌐 Abrindo relatório de coverage..."
	@if [ -f htmlcov/index.html ]; then \
		python -m webbrowser htmlcov/index.html; \
	else \
		echo "❌ Rode 'make coverage' primeiro"; \
	fi

# Setup inicial do projeto
install: build
	@echo "🏗️  Setup inicial do projeto..."
	docker-compose run --rm web python manage.py migrate
	@echo "✅ Projeto configurado! Use 'make up' para subir os containers"

# Comandos úteis
clean:
	@echo "🧹 Limpando containers e imagens órfãs..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Limpeza concluída!"

restart: down up
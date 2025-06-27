.PHONY: help build up down restart logs shell clean backup

# Default target
help:
	@echo "Available commands:"
	@echo "  build    - Build the Docker image"
	@echo "  up       - Start the application"
	@echo "  down     - Stop the application"
	@echo "  restart  - Restart the application"
	@echo "  logs     - View application logs"
	@echo "  shell    - Access container shell"
	@echo "  clean    - Remove containers and images"
	@echo "  backup   - Backup the database"
	@echo "  status   - Show container status"

# Build the Docker image
build:
	docker-compose build --no-cache

# Start the application
up:
	docker-compose up -d

# Stop the application
down:
	docker-compose down

# Restart the application
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

# Access container shell
shell:
	docker-compose exec jobsearch-app bash

# Clean up containers and images
clean:
	docker-compose down --rmi all --volumes --remove-orphans

# Backup database
backup:
	@echo "Creating database backup..."
	docker-compose exec jobsearch-app cp /app/instance/jobsearch.db /app/instance/jobsearch_backup_$$(date +%Y%m%d_%H%M%S).db
	@echo "Backup created successfully"

# Show container status
status:
	docker-compose ps

# Update and restart
update:
	git pull
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

PYTHON=python3
IMAGE_NAME=pexa
IMAGE_TAG=latest

.PHONY: test install format lint clean venv help db-init build run stop logs

# Run tests
test:
	PYTHONPATH=. $(PYTHON) -m pytest $(TEST) -v

# Install production dependencies
install:
	$(PYTHON) -m pip install pip --upgrade
	$(PYTHON) -m pip install -r requirements.txt

# Format code with Black
format:
	$(PYTHON) -m black app/ tests/

# Check code formatting
lint:
	$(PYTHON) -m black --check app/ tests/

# Create virtual environment if it doesn't exist
venv:
	@if [ ! -d "env" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv env; \
		echo "Virtual environment created at ./env"; \
		echo "Activate it with: source env/bin/activate"; \
	else \
		echo "Virtual environment already exists at ./env"; \
	fi

# Clean up cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Build Docker image
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Deploy with docker compose (pexa + caddy)
run:
	docker compose up -d

# Stop docker compose deployment
stop:
	docker compose down

# Tail logs from all services
logs:
	docker compose logs -f

# Setup db for manual testing
db-init:
	./bin/init_db.sh

# Show help
help:
	@echo "Available commands:"
	@echo "  test        - Run tests"
	@echo "  install     - Install production dependencies"
	@echo "  format      - Format code with Black"
	@echo "  lint        - Check code formatting"
	@echo "  venv        - Create virtual environment if it doesn't exist"
	@echo "  clean       - Clean up cache files"
	@echo "  help        - Show this help message"
	@echo "  db-init     - Setup user for manual testing (NOTE: needs api running)"
	@echo "  build       - Build Docker image (IMAGE_NAME=pexa IMAGE_TAG=latest)"
	@echo "  run         - Deploy with docker compose (pexa + caddy)"
	@echo "  stop        - Stop docker compose deployment"
	@echo "  logs        - Tail logs from all services"

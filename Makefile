PYTHON=python3

.PHONY: test install format lint clean venv help

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

# Show help
help:
	@echo "Available commands:"
	@echo "  test        - Run tests"
	@echo "  install     - Install production dependencies"
	@echo "  dev-install - Install development dependencies"
	@echo "  format      - Format code with Black"
	@echo "  lint        - Check code formatting"
	@echo "  venv        - Create virtual environment if it doesn't exist"
	@echo "  clean       - Clean up cache files"
	@echo "  help        - Show this help message"

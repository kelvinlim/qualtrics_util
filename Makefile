# Makefile for qualtrics_util project

# Variables
PYTHON := python
PYINSTALLER := pyinstaller
SRC := qualtrics_util.py
SPEC := qualtrics-util.spec
DIST_DIR := dist
BUILD_DIR := build
BINARY_NAME := qualtrics-util

# Targets
.PHONY: all build clean help install test install-deps

all: install-deps build

help:
	@echo "Qualtrics Util - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make install-deps    - Install all dependencies"
	@echo "  make build           - Build executable with PyInstaller"
	@echo "  make build-linux     - Build Linux executable"
	@echo "  make build-macos     - Build macOS executable"
	@echo "  make build-windows   - Build Windows executable (requires Wine)"
	@echo "  make test            - Run tests"
	@echo "  make clean           - Remove build artifacts"
	@echo ""

install-deps:
	@echo "Installing dependencies..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install pyinstaller

build:
	@echo "Building executable..."
	$(PYINSTALLER) $(SPEC) --clean
	@echo "Build complete! Executable is in $(DIST_DIR)/$(BINARY_NAME)"

build-linux:
	@echo "Building for Linux..."
	docker run --rm -v "$$(pwd)":/workspace -w /workspace python:3.11-slim bash -c \
		"pip install -r requirements.txt && pip install pyinstaller && pyinstaller $(SPEC) --clean"

build-macos:
	@echo "Building for macOS..."
	# Note: Run this on a macOS machine
	$(PYINSTALLER) $(SPEC) --clean
	@echo "Build complete for macOS!"

build-windows:
	@echo "Building for Windows..."
	# Note: Run this on a Windows machine or use Wine on Linux
	docker run --rm -v "$$(pwd)":/workspace -w /workspace python:3.11-windowsservercore bash -c \
		"pip install -r requirements.txt && pip install pyinstaller && pyinstaller $(SPEC) --clean"

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v

clean:
	@echo "Cleaning up..."
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	find . -name "*.spec" -not -name "$(SPEC)" -delete
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	@echo "Cleanup complete."

check-executable:
	@echo "Checking executable..."
	@if [ -f "$(DIST_DIR)/$(BINARY_NAME)" ]; then \
		echo "Executable exists"; \
		file $(DIST_DIR)/$(BINARY_NAME); \
		./$(DIST_DIR)/$(BINARY_NAME) --version; \
	else \
		echo "Executable not found. Run 'make build' first."; \
	fi

install:
	@echo "Installing package..."
	$(PYTHON) -m pip install -e .

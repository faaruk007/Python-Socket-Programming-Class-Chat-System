# Makefile for ClassChat Project
# Author: Md Farukuzzaman Faruk
# ULID: C00605733
# Course: CSCE-513, Fall 2025
# University of Louisiana at Lafayette

# Python interpreter
PYTHON = python3
PIP = pip3

# Project name
PROJECT = ClassChat

# Virtual environment
VENV = venv
VENV_BIN = $(VENV)/bin
VENV_PYTHON = $(VENV_BIN)/python
VENV_PIP = $(VENV_BIN)/pip

# Project files
LAUNCHER = launcher.py
SERVER = server.py
CLIENT = client.py

# Database file
DB_FILE = classchat.db

# Requirements
REQUIREMENTS = requirements.txt

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
MAGENTA = \033[0;35m
CYAN = \033[0;36m
NC = \033[0m # No Color

.DEFAULT_GOAL := help

.PHONY: help install setup venv run server client launcher clean cleanall test check package

# ============================================================================
# HELP & INFO
# ============================================================================

## Show help message
help:
	@echo "$(CYAN)╔══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║         ClassChat Project - Makefile Help              ║$(NC)"
	@echo "$(CYAN)║    Multi-threaded Chat with RSA-2048 + AES-256         ║$(NC)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Installation & Setup:$(NC)"
	@echo "  $(YELLOW)make install$(NC)      - Install dependencies (system-wide)"
	@echo "  $(YELLOW)make venv$(NC)         - Create virtual environment"
	@echo "  $(YELLOW)make setup$(NC)        - Full setup (venv + install)"
	@echo ""
	@echo "$(GREEN)Running Application:$(NC)"
	@echo "  $(YELLOW)make run$(NC)          - Run launcher (GUI control panel)"
	@echo "  $(YELLOW)make launcher$(NC)     - Run launcher (same as 'make run')"
	@echo "  $(YELLOW)make server$(NC)       - Run server only"
	@echo "  $(YELLOW)make client$(NC)       - Run client only"
	@echo ""
	@echo "$(GREEN)Database Management:$(NC)"
	@echo "  $(YELLOW)make db-init$(NC)      - Initialize database"
	@echo "  $(YELLOW)make db-clean$(NC)     - Delete database"
	@echo "  $(YELLOW)make db-reset$(NC)     - Reset database (clean + init)"
	@echo "  $(YELLOW)make db-backup$(NC)    - Backup database"
	@echo ""
	@echo "$(GREEN)Testing & Quality:$(NC)"
	@echo "  $(YELLOW)make test$(NC)         - Run tests"
	@echo "  $(YELLOW)make check$(NC)        - Check dependencies"
	@echo "  $(YELLOW)make lint$(NC)         - Run code linter"
	@echo ""
	@echo "$(GREEN)Cleaning:$(NC)"
	@echo "  $(YELLOW)make clean$(NC)        - Remove cache and temp files"
	@echo "  $(YELLOW)make cleanall$(NC)     - Remove everything (cache, db, venv)"
	@echo ""
	@echo "$(GREEN)Packaging:$(NC)"
	@echo "  $(YELLOW)make package$(NC)      - Create distribution zip"
	@echo "  $(YELLOW)make submission$(NC)   - Create submission package"
	@echo ""
	@echo "$(BLUE)Quick Start:$(NC)"
	@echo "  1. $(YELLOW)make setup$(NC)     # First time setup"
	@echo "  2. $(YELLOW)make run$(NC)       # Start the application"
	@echo ""

## Show project information
info:
	@echo "$(CYAN)Project Information:$(NC)"
	@echo "  Name:        $(PROJECT)"
	@echo "  Author:      Md Farukuzzaman Faruk"
	@echo "  ULID:        C00605733"
	@echo "  Course:      CSCE-513"
	@echo "  Python:      $(shell $(PYTHON) --version 2>&1)"
	@echo "  Database:    $(DB_FILE)"
	@echo ""

# ============================================================================
# INSTALLATION & SETUP
# ============================================================================

## Install dependencies (system-wide)
install:
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Installing Dependencies$(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r $(REQUIREMENTS)
	@echo "$(GREEN)✓ Dependencies installed successfully$(NC)"
	@echo ""

## Create virtual environment
venv:
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created: $(VENV)$(NC)"
	@echo "$(YELLOW)Activate with: source $(VENV_BIN)/activate$(NC)"
	@echo ""

## Full setup (create venv and install dependencies)
setup: venv
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Setting up ClassChat Project$(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install -r $(REQUIREMENTS)
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo ""
	@echo "$(YELLOW)To activate virtual environment:$(NC)"
	@echo "  source $(VENV_BIN)/activate"
	@echo ""
	@echo "$(YELLOW)To run the application:$(NC)"
	@echo "  make run"
	@echo ""

# ============================================================================
# RUNNING APPLICATION
# ============================================================================

## Run launcher (GUI control panel)
run: check-deps
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Starting ClassChat Launcher$(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@$(PYTHON) $(LAUNCHER)

## Run launcher (alias for 'run')
launcher: run

## Run server only
server: check-deps
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Starting ClassChat Server$(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(YELLOW)Server will start on 127.0.0.1:5555$(NC)"
	@$(PYTHON) $(SERVER)

## Run client only
client: check-deps
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Starting ClassChat Client$(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@$(PYTHON) $(CLIENT)

## Run multiple clients (specify number with N=3)
clients: check-deps
	@echo "$(BLUE)Starting $(or $(N),2) client instances...$(NC)"
	@for i in $$(seq 1 $(or $(N),2)); do \
		echo "$(YELLOW)Starting client $$i...$(NC)"; \
		$(PYTHON) $(CLIENT) & \
		sleep 0.5; \
	done
	@echo "$(GREEN)✓ All clients started$(NC)"

# ============================================================================
# DATABASE MANAGEMENT
# ============================================================================

## Initialize database
db-init:
	@echo "$(BLUE)Initializing database...$(NC)"
	@$(PYTHON) -c "from database import Database; db = Database(); print('✓ Database initialized')"
	@echo "$(GREEN)✓ Database ready: $(DB_FILE)$(NC)"

## Delete database
db-clean:
	@echo "$(YELLOW)Deleting database...$(NC)"
	@rm -f $(DB_FILE)
	@echo "$(GREEN)✓ Database deleted$(NC)"

## Reset database (delete and reinitialize)
db-reset: db-clean db-init
	@echo "$(GREEN)✓ Database reset complete$(NC)"

## Backup database
db-backup:
	@if [ -f $(DB_FILE) ]; then \
		BACKUP_FILE="$(DB_FILE).backup.$$(date +%Y%m%d_%H%M%S)"; \
		cp $(DB_FILE) $$BACKUP_FILE; \
		echo "$(GREEN)✓ Database backed up: $$BACKUP_FILE$(NC)"; \
	else \
		echo "$(YELLOW)No database file found$(NC)"; \
	fi

## Show database info
db-info:
	@if [ -f $(DB_FILE) ]; then \
		echo "$(CYAN)Database Information:$(NC)"; \
		echo "  File: $(DB_FILE)"; \
		echo "  Size: $$(du -h $(DB_FILE) | cut -f1)"; \
		echo "  Modified: $$(stat -c %y $(DB_FILE) 2>/dev/null || stat -f %Sm $(DB_FILE))"; \
	else \
		echo "$(YELLOW)Database not found. Run 'make db-init' to create.$(NC)"; \
	fi

# ============================================================================
# TESTING & QUALITY
# ============================================================================

## Check if all dependencies are installed
check-deps:
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@$(PYTHON) -c "import cryptography" 2>/dev/null && \
		echo "$(GREEN)✓ cryptography$(NC)" || \
		echo "$(RED)✗ cryptography - Run 'make install'$(NC)"
	@$(PYTHON) -c "from PIL import Image" 2>/dev/null && \
		echo "$(GREEN)✓ Pillow$(NC)" || \
		echo "$(RED)✗ Pillow - Run 'make install'$(NC)"
	@$(PYTHON) -c "import psutil" 2>/dev/null && \
		echo "$(GREEN)✓ psutil$(NC)" || \
		echo "$(RED)✗ psutil - Run 'make install'$(NC)"
	@echo ""

## Check system requirements
check:
	@echo "$(CYAN)System Requirements Check:$(NC)"
	@echo "$(BLUE)Python Version:$(NC)"
	@$(PYTHON) --version
	@echo ""
	@echo "$(BLUE)Installed Packages:$(NC)"
	@$(PIP) list | grep -E "cryptography|Pillow|psutil|pycryptodome" || echo "No packages installed"
	@echo ""
	@echo "$(BLUE)Project Files:$(NC)"
	@ls -lh *.py 2>/dev/null || echo "No Python files found"
	@echo ""

## Run tests (if test file exists)
test:
	@echo "$(BLUE)Running tests...$(NC)"
	@if [ -f "test_classchat.py" ]; then \
		$(PYTHON) -m pytest test_classchat.py -v; \
	else \
		echo "$(YELLOW)No test file found. Create test_classchat.py to run tests.$(NC)"; \
	fi

## Run code linter (requires pylint)
lint:
	@echo "$(BLUE)Running linter...$(NC)"
	@which pylint > /dev/null 2>&1 && \
		pylint *.py --disable=C0111,C0103 || \
		echo "$(YELLOW)pylint not installed. Install with: pip install pylint$(NC)"

## Format code (requires black)
format:
	@echo "$(BLUE)Formatting code...$(NC)"
	@which black > /dev/null 2>&1 && \
		black *.py || \
		echo "$(YELLOW)black not installed. Install with: pip install black$(NC)"

# ============================================================================
# CLEANING
# ============================================================================

## Remove Python cache and temporary files
clean:
	@echo "$(YELLOW)Cleaning cache and temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf .pytest_cache 2>/dev/null || true
	@echo "$(GREEN)✓ Cache and temporary files removed$(NC)"

## Remove everything (cache, database, venv, backups)
cleanall: clean
	@echo "$(RED)WARNING: This will remove database, virtual environment, and all generated files!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(YELLOW)Removing all files...$(NC)"; \
		rm -f $(DB_FILE); \
		rm -f $(DB_FILE).backup.*; \
		rm -rf $(VENV); \
		rm -f *.zip; \
		echo "$(GREEN)✓ All files removed$(NC)"; \
	else \
		echo "$(BLUE)Cancelled$(NC)"; \
	fi

# ============================================================================
# PACKAGING & DISTRIBUTION
# ============================================================================

## Create distribution package
package: clean
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Creating Distribution Package$(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@mkdir -p dist
	@zip -r dist/ClassChat_v1.0.zip \
		*.py \
		$(REQUIREMENTS) \
		*.png \
		*.md \
		README.md 2>/dev/null || true
	@echo "$(GREEN)✓ Package created: dist/ClassChat_v1.0.zip$(NC)"
	@ls -lh dist/ClassChat_v1.0.zip

## Create submission package (includes documentation)
submission: clean
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Creating Submission Package$(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	ZIPNAME="ClassChat_Faruk_C00605733_$$TIMESTAMP.zip"; \
	zip -r $$ZIPNAME \
		*.py \
		$(REQUIREMENTS) \
		*.png \
		*.md \
		Makefile \
		README.md 2>/dev/null || true; \
	echo "$(GREEN)✓ Submission package created: $$ZIPNAME$(NC)"; \
	ls -lh $$ZIPNAME

## Install as system command (creates 'classchat' command)
install-cmd:
	@echo "$(BLUE)Installing ClassChat command...$(NC)"
	@echo '#!/bin/bash' > /tmp/classchat
	@echo 'cd $(shell pwd) && python3 launcher.py' >> /tmp/classchat
	@chmod +x /tmp/classchat
	@sudo mv /tmp/classchat /usr/local/bin/classchat
	@echo "$(GREEN)✓ ClassChat installed! Run with: classchat$(NC)"

# ============================================================================
# DEVELOPMENT UTILITIES
# ============================================================================

## Show all TODO comments in code
todos:
	@echo "$(CYAN)TODO items in code:$(NC)"
	@grep -rn "TODO\|FIXME\|XXX" *.py 2>/dev/null || echo "No TODOs found"

## Count lines of code
loc:
	@echo "$(CYAN)Lines of Code:$(NC)"
	@wc -l *.py | sort -n
	@echo ""
	@echo "$(CYAN)Total Python Code:$(NC)"
	@find . -name "*.py" -type f -exec wc -l {} + | tail -1

## Show project statistics
stats:
	@echo "$(CYAN)Project Statistics:$(NC)"
	@echo "  Python files:    $$(find . -name "*.py" -type f | wc -l)"
	@echo "  Total lines:     $$(find . -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $$1}')"
	@echo "  Database size:   $$(du -h $(DB_FILE) 2>/dev/null | cut -f1 || echo 'N/A')"
	@echo "  Dependencies:    $$(wc -l < $(REQUIREMENTS))"

## Open project in VS Code
code:
	@which code > /dev/null 2>&1 && \
		code . || \
		echo "$(YELLOW)VS Code not found$(NC)"

## Open project in PyCharm
pycharm:
	@which pycharm > /dev/null 2>&1 && \
		pycharm . || \
		echo "$(YELLOW)PyCharm command not found$(NC)"

# ============================================================================
# DEMO & PRESENTATION
# ============================================================================

## Run demo (server + 2 clients)
demo: check-deps
	@echo "$(MAGENTA)════════════════════════════════════════$(NC)"
	@echo "$(MAGENTA)  ClassChat Demo Mode$(NC)"
	@echo "$(MAGENTA)════════════════════════════════════════$(NC)"
	@echo "$(YELLOW)Starting server...$(NC)"
	@$(PYTHON) $(SERVER) & sleep 2
	@echo "$(YELLOW)Starting 2 clients...$(NC)"
	@$(PYTHON) $(CLIENT) & sleep 1
	@$(PYTHON) $(CLIENT) &
	@echo "$(GREEN)✓ Demo started: 1 server + 2 clients$(NC)"

## Kill all ClassChat processes
kill:
	@echo "$(YELLOW)Stopping all ClassChat processes...$(NC)"
	@pkill -f "$(SERVER)" 2>/dev/null || true
	@pkill -f "$(CLIENT)" 2>/dev/null || true
	@pkill -f "$(LAUNCHER)" 2>/dev/null || true
	@echo "$(GREEN)✓ All processes stopped$(NC)"

# ============================================================================
# END OF MAKEFILE
# ============================================================================

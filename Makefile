PYTHON ?= python3
PACKAGE = econsim

.PHONY: install lint format type test-unit perf manual-tests launcher enhanced-tests batch-tests bookmarks test tests clean venv token token-analysis token-analysis-full

# Create canonical development virtual environment (vmt-dev) and install deps
.PHONY: venv
venv:
	@if [ -d "vmt-dev" ]; then \
		echo "[venv] Existing vmt-dev directory detected; skipping creation."; \
	else \
		python3 -m venv vmt-dev && echo "[venv] Created vmt-dev virtual environment."; \
	fi
	@. vmt-dev/bin/activate && pip install --upgrade pip >/dev/null 2>&1 && echo "[venv] Upgraded pip." && pip install -e .[dev]
	@echo "[venv] Environment ready. Activate with: source vmt-dev/bin/activate"

install:
	$(PYTHON) -m pip install -e .[dev]


lint:
	ruff check src tests
	black --check src tests
	mdformat --check *.md docs/*.md tmp_plans/**/*.md .github/*.md 2>/dev/null || true

format:
	black src tests
	ruff check --fix src tests || true
	mdformat *.md docs/*.md tmp_plans/**/*.md .github/*.md 2>/dev/null || true

type:
	mypy src

test-unit:
	# Run comprehensive automated unit/integration tests (210+ tests)
	# Includes observer pattern tests, import guards, and modernized architecture validation
	pytest -q

perf:
	@echo "🚀 VMT EconSim Comprehensive Performance Baseline"
	@echo "Running all 7 educational scenarios headless for simulation performance..."
	@if [ -d "vmt-dev" ]; then \
		. vmt-dev/bin/activate && $(PYTHON) tests/performance/baseline_capture.py --steps 1000 --warmup 100; \
	else \
		$(PYTHON) tests/performance/baseline_capture.py --steps 1000 --warmup 100; \
	fi

token:
	# Generate VMT repository token analysis report with full repotokens analysis
	@echo "📄 Generating full token analysis report with timestamp..."
	@if [ -d "vmt-dev" ]; then \
		. vmt-dev/bin/activate && cd llm_counter && $(PYTHON) generate_report.py --timestamp; \
	else \
		cd llm_counter && $(PYTHON) generate_report.py --timestamp; \
	fi
	@echo "✅ Report saved to llm_counter/ with timestamped filename"

launcher:
	# Launch VMT Enhanced Test Launcher with modernized observer-based architecture
	# Launcher logs suppressed by default - set ECONSIM_LAUNCHER_SUPPRESS_LOGS=0 to re-enable.
	# Uses observer pattern for all logging (legacy GUILogger eliminated)
	@if [ -d "vmt-dev" ]; then \
		echo "[launcher] Using virtual environment (observer-based launcher system)."; \
		. vmt-dev/bin/activate && ECONSIM_LAUNCHER_SUPPRESS_LOGS=1 $(PYTHON) -m econsim.gui.launcher.runner; \
	else \
		echo "[launcher] Using system Python (observer-based launcher system)."; \
		ECONSIM_LAUNCHER_SUPPRESS_LOGS=1 $(PYTHON) -m econsim.gui.launcher.runner; \
	fi


visualtest:
	# Launch High Density Local test with visual debugging at 20 FPS
	# Uses TestRunner API for auto-execution with comfortable viewing speed
	@echo "👁️  Visual Test - High Density Local at 20 FPS"
	@echo "Launching Test ID 3 with visual debugging (20 turns/second)..."
	@if [ -d "vmt-dev" ]; then \
		. vmt-dev/bin/activate && $(PYTHON) visual_test_simple.py; \
	else \
		$(PYTHON) visual_test_simple.py; \
	fi


clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	 rm -rf .mypy_cache .ruff_cache .pytest_cache

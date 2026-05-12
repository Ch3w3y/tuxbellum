# Makefile for TuxBellum GTK4
VERSION ?= 3.0.0
RELEASE_TARBALL := tuxbellum-$(VERSION).tar.gz

.PHONY: all build release clean help install

all: build

build:
	@echo "[BUILD] Installing tuxbellum in development mode..."
	pip install -e .

release: clean
	@echo "[RELEASE] Creating release tarball $(RELEASE_TARBALL)..."
	tar -czf $(RELEASE_TARBALL) \
		--exclude='packages/Public Press Kit' \
		src/ \
		packages/ \
		locales/ \
		data/ \
		docs/ \
		scripts/ \
		meson.build \
		pyproject.toml \
		PKGBUILD \
		LICENSE \
		README.md \
		Makefile
	@echo "[RELEASE] Done: $(RELEASE_TARBALL)"

clean:
	@echo "[CLEAN] Removing build artifacts..."
	rm -f $(RELEASE_TARBALL)
	rm -rf build/ dist/ *.egg-info/
	@echo "[CLEAN] Done"

install:
	pip install .

help:
	@echo "TuxBellum $(VERSION) — Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  build   - Install package in development mode (pip install -e .)"
	@echo "  release - Create release tarball for GitHub + AUR"
	@echo "  clean   - Remove build artifacts"
	@echo "  install - Install package (pip install .)"
	@echo "  help    - This help"

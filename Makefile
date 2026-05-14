# Makefile for TuxBellum GTK4
VERSION ?= 4.0.0
RELEASE_TARBALL := tuxbellum-$(VERSION).tar.gz

.PHONY: all build release clean help install

all: build

build:
	@echo "[BUILD] Installing tuxbellum in development mode..."
	pip install -e .

release: clean
	@echo "[RELEASE] Creating release tarball $(RELEASE_TARBALL)..."
	mkdir -p .release/tuxbellum-$(VERSION)
	cp -r src/ packages/ locales/ data/ docs/ scripts/ \
		meson.build pyproject.toml PKGBUILD LICENSE README.md Makefile \
		.release/tuxbellum-$(VERSION)/
	rm -rf .release/tuxbellum-$(VERSION)/packages/Public\ Press\ Kit
	tar -czf $(RELEASE_TARBALL) -C .release tuxbellum-$(VERSION)
	rm -rf .release
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
	@echo "  build   - Install package in development mode (for contributors)"
	@echo "  release - Create release tarball for GitHub + AUR"
	@echo "  clean   - Remove build artifacts"
	@echo "  install - Install package locally (for development/testing only)"
	@echo ""
	@echo "Note: End users should use AppImage or AUR, not pip install"

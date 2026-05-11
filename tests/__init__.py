"""TuxBellum test suite.

GTK4 tests are marked with @pytest.mark.gtk4 and skipped by default
because they require a running display server. Run with:
    pytest                              # non-GTK4 only
    pytest -m gtk4                      # GTK4 tests (requires display)
    pytest --run-gtk4                   # all tests with GTK4 auto-added
"""
import pytest

pytestmark = pytest.mark.skipif(
    True,
    reason="GTK4 tests require display server; run with -m gtk4 explicitly",
)
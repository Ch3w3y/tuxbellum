"""Entry point — CLI when args provided, GUI otherwise."""

from __future__ import annotations

import sys


def main() -> int:
    """Route to CLI or GUI based on command-line arguments."""
    if len(sys.argv) > 1:
        from tuxbellum.cli.main import main as cli_main

        return cli_main()
    else:
        from tuxbellum.app.application import main as gui_main

        gui_main()
        return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Step definitions for the TuxBellum installer engine.

Each module exports an ``InstallStep`` callable::

    from tuxbellum.engine.steps.validate_host import step

Each step receives an ``InstallContext`` and raises on failure.
"""

from tuxbellum.engine.steps.apply_dxvk import step as apply_dxvk
from tuxbellum.engine.steps.apply_fsr import step as apply_fsr
from tuxbellum.engine.steps.apply_tuning import step as apply_tuning
from tuxbellum.engine.steps.ensure_proton import step as ensure_proton
from tuxbellum.engine.steps.generate_desktop import step as generate_desktop
from tuxbellum.engine.steps.generate_launcher import step as generate_launcher
from tuxbellum.engine.steps.init_prefix import step as init_prefix
from tuxbellum.engine.steps.install_dlls import step as install_dlls
from tuxbellum.engine.steps.run_launcher import step as run_launcher
from tuxbellum.engine.steps.validate_host import step as validate_host
from tuxbellum.engine.steps.verify_launcher import step as verify_launcher
from tuxbellum.engine.steps.write_manifest import step as write_manifest

__all__ = [
    "validate_host",
    "ensure_proton",
    "init_prefix",
    "install_dlls",
    "run_launcher",
    "verify_launcher",
    "apply_dxvk",
    "apply_tuning",
    "apply_fsr",
    "generate_launcher",
    "generate_desktop",
    "write_manifest",
]

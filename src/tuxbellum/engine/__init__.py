"""Engine package — step-based install executor and context."""

from tuxbellum.engine.context import InstallContext
from tuxbellum.engine.executor import Executor, StepResult, run_plan

# build_install_plan is imported lazily by callers to avoid circular imports
__all__ = [
    "InstallContext",
    "StepResult",
    "Executor",
    "run_plan",
]

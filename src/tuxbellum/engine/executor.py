"""Executor — runs a plan of steps and collects results."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from tuxbellum.engine.context import InstallContext

# Type aliases
Plan = list[tuple[str, Callable[[InstallContext], None]]]


@dataclass
class StepResult:
    """Outcome of a single step execution."""

    name: str
    status: str  # "success", "skipped", "failed"
    message: str = ""
    error: Exception | None = None

    @property
    def ok(self) -> bool:
        return self.status in ("success", "skipped")

    @property
    def failed(self) -> bool:
        return self.status == "failed"


class Executor:
    """
    Runs a plan of steps sequentially, collecting results.

    By default stops on the first failure (fail_fast=True).
    """

    def __init__(self, fail_fast: bool = True) -> None:
        self.fail_fast = fail_fast
        self.results: list[StepResult] = []

    def run(self, plan: Plan, ctx: InstallContext) -> list[StepResult]:
        """
        Execute every step in `plan` against `ctx`.

        Returns the list of ``StepResult`` entries, one per step.
        On failure, the exception is stored in the result and (if
        fail_fast) re-raised to stop the pipeline immediately.
        """
        self.results = []

        for name, fn in plan:
            self.results.append(self._run_one(name, fn, ctx))
            if self.results[-1].failed and self.fail_fast:
                break

        return self.results

    def _run_one(
        self,
        name: str,
        fn: Callable[[InstallContext], None],
        ctx: InstallContext,
    ) -> StepResult:
        try:
            fn(ctx)
            return StepResult(name=name, status="success")
        except Exception as exc:
            return StepResult(
                name=name,
                status="failed",
                message=str(exc),
                error=exc,
            )

    @property
    def failed(self) -> bool:
        return any(r.failed for r in self.results)

    @property
    def last_error(self) -> Exception | None:
        for r in reversed(self.results):
            if r.error:
                return r.error
        return None


def run_plan(plan: Plan, ctx: InstallContext) -> list[StepResult]:
    """Run a plan with a fail-fast Executor."""
    executor = Executor(fail_fast=True)
    return executor.run(plan, ctx)

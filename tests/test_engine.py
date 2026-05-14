"""Tests for the step-based install engine."""

from unittest.mock import MagicMock

from tuxbellum.engine.context import InstallContext
from tuxbellum.engine.executor import Executor, StepResult, run_plan
from tuxbellum.engine.planner import build_install_plan


# ── InstallContext ───────────────────────────────────────────────────────────


class TestInstallContext:
    def test_defaults(self):
        ctx = InstallContext()
        assert ctx.wineprefix == ""
        assert ctx.is_amd_gpu is False
        assert ctx._state == {}

    def test_put_get_pop(self):
        ctx = InstallContext()
        ctx.put("key", "value")
        assert ctx.get("key") == "value"
        assert ctx.pop("key") == "value"
        assert ctx.get("key") is None

    def test_get_default(self):
        ctx = InstallContext()
        assert ctx.get("missing", 42) == 42

    def test_pop_default(self):
        ctx = InstallContext()
        assert ctx.pop("missing", "fallback") == "fallback"


# ── StepResult ───────────────────────────────────────────────────────────────


class TestStepResult:
    def test_success(self):
        r = StepResult(name="test", status="success")
        assert r.ok is True
        assert r.failed is False

    def test_skipped(self):
        r = StepResult(name="test", status="skipped")
        assert r.ok is True
        assert r.failed is False

    def test_failed(self):
        r = StepResult(name="test", status="failed", message="boom")
        assert r.ok is False
        assert r.failed is True
        assert r.message == "boom"

    def test_failed_with_error(self):
        exc = RuntimeError("test error")
        r = StepResult(name="test", status="failed", error=exc)
        assert r.error is exc


# ── Executor ─────────────────────────────────────────────────────────────────


class TestExecutor:
    def test_runs_all_steps_on_success(self):
        ctx = InstallContext()
        called = []

        def step_a(ctx):
            called.append("a")

        def step_b(ctx):
            called.append("b")

        plan = [("a", step_a), ("b", step_b)]
        results = run_plan(plan, ctx)

        assert called == ["a", "b"]
        assert len(results) == 2
        assert all(r.ok for r in results)

    def test_stops_on_first_failure(self):
        ctx = InstallContext()
        called = []

        def step_a(ctx):
            called.append("a")

        def step_b(ctx):
            called.append("b")
            raise RuntimeError("fail")

        def step_c(ctx):
            called.append("c")  # should not be reached

        plan = [("a", step_a), ("b", step_b), ("c", step_c)]
        results = run_plan(plan, ctx)

        assert called == ["a", "b"]  # c never called
        assert len(results) == 2  # only a and b recorded
        assert results[0].ok
        assert results[1].failed

    def test_executor_last_error(self):
        ctx = InstallContext()
        executor = Executor(fail_fast=True)

        def failing(ctx):
            raise ValueError("bad")

        results = executor.run([("f", failing)], ctx)
        assert executor.failed
        assert isinstance(executor.last_error, ValueError)

    def test_context_mutation_persists_across_steps(self):
        ctx = InstallContext()

        def step_a(ctx):
            ctx.put("shared", 1)

        def step_b(ctx):
            ctx.put("shared", ctx.get("shared") + 1)

        results = run_plan([("a", step_a), ("b", step_b)], ctx)
        assert ctx.get("shared") == 2
        assert all(r.ok for r in results)


# ── Planner ──────────────────────────────────────────────────────────────────


class TestPlanner:
    def test_build_install_plan_returns_named_steps(self):
        plan = build_install_plan()
        names = [name for name, _ in plan]
        assert names == [
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
        # All callables
        for _, fn in plan:
            assert callable(fn)

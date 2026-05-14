"""CLI frontend — drive the installer without GTK."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from tuxbellum.config.paths import path_mgr
from tuxbellum.core.logging import Logger
from tuxbellum.domain.install_state import discover_manifest
from tuxbellum.engine.context import InstallContext
from tuxbellum.engine.executor import run_plan
from tuxbellum.engine.planner import build_install_plan


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI. Returns exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    log_file = os.path.join(path_mgr.logs_dir(), "tuxbellum-cli.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = Logger(log_file)

    try:
        if args.command == "install":
            return _cmd_install(args, logger)
        elif args.command == "status":
            return _cmd_status(args, logger)
        elif args.command == "uninstall":
            return _cmd_uninstall(args, logger)
        elif args.command == "doctor":
            return _cmd_doctor(args, logger)
        elif args.command == "repair":
            return _cmd_repair(args, logger)
        else:
            parser.print_help()
            return 1
    finally:
        logger.close()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tuxbellum",
        description="Install, configure, and manage Bellum on Linux via Wine/Proton.",
    )
    sub = parser.add_subparsers(dest="command")

    # install
    p_install = sub.add_parser("install", help="Install Bellum")
    p_install.add_argument("--wineprefix", default="", help="WINEPREFIX path")
    p_install.add_argument("--gpu", default="", help="GPU type (auto-detect if omitted)")
    p_install.add_argument("--fsr41", action="store_true", help="Enable FSR 4.1 (AMD only)")
    p_install.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts")
    p_install.add_argument(
        "--json", action="store_true", default=True, help="Machine-readable output"
    )

    # status
    p_status = sub.add_parser("status", help="Show install status")
    p_status.add_argument("--wineprefix", default="", help="WINEPREFIX path")
    p_status.add_argument("--json", action="store_true", help="Machine-readable output")

    # uninstall
    p_uninstall = sub.add_parser("uninstall", help="Uninstall Bellum")
    p_uninstall.add_argument("--wineprefix", default="", help="WINEPREFIX path")
    p_uninstall.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    p_uninstall.add_argument("--json", action="store_true", help="Machine-readable output")

    # doctor
    p_doctor = sub.add_parser("doctor", help="Run diagnostics")
    p_doctor.add_argument("--wineprefix", default="", help="WINEPREFIX path (optional)")
    p_doctor.add_argument("--json", action="store_true", help="Machine-readable output")

    # repair
    p_repair = sub.add_parser("repair", help="Repair an existing install")
    p_repair.add_argument("--wineprefix", default="", help="WINEPREFIX path")
    p_repair.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    p_repair.add_argument("--json", action="store_true", help="Machine-readable output")

    return parser


# ── Commands ─────────────────────────────────────────────────────────────────


def _cmd_install(args, logger: Logger) -> int:
    logger.info("TuxBellum CLI — install")
    resource_root = path_mgr.app_data_root()
    cache_dir = path_mgr.launcher_cache_dir()

    ctx = InstallContext(
        wineprefix=args.wineprefix or os.path.join(Path.home(), "Games", "bellum"),
        resource_root=resource_root,
        cache_dir=cache_dir,
        is_fsr41=args.fsr41,
        logger=logger,
    )

    plan = build_install_plan()
    results = run_plan(plan, ctx)

    # Machine-readable output
    output = {
        "status": "ok" if all(r.ok for r in results) else "failed",
        "steps": [{"name": r.name, "status": r.status, "message": r.message} for r in results],
        "wineprefix": ctx.wineprefix,
    }

    print(_format_output(output, args))
    return 0 if output["status"] == "ok" else 1


def _cmd_status(args, logger: Logger) -> int:
    logger.info("TuxBellum CLI — status")
    wineprefix = args.wineprefix

    if not wineprefix:
        # Try to discover from config
        from tuxbellum.config.manager import ConfigManager

        cfg = ConfigManager()
        wineprefix = cfg.get("last_wineprefix", "")

    manifest = discover_manifest(wineprefix) if wineprefix else None

    output = {
        "installed": manifest is not None,
        "wineprefix": wineprefix,
    }
    if manifest:
        output.update(
            {
                "tuxbellum_version": manifest.tuxbellum_version,
                "proton_version": manifest.proton_version,
                "gpu_type": manifest.gpu_type,
                "fsr_enabled": manifest.fsr_enabled,
                "launcher_path": manifest.launcher_path,
            }
        )

    print(_format_output(output, args))
    return 0 if manifest else 1


def _cmd_uninstall(args, logger: Logger) -> int:
    logger.info("TuxBellum CLI — uninstall")

    if not args.yes:
        response = input("Are you sure you want to uninstall Bellum? (y/N): ")
        if response.lower() not in ("y", "yes"):
            print("Cancelled.")
            return 0

    from tuxbellum.installer.uninstall import UninstallConfig, run_uninstallation

    config = UninstallConfig(wineprefix=args.wineprefix or "")
    run_uninstallation(config, logger)

    output = {"status": "ok", "wineprefix": args.wineprefix}
    print(_format_output(output, args))
    return 0


def _cmd_doctor(args, logger: Logger) -> int:
    logger.info("TuxBellum CLI — doctor")
    from tuxbellum.engine.doctor import run_diagnostics

    report = run_diagnostics(args.wineprefix)
    output = {
        "status": "healthy" if report["healthy"] else "issues_found",
        "checks": report["checks"],
    }
    print(_format_output(output, args))
    return 0 if report["healthy"] else 1


def _cmd_repair(args, logger: Logger) -> int:
    logger.info("TuxBellum CLI — repair")
    from tuxbellum.engine.repair import run_repair

    result = run_repair(args.wineprefix, logger)
    output = {
        "status": "repaired" if result["repaired"] else "repair_failed",
        "fixed": result["fixed"],
        "unfixed": result["unfixed"],
    }
    print(_format_output(output, args))
    return 0 if result["repaired"] else 1


def _format_output(data: dict, args) -> str:
    if getattr(args, "json", False):
        return json.dumps(data, indent=2)
    return json.dumps(data, indent=2)  # Always JSON for now

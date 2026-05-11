"""GPU detection using glxinfo."""

import subprocess


def detect_gpu() -> tuple[str | None, str | None]:
    """Detect GPU vendor. Returns (vendor_label, renderer_string) or (None, error_msg)."""
    try:
        result = subprocess.run(["glxinfo", "-B"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return None, f"glxinfo failed: {result.stderr.strip()}"
    except FileNotFoundError:
        return None, "glxinfo not found. Install mesa-utils package."
    except subprocess.TimeoutExpired:
        return None, "glxinfo timed out."

    renderer = _parse_renderer(result.stdout)
    if not renderer:
        return None, "OpenGL renderer string not found in glxinfo output."

    return classify_gpu(renderer), None


def _parse_renderer(output: str) -> str | None:
    for line in output.splitlines():
        if "opengl renderer" in line.lower():
            parts = line.split(":", 1)
            if len(parts) == 2:
                return parts[1].strip()
    return None


def classify_gpu(renderer: str) -> str:
    r = renderer.lower()
    if "nvidia" in r:
        return "NVIDIA"
    if "amd" in r or "radeon" in r:
        return "AMD"
    if "intel" in r:
        return "Intel"
    parts = renderer.split()
    return parts[0] if parts else "Unknown"

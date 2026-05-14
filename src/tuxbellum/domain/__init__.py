"""Domain models — install manifest, options, and state management."""

from tuxbellum.domain.dependency_spec import (
    DEPENDENCIES,
    DepCategory,
    DependencySpec,
    get_by_category,
    get_dependency,
)
from tuxbellum.domain.install_manifest import (
    CURRENT_SCHEMA_VERSION,
    InstallManifest,
    manifest_exists,
    manifest_path,
)
from tuxbellum.domain.install_options import InstallOptions
from tuxbellum.domain.install_state import (
    StateError,
    delete_manifest,
    discover_manifest,
    save_manifest,
)

__all__ = [
    "InstallManifest",
    "InstallOptions",
    "CURRENT_SCHEMA_VERSION",
    "manifest_path",
    "manifest_exists",
    "discover_manifest",
    "save_manifest",
    "delete_manifest",
    "StateError",
    "DependencySpec",
    "DepCategory",
    "DEPENDENCIES",
    "get_dependency",
    "get_by_category",
]

"""Per-repo configuration loading and version-pin comparison.

Governing spec: specs/tools/aire/architecture-spec.md (Configuration Model).
Reads .aire/config.toml via stdlib tomllib. No external dependencies.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Parsed .aire/config.toml, with provenance about how it loaded."""

    aire_version_min: str | None = None
    profile: str | None = None
    local_model_floor: int | None = None
    present: bool = False          # the file existed
    parse_error: str | None = None  # set if it existed but failed to parse


def load_config(root: Path) -> Config:
    """Load .aire/config.toml from `root`. Absent file is not an error."""
    path = Path(root) / ".aire" / "config.toml"
    if not path.is_file():
        return Config(present=False)
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except (tomllib.TOMLDecodeError, OSError) as exc:
        return Config(present=True, parse_error=str(exc))
    floor = data.get("local_model_floor")
    return Config(
        aire_version_min=data.get("aire_version_min"),
        profile=data.get("profile"),
        local_model_floor=int(floor) if isinstance(floor, int) else None,
        present=True,
    )


def _version_tuple(value: str) -> tuple[int, ...]:
    """Parse a dotted version into an int tuple, ignoring pre-release suffixes."""
    parts: list[int] = []
    for piece in str(value).strip().split("."):
        digits = ""
        for ch in piece:
            if ch.isdigit():
                digits += ch
            else:
                break
        parts.append(int(digits) if digits else 0)
    return tuple(parts) or (0,)


def version_satisfies(running: str, minimum: str) -> bool:
    """True if `running` version is >= `minimum` version."""
    r = _version_tuple(running)
    m = _version_tuple(minimum)
    width = max(len(r), len(m))
    r += (0,) * (width - len(r))
    m += (0,) * (width - len(m))
    return r >= m

"""Project-root restrictions shared by the idalib supervisor and workers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def normalize_allowed_roots(roots: Iterable[str | Path]) -> tuple[Path, ...]:
    """Resolve and deduplicate allowed roots without changing their order."""

    normalized: list[Path] = []
    for root in roots:
        resolved = Path(root).resolve()
        if resolved not in normalized:
            normalized.append(resolved)
    return tuple(normalized)


def resolve_allowed_path(
    input_path: str | Path,
    allowed_roots: Iterable[Path],
) -> Path:
    """Resolve *input_path* and reject it when it escapes the project roots."""

    resolved = Path(input_path).resolve()
    roots = tuple(allowed_roots)
    if roots and not any(resolved == root or root in resolved.parents for root in roots):
        raise ValueError(f"Input path is outside the allowed project roots: {resolved}")
    return resolved

from pathlib import Path

import pytest

from ida_pro_mcp.path_policy import normalize_allowed_roots, resolve_allowed_path


def test_normalize_allowed_roots_deduplicates(tmp_path):
    root = tmp_path / "Nexus"
    assert normalize_allowed_roots([root, root]) == (root.resolve(),)


def test_resolve_allowed_path_accepts_descendant(tmp_path):
    root = (tmp_path / "Nexus").resolve()
    assert resolve_allowed_path(root / "db" / "retail.i64", (root,)) == (
        root / "db" / "retail.i64"
    )


def test_resolve_allowed_path_rejects_sibling(tmp_path):
    root = (tmp_path / "Nexus").resolve()
    with pytest.raises(ValueError, match="outside the allowed project roots"):
        resolve_allowed_path(tmp_path / "Ares" / "grimfall.i64", (root,))

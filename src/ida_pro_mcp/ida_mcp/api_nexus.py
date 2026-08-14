"""Nexus-specific, read-only semantic candidate export tool."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Annotated, Any, Optional, TypedDict

from .rpc import tool
from .sync import idasync


class NexusSemanticCandidateExportResult(TypedDict):
    schema: str
    candidateCount: int
    outputPath: str
    outputSha256: str
    databaseSaveRequested: bool
    automaticPromotionAllowed: bool


def _load_adapter(repository_root: Path) -> Any:
    adapter_path = (
        repository_root / "tools" / "ida" / "nexus_semantic_mcp_adapter.py"
    ).resolve()
    expected_parent = (repository_root / "tools" / "ida").resolve()
    if adapter_path.parent != expected_parent or not adapter_path.is_file():
        raise ValueError("NEXUS_IDA_SEMANTIC_ADAPTER_UNAVAILABLE")
    spec = importlib.util.spec_from_file_location(
        "nexus_semantic_mcp_adapter", adapter_path
    )
    if spec is None or spec.loader is None:
        raise ValueError("NEXUS_IDA_SEMANTIC_ADAPTER_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@tool
@idasync
def nexus_export_semantic_candidate_facts(
    plan_path: Annotated[str, "Absolute bound semantic relocation plan path"],
    request_path: Annotated[str, "Absolute one-owner candidate request path"],
    output_path: Annotated[str, "New draft-facts path under Nexus evidence"],
    candidate_rvas: Annotated[
        Optional[list[str]],
        "Current-build candidate RVAs for bounded manual rediscovery; omit for replay-selected candidates",
    ] = None,
    discovery_ledger_sha256: Annotated[
        str,
        "Append-only discovery-ledger SHA-256 for manual rediscovery; omit for replay-selected candidates",
    ] = "",
) -> NexusSemanticCandidateExportResult:
    """Export one hash-bound Nexus semantic owner family without saving IDA."""

    repository_root = Path(__file__).resolve().parents[5]
    adapter = _load_adapter(repository_root)
    return adapter.run_bounded_export(
        repository_root,
        plan_path,
        request_path,
        output_path,
        candidate_rvas,
        discovery_ledger_sha256 or None,
    )

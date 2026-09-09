"""Regression checks for unattended Aether operation, without a licensed IDA."""

from unittest.mock import Mock
import urllib.error
import urllib.request

from ida_pro_mcp import idalib_supervisor as supmod
from _mcp_spec_support import McpHttpTestServer, McpServer


def test_status_dispatch_does_not_start_or_probe_worker(monkeypatch):
    supervisor = supmod.IdalibSupervisor(supmod.mcp, max_workers=1)
    supervisor._spawn_worker = Mock(side_effect=AssertionError("worker started"))
    supervisor._worker_rpc = Mock(side_effect=AssertionError("worker probed"))
    monkeypatch.setattr(supmod, "supervisor", supervisor)
    response = supmod._handle_tools_call({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "supervisor_status", "arguments": {}},
    })
    result = response["result"]["structuredContent"]
    assert result["session_count"] == 0
    assert result["max_workers"] == 1
    assert result["tools_cached"] is False
    assert result["worker_probe_performed"] is False
    supervisor._spawn_worker.assert_not_called()
    supervisor._worker_rpc.assert_not_called()


def test_http_delete_releases_only_requested_session_and_checks_origin():
    server = McpServer("cleanup-test")
    server.register_http_session("keep")
    server.register_http_session("remove")
    with McpHttpTestServer(server) as harness:
        def delete(headers):
            request = urllib.request.Request(
                harness.base_url + "/mcp", method="DELETE", headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=5) as response:
                    return response.status
            except urllib.error.HTTPError as error:
                return error.code

        assert delete({}) == 400
        assert delete({"Mcp-Session-Id": "remove", "Origin": "https://evil.example"}) == 403
        assert server.has_http_session("remove")
        assert delete({"Mcp-Session-Id": "remove"}) == 204
        assert not server.has_http_session("remove")
        assert server.has_http_session("keep")
        assert delete({"Mcp-Session-Id": "remove"}) == 404

from __future__ import annotations

import json
import shutil
import subprocess
import threading
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

import pytest

from omniwebbench.fixture import LAB_HTML, FixtureHandler
from omniwebbench.task_factory import BLUEPRINTS


def test_fixture_javascript_parses() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")
    script = LAB_HTML.split("<script>", 1)[1].split("</script>", 1)[0]
    script = script.replace("__CONFIG_JSON__", "{}")
    result = subprocess.run([node, "--check"], input=script, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


def test_fixture_serves_tasks_and_records_observed_events() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(f"{origin}/health") as response:
            assert json.load(response)["status"] == "ok"
        with urlopen(f"{origin}/lab?task_id=owb-dev-001&run_id=test-run") as response:
            body = response.read().decode()
            assert "Launch analysis" in body
            assert "OMNIWEBBENCH" in body
        payload = json.dumps(
            {"run_id": "test-run", "task_id": "owb-dev-001", "name": "primary-clicked", "data": {}}
        ).encode()
        request = Request(
            f"{origin}/api/event",
            data=payload,
            headers={"content-type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            assert response.status == 201
        with urlopen(f"{origin}/api/runs/test-run") as response:
            events = json.load(response)["events"]
            assert events[0]["name"] == "primary-clicked"
            assert events[0]["sequence"] == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_fixture_serves_every_blueprint_family() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    expected_uis = {
        "workflow_form",
        "research_board",
        "state_form",
        "safety_panel",
        "artifact_case",
        "debug_case",
        "patch_case",
    }
    try:
        seen = set()
        for index, blueprint in enumerate(BLUEPRINTS, start=1):
            with urlopen(
                f"{origin}/lab?task_id=owb-dev-{index:03d}&run_id=family-{index}"
            ) as response:
                body = response.read().decode()
                assert response.status == 200
                assert blueprint["title"] in body
                assert f'"ui": "{blueprint["ui"]}"' in body
                seen.add(blueprint["ui"])
        assert expected_uis <= seen
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

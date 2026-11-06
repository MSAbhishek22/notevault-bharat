"""Regression test: the homepage inline script must parse as JavaScript.

The live site once shipped a SyntaxError in its only inline script
(unescaped quotes in an onkeydown handler inside a single-quoted JS
string, built inside a Python triple-quoted template), which killed
every interactive feature: notes stuck on "Loading…", constellation
blank, Ask dead. This test extracts the inline <script> from the
served homepage and runs node --check on it.
"""
import re
import shutil
import subprocess
import threading
import urllib.request
from wsgiref.simple_server import make_server as make_wsgi_server

import pytest

from notes_bharat.agent import NotesAgent
from notes_bharat.config import Config
from notes_bharat.wsgi import make_application


def _config(tmp_path, **overrides):
    kwargs = dict(notes_root=tmp_path, provider="mock")
    kwargs.update(overrides)
    return Config(**kwargs)


@pytest.fixture()
def live(tmp_path):
    (tmp_path / "a.md").write_text("# Abhiverse idea\nPhone remote for laptop. #project", encoding="utf-8")
    agent = NotesAgent(_config(tmp_path))
    server = make_wsgi_server("127.0.0.1", 0, make_application(agent))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


def _homepage(live):
    with urllib.request.urlopen(live + "/") as resp:
        assert resp.status == 200
        return resp.read().decode("utf-8")


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_homepage_inline_script_parses(live, tmp_path):
    html = _homepage(live)
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    assert scripts, "expected at least one inline <script> on the homepage"
    script_file = tmp_path / "inline.js"
    script_file.write_text(scripts[0], encoding="utf-8")
    proc = subprocess.run(["node", "--check", str(script_file)],
                          capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, f"node --check failed:\n{proc.stderr}"


def test_homepage_has_no_unescaped_enter_handler(live):
    html = _homepage(live)
    assert "key==='Enter'" not in html, "unescaped quotes in onkeydown handler"
    assert "key===\\'Enter\\'" in html, "onkeydown handler must carry escaped quotes"

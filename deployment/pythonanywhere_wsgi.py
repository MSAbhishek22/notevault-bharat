"""PythonAnywhere WSGI file for NoteVault Bharat.

In the PythonAnywhere Web tab, set the WSGI configuration file to this
file:

    /home/<username>/notevault-bharat/deployment/pythonanywhere_wsgi.py

(or copy it to /var/www/<username>_pythonanywhere_com_wsgi.py — the
content is the same).

It only puts the repo on sys.path and points NOTES_ROOT at the repo's
notes folder. The app itself lives in notes_bharat/wsgi.py. No key is
set here: without BHARATCODE_API_KEY the app runs in labelled mock
mode. To switch to real BharatCode mode later, set BHARATCODE_API_KEY
in the Web tab (or here via os.environ) AND confirm bharatcode.ai is
allowlisted for free accounts — see
deployment/PYTHONANYWHERE_DEPLOY.md. Until the allowlist is granted,
live /api/ask calls fail honestly with a provider error.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.environ.setdefault("NOTES_ROOT", str(REPO_ROOT / "notes"))

from notes_bharat.wsgi import application  # noqa: E402,F401

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["pypresence"]
# ///
import json
import os
import signal
import sys
import tempfile
import time
from pathlib import Path

CLIENT_ID = "1501939062901182596"
DETAILS = "Claude Code"
STATE = "AI assisted coding"


def _session_id() -> str:
    raw = os.environ.get("CCDISCORD_HOOK_JSON")
    if not raw:
        return "default"
    try:
        sid = json.loads(raw).get("session_id")
    except json.JSONDecodeError:
        return "default"
    return sid or "default"


PID_FILE = Path(tempfile.gettempdir()) / "ccdiscord" / f"{_session_id()}.pid"

rpc = None


def log(msg: str) -> None:
    print(f"[ccdiscord] {msg}", file=sys.stderr)


def cleanup(signum=None, frame=None):
    if rpc is not None:
        try:
            rpc.clear()
            rpc.close()
        except Exception:
            pass
    PID_FILE.unlink(missing_ok=True)
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

PID_FILE.parent.mkdir(parents=True, exist_ok=True)
PID_FILE.write_text(str(os.getpid()))

try:
    from pypresence import Presence
except ImportError as exc:
    log(f"failed to import pypresence: {exc}")
    cleanup()

START_TIME = int(time.time())


def _update() -> None:
    rpc.update(details=DETAILS, state=STATE, start=START_TIME)


try:
    rpc = Presence(CLIENT_ID)
    rpc.connect()
    _update()
except Exception as exc:
    name = type(exc).__name__
    if name == "DiscordNotFound":
        log("Discord desktop client not detected. Open Discord and start a new session.")
    else:
        log(f"could not connect to Discord. ({name}: {exc})")
    cleanup()

connected = True
while True:
    time.sleep(15)
    try:
        _update()
        if not connected:
            log("reconnected to Discord.")
            connected = True
        continue
    except Exception:
        pass

    try:
        rpc.close()
    except Exception:
        pass
    try:
        rpc = Presence(CLIENT_ID)
        rpc.connect()
        _update()
        if not connected:
            log("reconnected to Discord.")
        connected = True
    except Exception:
        if connected:
            log("lost connection to Discord. Will keep retrying.")
        connected = False

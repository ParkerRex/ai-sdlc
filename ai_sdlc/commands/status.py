# ai_sdlc/commands/status.py
"""`aisdlc status` – show progress through lifecycle steps."""

from __future__ import annotations

import argparse

from ai_sdlc.utils import load_config, read_lock, render_step_bar


def run_status(args: argparse.Namespace | None = None) -> None:
    conf = load_config()
    steps = conf["steps"]
    lock = read_lock()
    print("Active workstreams\n------------------")
    if not lock:
        print("none – create one with `aisdlc new`")
        return
    slug = lock["slug"]
    cur = lock["current"]
    idx = steps.index(cur)
    bar = render_step_bar(steps, idx)
    print(f"{slug:20} {cur:12} {bar}")

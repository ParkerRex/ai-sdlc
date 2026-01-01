"""`aisdlc done` – validate finished stream and archive it."""

import shutil
import sys

from ai_sdlc.utils import ROOT, load_config, read_lock, write_lock


def run_done(args: object = None) -> None:
    conf = load_config()
    steps = conf["steps"]
    lock = read_lock()
    if not lock:
        print("❌  No active workstream.")
        return
    slug = lock["slug"]
    if lock["current"] != steps[-1]:
        print("❌  Workstream not finished yet. Complete all steps before archiving.")
        return
    workdir = ROOT / conf["active_dir"] / slug
    missing = [s for s in steps if not (workdir / f"{s}-{slug}.md").exists()]
    if missing:
        print("❌  Missing files:", ", ".join(missing))
        return
    dest = ROOT / conf["done_dir"] / slug
    try:
        shutil.move(str(workdir), dest)
        write_lock({})
        print(f"🎉  Archived to {dest}")
    except OSError as e:
        print(f"❌  Error archiving work-stream '{slug}': {e}")
        sys.exit(1)

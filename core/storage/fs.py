import shutil
from pathlib import Path

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def atomic_move(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.move(str(src), str(dst))

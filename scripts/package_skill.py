"""youtube-math-auto/ 디렉토리를 .skill ZIP 패키지로 묶는다.

기존 youtube-math-lesson.skill과 동일한 구조:
    youtube-math-auto/SKILL.md
    youtube-math-auto/scripts/fetch_subtitle.py
    youtube-math-auto/scripts/vtt_to_text.py
"""
import sys
import zipfile
from pathlib import Path

EXCLUDE = {"__pycache__", ".pyc", ".DS_Store"}


def should_skip(path: Path) -> bool:
    parts = path.parts
    if any(part in EXCLUDE or part.startswith(".") for part in parts):
        return True
    if path.suffix in {".pyc", ".pyo"}:
        return True
    return False


def package(src_dir: Path, out_path: Path) -> None:
    if not src_dir.is_dir():
        raise FileNotFoundError(f"소스 디렉토리 없음: {src_dir}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    skill_root = src_dir.name

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(src_dir.rglob("*")):
            rel = path.relative_to(src_dir)
            if should_skip(rel):
                continue
            if path.is_file():
                arcname = f"{skill_root}/{rel.as_posix()}"
                zf.write(path, arcname)
                print(f"  + {arcname} ({path.stat().st_size} B)")

    size = out_path.stat().st_size
    print(f"\nOK: {out_path} ({size} B)")


def main() -> int:
    here = Path(__file__).resolve().parent.parent
    src = here / "youtube-math-auto"
    out = here / "youtube-math-auto.skill"
    if len(sys.argv) > 1:
        src = Path(sys.argv[1]).resolve()
    if len(sys.argv) > 2:
        out = Path(sys.argv[2]).resolve()
    package(src, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

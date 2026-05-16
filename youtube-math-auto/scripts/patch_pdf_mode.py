#!/usr/bin/env python3
"""
patch_pdf_mode.py — 학습자료 HTML 에 PDF 인쇄 모드 컴포넌트 삽입.

각 자료 HTML 의 <head> 끝에 pdf-mode.css link 를, </body> 직전에
pdf-mode.js script 를 삽입한다. 이미 들어가 있으면 skip (idempotent).

사용:
    python youtube-math-auto/scripts/patch_pdf_mode.py output/
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LINK_TAG = '<link rel="stylesheet" href="{}pdf-mode.css">'
SCRIPT_TAG = '<script defer src="{}pdf-mode.js"></script>'

# 자료 파일의 상대 경로에 따른 ../ 개수 계산용 표식
MARKER_CSS = "pdf-mode.css"
MARKER_JS = "pdf-mode.js"


def relative_prefix(html_path: Path, output_root: Path) -> str:
    """
    output/고2/수학II-.../*.html → "../../" 형태로 반환.
    output/index.html → "./" 또는 "".
    """
    rel = html_path.relative_to(output_root).parent
    depth = len(rel.parts)
    return "../" * depth


def patch_file(html_path: Path, output_root: Path) -> bool:
    """파일 패치. 변경 발생 시 True."""
    text = html_path.read_text(encoding="utf-8")

    changed = False
    prefix = relative_prefix(html_path, output_root)

    # 1. <link> 추가 — </head> 직전
    if MARKER_CSS not in text:
        link = LINK_TAG.format(prefix)
        new_text, n = re.subn(
            r"(</head>)",
            f"  {link}\n\\1",
            text,
            count=1,
        )
        if n:
            text = new_text
            changed = True

    # 2. <script> 추가 — </body> 직전
    if MARKER_JS not in text:
        script = SCRIPT_TAG.format(prefix)
        new_text, n = re.subn(
            r"(</body>)",
            f"  {script}\n\\1",
            text,
            count=1,
        )
        if n:
            text = new_text
            changed = True

    if changed:
        html_path.write_text(text, encoding="utf-8")
    return changed


def main():
    if len(sys.argv) != 2:
        print("Usage: patch_pdf_mode.py <output-dir>")
        sys.exit(1)

    output_root = Path(sys.argv[1]).resolve()
    if not output_root.is_dir():
        print(f"❌ Not a directory: {output_root}")
        sys.exit(1)

    targets = []
    for path in output_root.rglob("*.html"):
        name = path.name
        # 갤러리 index.html 은 패치 대상 아님 — 자료 페이지만
        if path.parent == output_root and name == "index.html":
            continue
        # pdf-mode 자체 파일 제외 (없겠지만 안전)
        if name in {"pdf-mode.css", "pdf-mode.js"}:
            continue
        targets.append(path)

    print(f"[INFO] Found {len(targets)} lesson HTML file(s)")

    patched = 0
    skipped = 0
    for path in sorted(targets):
        if patch_file(path, output_root):
            print(f"  ✅ patched  {path.relative_to(output_root)}")
            patched += 1
        else:
            print(f"  ⏭  skipped  {path.relative_to(output_root)}")
            skipped += 1

    print(f"\n[OK] patched {patched}, skipped {skipped} (already up-to-date)")


if __name__ == "__main__":
    main()

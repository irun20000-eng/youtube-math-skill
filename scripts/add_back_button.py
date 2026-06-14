"""갤러리 복귀 버튼 일괄 추가 — output/ 의 모든 학습자료 HTML 상단에
'🏠 갤러리로' 링크를 삽입한다. A형·B형 템플릿 모두 호환(<body> 직후 삽입).

- 경로: 페이지는 output/{학년}/{단원}/파일.html, 갤러리 index는 output/ 루트.
  따라서 상대링크 ../../index.html 이 로컬·라이브(Pages 루트=output) 모두에서 갤러리를 가리킨다.
- idempotent: 이미 있으면(id="gallery-back") 건너뜀.

사용법: python add_back_button.py [--force]
"""
import argparse
import glob
import os
import re
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO, "output")

SNIPPET = (
    '\n<nav id="gallery-back" '
    'style="max-width:900px;margin:0 auto;padding:14px 20px 0;font-family:'
    "'Pretendard','Noto Sans KR',sans-serif;\">"
    '<a href="../../index.html" '
    'style="display:inline-block;padding:7px 16px;border-radius:8px;'
    'background:#2196f3;color:#fff;text-decoration:none;font-size:0.92em;'
    'font-weight:600;box-shadow:0 1px 4px rgba(0,0,0,.15);">'
    "🏠 갤러리로 돌아가기</a></nav>\n"
)

BODY_RE = re.compile(r"(<body[^>]*>)", re.IGNORECASE)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    files = sorted(
        f for f in glob.glob(os.path.join(OUTPUT, "**", "*.html"), recursive=True)
        if os.path.basename(f) != "index.html"
    )
    added = skipped = failed = 0
    for f in files:
        t = open(f, encoding="utf-8", errors="replace").read()
        rel = os.path.relpath(f, OUTPUT)
        if 'id="gallery-back"' in t and not args.force:
            skipped += 1
            print(f"  - skip(이미 있음): {rel}", file=sys.stderr)
            continue
        if args.force:
            t = re.sub(r"\n?<nav id=\"gallery-back\".*?</nav>\n?", "", t, flags=re.DOTALL)
        if not BODY_RE.search(t):
            failed += 1
            print(f"  ! <body> 못 찾음: {rel}", file=sys.stderr)
            continue
        t = BODY_RE.sub(lambda m: m.group(1) + SNIPPET, t, count=1)
        open(f, "w", encoding="utf-8").write(t)
        added += 1
        print(f"  + 추가: {rel}", file=sys.stderr)
    print(f"[OK] 추가 {added} / 건너뜀 {skipped} / 실패 {failed} / 총 {len(files)}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

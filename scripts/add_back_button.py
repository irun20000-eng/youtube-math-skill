"""갤러리 복귀 버튼 일괄 추가 — output/ 의 모든 학습자료 HTML 상단에
'🏠 갤러리로' 링크를 삽입한다. A형·B형 템플릿 모두 호환(<body> 직후 삽입).

- 경로: 페이지는 output/{학년}/{단원}/파일.html, 갤러리 index는 output/ 루트.
  따라서 상대링크 ../../index.html 이 로컬·라이브(Pages 루트=output) 모두에서 갤러리를 가리킨다.
- idempotent: 이미 있으면(id="brand-bar") 건너뜀.
  주의: 레슨 템플릿 자체가 <a id="gallery-back"> 를 갖고 있어
  그 id 로 판정하면 전 파일이 '이미 있음'으로 오탐돼 한 건도 안 들어간다.

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

# 브랜드 바 — 워드마크(aftermath) + (필요할 때만) 갤러리 복귀 링크.
# 워드마크는 파랑(#2563eb)+회색(#99a1b0)이라 라이트·다크 어느 쪽에서도 읽힌다.
# 인쇄(PDF)에서는 복귀 링크만 숨기고 워드마크는 남겨 배포본에 출처가 찍히게 한다.

_BACK_LINK = (
    '<a class="gb-link" href="../../index.html" '
    'style="display:inline-block;padding:7px 16px;border-radius:8px;'
    'background:#2563eb;color:#fff;text-decoration:none;font-size:0.92em;'
    'font-weight:600;box-shadow:0 1px 4px rgba(0,0,0,.15);">'
    "갤러리로 돌아가기</a>"
)

# 스티키 툴바가 margin-top:-24px 로 위로 끌려 올라와 브랜드 바를 덮는다.
# (툴바가 body 의 첫 요소라는 전제로 만든 값인데, 그 앞에 브랜드 바가 생겼다.)
# 브랜드 바가 상단 여백을 대신하므로 음수 마진만 0 으로 되돌린다.
_STYLE = (
    "<style>.controls.hybrid-toolbar{margin-top:0!important}"
    "@media print{#brand-bar .gb-link{display:none!important}"
    "#brand-bar{padding-top:0!important;margin-bottom:6px}"
    "#brand-bar img{width:104px!important}}</style>"
)


def build_snippet(has_own_gallery_link: bool) -> str:
    """페이지 툴바에 이미 갤러리 링크가 있으면 복귀 버튼을 빼고 워드마크만 넣는다."""
    return (
        '\n<nav id="brand-bar" '
        'style="max-width:900px;margin:0 auto;padding:14px 20px 0;display:flex;'
        'align-items:center;gap:14px;flex-wrap:wrap;font-family:'
        "'Pretendard','Noto Sans KR',sans-serif;\">"
        '<a href="../../index.html" aria-label="aftermath — 갤러리 홈" '
        'style="line-height:0;flex-shrink:0;">'
        '<img src="../../assets/brand/wordmark.png" alt="aftermath" '
        'style="width:132px;height:auto;display:block;">'
        "</a>"
        + ("" if has_own_gallery_link else _BACK_LINK)
        + _STYLE
        + "</nav>\n"
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
        if 'id="brand-bar"' in t and not args.force:
            skipped += 1
            print(f"  - skip(이미 있음): {rel}", file=sys.stderr)
            continue
        if args.force:
            t = re.sub(r"\n?<nav id=\"(?:brand-bar|gallery-back)\".*?</nav>\n?", "", t, flags=re.DOTALL)
        if not BODY_RE.search(t):
            failed += 1
            print(f"  ! <body> 못 찾음: {rel}", file=sys.stderr)
            continue
        # 페이지가 자체 툴바에 갤러리 링크를 이미 갖고 있으면 복귀 버튼 중복을 피한다
        snippet = build_snippet('href="../../index.html"' in t)
        t = BODY_RE.sub(lambda m: m.group(1) + snippet, t, count=1)
        open(f, "w", encoding="utf-8").write(t)
        added += 1
        print(f"  + 추가: {rel}", file=sys.stderr)
    print(f"[OK] 추가 {added} / 건너뜀 {skipped} / 실패 {failed} / 총 {len(files)}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

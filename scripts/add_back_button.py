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

# 주입 스타일 두 가지.
#
# (1) 스티키 툴바가 margin-top:-24px 로 위로 끌려 올라와 브랜드 바를 덮는다.
#     (툴바가 body 의 첫 요소라는 전제로 만든 값인데, 그 앞에 브랜드 바가 생겼다.)
#     브랜드 바가 상단 여백을 대신하므로 음수 마진만 0 으로 되돌린다.
#
# (2) 모바일 가로 밀림 방지. 긴 수식 한 줄이 문단 상자를 넘치면 그 넘침이
#     페이지 전체로 번져 좌우로 흔들렸다(실측 40px). 넓은 콘텐츠는 자기 상자
#     안에서만 스크롤시키고, 끊을 데 없는 긴 문자열은 강제로 줄바꿈한다.
#     A형 자료가 .visual 에 이미 쓰던 방식(overflow-x:auto)을 전체로 넓힌 것.
_STYLE = (
    "<style>.controls.hybrid-toolbar{margin-top:0!important}"
    ".katex-display{overflow-x:auto;overflow-y:hidden;padding:2px 0}"
    ".formula-box,.step-derive,.visual,.mini-ex{overflow-x:auto}"
    # 표는 display:table 이라 overflow-x:auto 가 안 먹는다. block 으로 바꿔야
    # 자기 상자 안에서 가로 스크롤된다(반응형 표의 표준 처리).
    "table{display:block;overflow-x:auto;max-width:100%}"
    # overflow-wrap 은 상속되는 속성이라 body 한 줄로 전 자손을 덮는다.
    # 클래스를 일일이 나열하면(.why, .step-body …) 새 템플릿이 생길 때마다 또 샌다.
    # 'anywhere' 가 아니라 'break-word' — 넘칠 때만 끊어 평소 줄바꿈은 그대로 둔다.
    "body{overflow-wrap:break-word}"
    # 진짜 원인: 풀이 단계가 flex 컨테이너(.sol-step, .step-row)인데 flex 아이템은
    # 기본 min-width:auto 라 min-content 아래로 줄어들지 않는다. 긴 수식 한 줄이
    # 그 하한을 키워 상자를 밀어냈다. div 는 컨트롤이 아니라 컨테이너뿐이므로
    # min-width:0 을 넓게 줘도 버튼·입력폭에는 영향이 없고, 비플렉스 요소에서는
    # min-width:auto 가 어차피 0 으로 계산돼 무해하다.
    "body div{min-width:0}"
    "@media print{#brand-bar .gb-link,#brand-bar .gb-copy{display:none!important}"
    "#brand-bar{padding-top:0!important;margin-bottom:6px}"
    "#brand-bar img{width:104px!important}}</style>"
)


# 링크 복사 — 학생에게 주소를 보내는 게 이 자료의 종착점인데,
# 지금까지는 주소창에서 직접 긁어야 했다. 인쇄본에서는 숨긴다.
_COPY_LINK = (
    '<button class="gb-copy" type="button" '
    'style="min-height:38px;padding:7px 14px;border-radius:8px;'
    'border:1px solid #d0d7de;background:transparent;color:#57606a;'
    'font:inherit;font-size:0.88em;cursor:pointer;">'
    "🔗 링크 복사</button>"
)

_COPY_SCRIPT = (
    "<script>(function(){var b=document.querySelector('#brand-bar .gb-copy');"
    "if(!b)return;b.addEventListener('click',function(){"
    "var u=location.href,done=function(ok){var t=b.textContent;"
    "b.textContent=ok?'✅ 복사됨':'복사 실패';"
    "setTimeout(function(){b.textContent=t;},1600);};"
    "if(navigator.clipboard&&window.isSecureContext){"
    "navigator.clipboard.writeText(u).then(function(){done(true);},function(){done(false);});"
    "}else{"          # file:// 등 비보안 컨텍스트 폴백
    "var ta=document.createElement('textarea');ta.value=u;"
    "ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();"
    "var ok=false;try{ok=document.execCommand('copy');}catch(e){}ta.remove();done(ok);}"
    "});})();</script>"
)



# 본문 실제 폭 감지 — A형은 .container, B형은 body 자체에 max-width 가 있다.
# 하드코딩된 값(과거엔 항상 900px)을 쓰면 A형(880px 본문)에서 브랜드바만 20px
# 넓어져 상단이 어긋난다. 파일마다 실제 쓰는 폭을 읽어 그대로 맞춘다.
_CONTAINER_W_RE = re.compile(r"\.container\s*\{([^}]*)\}")
_BODY_W_RE = re.compile(r"(?<!\.)\bbody\s*\{([^}]*)\}")



# 폭 계산은 max-width 만 봐서는 안 된다. 본문 호스트(.container 또는 body)에는
# 좌우 패딩이 있고, 카드는 그 패딩 안쪽에 놓인다. 주입 요소는 호스트 밖(body 직계)
# 이라 패딩을 받지 못하므로, max-width 를 그대로 쓰면 좌우로 정확히 패딩만큼
# 더 넓어진다(A형 880-16-16=848 인데 880 을 써서 좌우 16px 씩 튀어나왔다).
_PAD_RE = re.compile(r"(?:^|;)\s*padding\s*:\s*([^;]+)")
_PADL_RE = re.compile(r"(?:^|;)\s*padding-left\s*:\s*(-?[\d.]+)px")
_PADR_RE = re.compile(r"(?:^|;)\s*padding-right\s*:\s*(-?[\d.]+)px")


def _h_padding(decls: str) -> "tuple[int, int]":
    """선언 블록에서 좌우 패딩(px)을 뽑는다. px 아닌 단위는 0 으로 본다."""
    left = right = 0
    m = _PAD_RE.search(decls)
    if m:
        parts = m.group(1).split()

        def px(tok):
            mm = re.fullmatch(r"(-?[\d.]+)px", tok)
            return int(float(mm.group(1))) if mm else 0

        if len(parts) == 1:
            left = right = px(parts[0])
        elif len(parts) in (2, 3):
            left = right = px(parts[1])
        elif len(parts) >= 4:
            right, left = px(parts[1]), px(parts[3])
    m = _PADL_RE.search(decls)
    if m:
        left = int(float(m.group(1)))
    m = _PADR_RE.search(decls)
    if m:
        right = int(float(m.group(1)))
    return left, right


def detect_side_gap(html: str) -> int:
    """본문 호스트의 좌우 패딩 합. 주입 요소의 width:calc() 에 쓴다.

    max-width 만 맞추면 화면이 좁을 때(모바일) max-width 가 걸리지 않아, 주입
    요소만 화면 끝까지 퍼지고 카드는 호스트 패딩만큼 들어가 좌우가 어긋난다.
    width:calc(100% - gap) 을 함께 주면 두 경우 모두 카드와 정확히 맞는다.
    """
    m = _CONTAINER_W_RE.search(html)
    if m and re.search(r"max-width:\s*\d+px", m.group(1)):
        # A형: 주입 요소가 .container 의 형제라 호스트 패딩을 못 받는다 → 보정 필요
        pl, pr = _h_padding(m.group(1))
        return pl + pr
    # B형: 호스트가 body 자신이고 주입 요소는 그 자식이라 이미 패딩 안쪽이다 → 보정 0
    return 0

def detect_content_width(html: str, default: int = 860) -> int:
    """본문 카드가 실제로 차지하는 폭(패딩 안쪽)을 돌려준다."""
    for rx in (_CONTAINER_W_RE, _BODY_W_RE):
        m = rx.search(html)
        if not m:
            continue
        decls = m.group(1)
        mm = re.search(r"max-width:\s*(\d+)px", decls)
        if not mm:
            continue
        pl, pr = _h_padding(decls)
        return int(mm.group(1)) - pl - pr
    return default


def build_snippet(has_own_gallery_link: bool, width: int = 900, gap: int = 32) -> str:
    """페이지 툴바에 이미 갤러리 링크가 있으면 복귀 버튼을 빼고 워드마크만 넣는다."""
    return (
        '\n<nav id="brand-bar" '
        f'style="max-width:{width}px;width:calc(100% - {gap}px);margin:0 auto;'
        'padding:14px 20px 0;display:flex;'
        'align-items:center;gap:14px;flex-wrap:wrap;font-family:'
        "'Pretendard','Noto Sans KR',sans-serif;\">"
        '<a href="../../index.html" aria-label="aftermath — 갤러리 홈" '
        'style="line-height:0;flex-shrink:0;">'
        '<img src="../../assets/brand/wordmark.png" alt="aftermath" '
        'style="width:132px;height:auto;display:block;">'
        "</a>"
        + ("" if has_own_gallery_link else _BACK_LINK)
        + _COPY_LINK
        + _STYLE
        + _COPY_SCRIPT
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
        width = detect_content_width(t)
        snippet = build_snippet('href="../../index.html"' in t, width, detect_side_gap(t))
        t = BODY_RE.sub(lambda m: m.group(1) + snippet, t, count=1)
        open(f, "w", encoding="utf-8").write(t)
        added += 1
        print(f"  + 추가: {rel}", file=sys.stderr)
    print(f"[OK] 추가 {added} / 건너뜀 {skipped} / 실패 {failed} / 총 {len(files)}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

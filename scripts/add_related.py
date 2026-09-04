"""관련 자료 크로스링크 자동 주입 — output/ 의 각 학습자료에 '🔗 관련 자료' 섹션을
자동 생성해 넣는다. 같은 단원 + 제목 개념 토큰 공유를 기준으로 관련도를 점수화해 상위 N개 링크.

- 링크는 페이지 간 상대경로(../../학년/단원/파일.html)로 로컬·라이브 모두 동작.
- idempotent: 기존 관련 박스(id="related-box")는 제거 후 재삽입.
- A형/B형/하이브리드 모두: <footer 앞 또는 </body> 앞에 삽입.

사용법: python add_related.py [--max N]   (기본 N=4)
"""
import argparse, glob, os, re, sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError): pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO, "output")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
# 본문 실제 폭 감지 — A형은 .container(880px), B형은 body 자체(900px)에 max-width 가 있다.
# 하드코딩(과거엔 항상 880px)을 쓰면 B형(900px 본문)에서 관련자료 박스만 20px 좁아져
# 본문 하단이 어긋난다. 파일마다 실제 쓰는 폭을 읽어 그대로 맞춘다.
CONTAINER_W_RE = re.compile(r"\.container\s*\{([^}]*)\}")
BODY_W_RE = re.compile(r"(?<!\.)\bbody\s*\{([^}]*)\}")



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
    m = CONTAINER_W_RE.search(html)
    if m and re.search(r"max-width:\s*\d+px", m.group(1)):
        # A형: 주입 요소가 .container 의 형제라 호스트 패딩을 못 받는다 → 보정 필요
        pl, pr = _h_padding(m.group(1))
        return pl + pr
    # B형: 호스트가 body 자신이고 주입 요소는 그 자식이라 이미 패딩 안쪽이다 → 보정 0
    return 0

def detect_content_width(html: str, default: int = 848) -> int:
    """본문 카드가 실제로 차지하는 폭(패딩 안쪽)을 돌려준다."""
    for rx in (CONTAINER_W_RE, BODY_W_RE):
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

STOP = {"완전정복", "정리", "풀이", "공식", "활용", "기초", "기본", "심화", "전략",
        "본질", "관점", "세관점", "마스터", "정복", "핵심", "비법", "꿀팁", "특강",
        "학습자료", "계산", "줄이는", "미분법", "보는", "눈이", "바뀝니다",
        # 너무 광범위해서 '관련'의 근거가 못 되는 단어 (이것만 겹치면 관련 아님)
        "미분", "함수", "수학", "문제", "유형", "방법", "성질", "값"}


def clean_title(html: str, slug: str) -> str:
    m = TITLE_RE.search(html)
    t = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else slug
    t = re.split(r"\s*[\|]\s*|\s+-\s+", t)[0].strip()      # "| 학습자료" / " - 부제" 제거
    return t or slug


def tokens(title: str) -> set:
    out = set()
    for w in re.findall(r"[가-힣]{2,}", title):
        if w not in STOP:
            out.add(w)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=4)
    args = ap.parse_args()

    files = sorted(f for f in glob.glob(os.path.join(OUTPUT, "**", "*.html"), recursive=True)
                   if os.path.basename(f) != "index.html")
    L = []
    for f in files:
        html = open(f, encoding="utf-8", errors="replace").read()
        rel = os.path.relpath(f, OUTPUT)
        parts = rel.replace("\\", "/").split("/")
        grade, unit, slug = parts[0], (parts[1] if len(parts) >= 3 else ""), os.path.splitext(parts[-1])[0]
        vid8 = slug.split("_")[-1]
        title = clean_title(html, slug)
        L.append({"f": f, "html": html, "grade": grade, "unit": unit, "slug": slug,
                  "vid8": vid8, "title": title, "tok": tokens(title)})

    # 관련 인정 기준(억지 금지): 같은 단원이거나, 특정 개념 토큰을 실제로 공유할 때만.
    MIN_SCORE = 2

    def score(a, b):
        s = 5 if a["unit"] == b["unit"] else 0      # 같은 단원 = 확실히 관련
        s += 2 * len(a["tok"] & b["tok"])            # 공유 특정개념 1개당 +2
        return s                                      # 같은 과목만으로는 관련 아님(가점 없음)

    injected = 0
    for a in L:
        ranked = sorted(((score(a, b), b) for b in L if b is not a),
                        key=lambda x: x[0], reverse=True)
        rel_links = []
        for sc, b in ranked:
            if sc < MIN_SCORE or len(rel_links) >= args.max:
                break
            href = os.path.relpath(b["f"], os.path.dirname(a["f"])).replace("\\", "/")
            rel_links.append(f'<a href="{href}">{b["title"]} ({b["vid8"]})</a>')

        html = a["html"]
        # 기존 관련 콘텐츠 정리 (3종): ① 마커 블록 ② 정상 박스(🔗 앵커) ③ 과거 버그가 남긴 고아 링크 잔재
        html = re.sub(r"\n?<!--REL_START-->.*?<!--REL_END-->\n?", "", html, flags=re.DOTALL)
        html = re.sub(r'\n?<div class="related-box" id="related-box"[\s\S]*?🔗 관련 자료</div>[\s\S]*?</div>\n?', "", html)
        html = re.sub(r'\n?(?:\s*<a href="\.\./[^"]+\.html">[^<]*\([A-Za-z0-9_-]{6,}\)</a>(?:\s*·\s*)?)+\s*</div>\n?', "", html)

        if rel_links:
            width = detect_content_width(html)
            gap = detect_side_gap(html)
            box = ('\n<!--REL_START--><div class="related-box" id="related-box" '
                   f'style="max-width:{width}px;width:calc(100% - {gap}px);'
                   f'margin:26px auto 0;padding:14px 20px;'
                   'background:#e3f2fd;border:1px solid #e0e0e0;border-radius:10px;'
                   "font-size:.95em;font-family:'Pretendard','Noto Sans KR',sans-serif;\">"
                   '<div class="rb-title" style="font-weight:700;margin-bottom:6px;">🔗 관련 자료</div>'
                   + " · ".join(rel_links) + "</div><!--REL_END-->\n")
            if re.search(r"<footer", html, re.I):
                html = re.sub(r"(<footer)", lambda m: box + m.group(1), html, count=1, flags=re.I)
            else:
                html = re.sub(r"(</body>)", lambda m: box + m.group(1), html, count=1, flags=re.I)
            injected += 1
        if html != a["html"]:
            open(a["f"], "w", encoding="utf-8").write(html)
        print(f"  + {a['slug'][:40]:42} → 관련 {len(rel_links)}개", file=sys.stderr)

    print(f"[OK] 관련자료 주입 {injected} / 총 {len(L)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

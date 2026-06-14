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

        html = re.sub(r'\n?<div class="related-box" id="related-box".*?</div>\n?', "",
                      a["html"], flags=re.DOTALL)
        if rel_links:
            box = ('\n<div class="related-box" id="related-box" '
                   'style="max-width:880px;margin:26px auto 0;padding:14px 20px;'
                   'background:#e3f2fd;border:1px solid #e0e0e0;border-radius:10px;'
                   "font-size:.95em;font-family:'Pretendard','Noto Sans KR',sans-serif;\">"
                   '<div class="rb-title" style="font-weight:700;margin-bottom:6px;">🔗 관련 자료</div>'
                   + " · ".join(rel_links) + "</div>\n")
            if re.search(r"<footer", html, re.I):
                html = re.sub(r"(<footer)", box + r"\1", html, count=1, flags=re.I)
            else:
                html = re.sub(r"(</body>)", box + r"\1", html, count=1, flags=re.I)
            injected += 1
        if html != a["html"]:
            open(a["f"], "w", encoding="utf-8").write(html)
        print(f"  + {a['slug'][:40]:42} → 관련 {len(rel_links)}개", file=sys.stderr)

    print(f"[OK] 관련자료 주입 {injected} / 총 {len(L)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

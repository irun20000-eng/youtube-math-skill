#!/usr/bin/env python3
"""자료 HTML 의 골격이 성한지 검사한다 — <div> 짝, 그리고 태그로 오인되는 <.

둘 다 증상이 같다: 브라우저가 .container 를 예정보다 먼저 닫아 버려서, 그 뒤
본문이 통째로 화면 전체 폭으로 퍼진다(카드 기둥이 무너진다). 눈에는 "너비가
안 맞는다"로만 보이고 콘솔 에러는 없어서 놓치기 쉽다.

수식 속 부등호가 특히 위험하다. `$-2<k<2$` 의 `<k` 를 파서는 태그 시작으로
읽고 다음 `>` 까지 통째로 삼킨다 — 바로 뒤의 `</div>` 나 `<br>` 가 사라지고,
그 사이 본문도 화면에서 없어진다. 부등호는 `&lt;` 로 써야 한다.

사용:  python scripts/check_structure.py [output/...]   # 인자 없으면 output/ 전체
종료코드 1 = 깨진 파일 있음.
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO, "output")
OPEN_RE = re.compile(r"<div\b", re.I)
CLOSE_RE = re.compile(r"</div\s*>", re.I)
CONTAINER_RE = re.compile(r'<div\s+class="container"', re.I)
TAG_RE = re.compile(r"<(/?)([A-Za-z][A-Za-z0-9]*)")
# 실제로 쓰는 HTML/SVG 태그. 여기 없는 이름이 나오면 수식 부등호를 안 막은 것이다.
KNOWN_TAGS = {
    "a", "abbr", "article", "aside", "b", "body", "br", "button", "canvas", "caption",
    "circle", "code", "col", "colgroup", "dd", "defs", "details", "div", "dl", "dt",
    "ellipse", "em", "embed", "fieldset", "figcaption", "figure", "footer", "form", "g",
    "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hr", "html", "i", "iframe",
    "img", "input", "kbd", "label", "legend", "li", "line", "link", "main", "mark",
    "marker", "meta", "nav", "noscript", "object", "ol", "optgroup", "option", "p",
    "param", "path", "picture", "polygon", "polyline", "pre", "progress", "q", "rect",
    "s", "script", "section", "select", "small", "source", "span", "strong", "style",
    "sub", "summary", "sup", "svg", "table", "tbody", "td", "template", "text",
    "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track", "tspan", "u",
    "ul", "use", "video", "wbr",
}


def bogus_tags(html):
    """태그로 오인되는 < 의 (줄번호, 문맥) 목록."""
    hits = []
    for ln, line in enumerate(html.split("\n"), 1):
        for m in TAG_RE.finditer(line):
            nxt = line[m.end():m.end() + 1]
            # 진짜 태그는 이름 뒤가 공백·'/'·'>' 로 끝난다. `<k<2$` 처럼 붙어 있으면 아니다.
            if m.group(2).lower() in KNOWN_TAGS and (nxt == "" or nxt in " \t/>"):
                continue
            hits.append((ln, line[m.start():m.start() + 14]))
    return hits


def check(path):
    """(첫 붕괴 줄번호, 최종 잔여깊이) — 이상 없으면 (None, 0)."""
    lines = open(path, encoding="utf-8").read().split("\n")
    start = next((i for i, l in enumerate(lines) if CONTAINER_RE.search(l)), None)
    if start is None:
        return None, 0            # B형(컨테이너 없음)은 이 검사 대상이 아니다
    depth = 0
    first_break = None
    for i in range(start, len(lines)):
        depth += len(OPEN_RE.findall(lines[i])) - len(CLOSE_RE.findall(lines[i]))
        if depth <= 0 and first_break is None and i < len(lines) - 1:
            # 컨테이너가 닫힌 뒤에도 본문 블록이 더 남아 있으면 조기 종료다
            rest = "\n".join(lines[i + 1:])
            if re.search(r'<div\s+class="(card|section-title|review-box)', rest) or 'id="problems"' in rest:
                first_break = i + 1
    return first_break, depth


def main():
    targets = sys.argv[1:]
    if not targets:
        targets = [os.path.join(r, f) for r, _, fs in os.walk(OUTPUT)
                   for f in fs if f.endswith(".html") and f != "index.html"]
    bad = 0
    for p in sorted(targets):
        rel = os.path.relpath(p, REPO)
        html = open(p, encoding="utf-8").read()
        body = html[html.lower().find("<body"):html.lower().rfind("</body>")]
        depth = len(OPEN_RE.findall(body)) - len(CLOSE_RE.findall(body))
        line, _ = check(p)
        hits = bogus_tags(body)
        if not (line or depth or hits):
            continue
        bad += 1
        print(f"✗ {rel}")
        if line:
            print(f"    {line} 번째 줄에서 .container 가 먼저 닫힘")
        if depth:
            print(f"    <div> 짝 안 맞음: {depth:+d}")
        if hits:
            shown = ", ".join(f"{ln}행 {ctx!r}" for ln, ctx in hits[:3])
            more = f" 외 {len(hits) - 3}곳" if len(hits) > 3 else ""
            print(f"    태그로 오인되는 < {len(hits)}곳 — &lt; 로 바꿀 것: {shown}{more}")
    print(f"\n검사 {len(targets)}편 · 구조 깨진 파일 {bad}편")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

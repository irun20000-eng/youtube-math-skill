"""B형(심플) 학습자료 → 하이브리드 표준 in-place 변환.

B형 특징: hero·video-card·card·problem-card 디자인은 이미 하이브리드와 같으나
다크모드·난이도필터·툴바가 없음. 내용은 보존하고 '인터랙션 껍데기'만 주입한다.

변환 내용:
  1. <style> 를 스켈레톤의 하이브리드 <style> 로 교체(+ B 전용 잔여 클래스 보강)
  2. 단독 <nav id="gallery-back"> 제거 → 상단 툴바(복귀·다크·필터) 주입
  3. level-header / problem-card 에 'filterable {레벨}' 클래스 부여(필터 동작 조건)
  4. 맨위로 버튼 + toggleDark/filterLevel JS + pdf-mode.js 주입

대상 판별: class="toolbar" 없고 class="problem-card" 있음 (= 아직 B형). 이미 변환된 건 skip.
사용법: python migrate_b_to_hybrid.py [--only 파일경로일부]
"""
import argparse, glob, os, re, sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError): pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO, "output")
SKEL = os.path.join(REPO, "templates", "lesson-hybrid-skeleton.html")

HYBRID_STYLE = re.search(r"<style>.*?</style>", open(SKEL, encoding="utf-8").read(), re.S).group(0)
EXTRA_STYLE = (
    "\n  <style>\n"
    "  hr.divider{border:none;border-top:1px solid var(--border);margin:30px 0;}\n"
    "  table{border-collapse:collapse;width:100%;} th,td{padding:10px;border:1px solid var(--border);text-align:center;} th{background:var(--box-blue);}\n"
    "  .step{margin:10px 0;}\n  </style>"
)
TOOLBAR = (
    '<div class="toolbar">\n'
    '    <a class="back" id="gallery-back" href="../../index.html">🏠 갤러리</a>\n'
    '    <button onclick="toggleDark()">🌙 다크모드</button>\n'
    '    <span class="spacer"></span>\n'
    '    <button class="flt active" onclick="filterLevel(\'all\', this)">전체</button>\n'
    '    <button class="flt" onclick="filterLevel(\'basic\', this)">기초</button>\n'
    '    <button class="flt" onclick="filterLevel(\'standard\', this)">기본</button>\n'
    '    <button class="flt" onclick="filterLevel(\'advanced\', this)">심화</button>\n'
    '    <button class="flt" onclick="filterLevel(\'csat\', this)">수능 대비</button>\n'
    '  </div>\n'
)
SCRIPTS = (
    '\n  <button id="scrollTopBtn" onclick="window.scrollTo({top:0,behavior:\'smooth\'})" title="맨 위로">↑</button>\n'
    '  <script>\n'
    '    function toggleDark(){document.body.classList.toggle(\'dark\');}\n'
    '    function filterLevel(level,btn){\n'
    '      document.querySelectorAll(\'.toolbar .flt\').forEach(b=>b.classList.remove(\'active\'));\n'
    '      if(btn)btn.classList.add(\'active\');\n'
    '      document.querySelectorAll(\'.filterable\').forEach(el=>{el.style.display=(level===\'all\'||el.classList.contains(level))?\'\':\'none\';});\n'
    '      if(level!==\'all\'){const f=document.querySelector(\'.level-header\');if(f)f.scrollIntoView({behavior:\'smooth\',block:\'start\'});}\n'
    '    }\n'
    '    window.addEventListener(\'scroll\',()=>{const b=document.getElementById(\'scrollTopBtn\');if(b)b.style.display=window.scrollY>400?\'block\':\'none\';});\n'
    '    document.addEventListener(\'keydown\',e=>{if(e.target.tagName===\'INPUT\'||e.target.tagName===\'TEXTAREA\')return;if(e.key===\'d\'||e.key===\'D\')toggleDark();});\n'
    '  </script>\n'
)


def add_filterable(html: str) -> str:
    # 1) level-header 에 레벨 클래스
    html = re.sub(
        r'<div class="level-header">(\s*<span class="level-badge badge-(basic|standard|advanced|csat)")',
        lambda m: f'<div class="level-header filterable {m.group(2)}">{m.group(1)}', html)
    # 2) problem-card 에 직전 level-header 의 레벨 부여(stateful)
    cur = {"lv": ""}
    def walk(m):
        if m.group(1):                       # level-header (이미 레벨 표시됨)
            cur["lv"] = m.group(2); return m.group(0)
        return f'<div class="problem-card filterable {cur["lv"]}"'
    html = re.sub(
        r'(<div class="level-header filterable (basic|standard|advanced|csat)")|(<div class="problem-card")',
        walk, html)
    return html


def migrate(html: str) -> str:
    html = re.sub(r"<style>.*?</style>", lambda m: HYBRID_STYLE + EXTRA_STYLE, html, count=1, flags=re.S)
    html = re.sub(r"\n?<nav id=\"gallery-back\".*?</nav>\n?", "", html, flags=re.S)
    html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n  " + TOOLBAR, html, count=1, flags=re.I)
    html = add_filterable(html)
    if "../../pdf-mode.js" not in html:
        scripts = SCRIPTS + '  <script defer src="../../pdf-mode.js"></script>\n'
    else:
        scripts = SCRIPTS
    html = re.sub(r"(</body>)", lambda m: scripts + m.group(1), html, count=1, flags=re.I)
    return html


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="경로 일부 일치하는 파일만")
    args = ap.parse_args()
    files = sorted(f for f in glob.glob(os.path.join(OUTPUT, "**", "*.html"), recursive=True)
                   if os.path.basename(f) != "index.html")
    done = skip = 0
    for f in files:
        if args.only and args.only not in f:
            continue
        html = open(f, encoding="utf-8", errors="replace").read()
        rel = os.path.relpath(f, OUTPUT)
        if 'class="toolbar"' in html or 'class="problem-card"' not in html:
            skip += 1; print(f"  - skip(B형 아님/이미 변환): {rel}", file=sys.stderr); continue
        out = migrate(html)
        open(f, "w", encoding="utf-8").write(out)
        done += 1; print(f"  + 변환: {rel}", file=sys.stderr)
    print(f"[OK] 변환 {done} / skip {skip}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

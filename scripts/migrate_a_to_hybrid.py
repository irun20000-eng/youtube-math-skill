"""A형(인터랙티브) 학습자료 → 하이브리드 표준 in-place 변환.

A형 특징: 다크모드·난이도필터·검증박스는 이미 있으나(JS 포함) 헤더가 밋밋(B 스타일 hero·썸네일 없음).
A의 콘텐츠 CSS(article.problem, concept-block 등)와 JS(toggleDarkMode, filterLevel)는 그대로 두고,
  1) B 스타일 hero(영상 썸네일 카드) CSS 추가 + 밋밋한 <header> 를 hero 로 교체
  2) <div class="controls"> 를 스티키 툴바로 교체(클래스 controls 유지 → A의 기존 JS가 그대로 동작)
  3) 단독 gallery-back nav 제거(툴바에 복귀 버튼 포함)
만 수행한다(콘텐츠·JS 무수정 = 저위험).

대상 판별: class="controls" 있고 'article class="problem"' 있고 class="hero" 없음.
사용법: python migrate_a_to_hybrid.py [--only 일부]
"""
import argparse, glob, os, re, sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError): pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO, "output")
VID_RE = re.compile(r"(?:v=|/live/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})")

HERO_CSS = """
    /* === 하이브리드 이관: B 스타일 hero + 스티키 툴바 (A 변수 사용) === */
    .hero{background:linear-gradient(135deg,#1a237e,#1565c0 60%,#0288d1);color:#fff;padding:34px 28px;border-radius:14px;text-align:center;margin-bottom:24px;}
    .hero .tag{display:inline-block;background:rgba(255,255,255,.18);border-radius:20px;padding:4px 16px;font-size:13px;margin-bottom:12px;}
    .hero h1{font-size:clamp(1.4rem,4vw,1.9rem);font-weight:800;line-height:1.35;margin-bottom:10px;color:#fff;border:none;}
    .hero p.sub{font-size:15px;opacity:.93;max-width:660px;margin:0 auto;}
    .video-card{max-width:680px;margin:22px auto 0;background:var(--summary-bg);border:1px solid var(--border);border-radius:12px;padding:14px;display:flex;gap:14px;align-items:center;text-align:left;}
    .video-card a.thumb{flex-shrink:0;position:relative;width:180px;aspect-ratio:16/9;border-radius:8px;overflow:hidden;background:#000;display:block;}
    .video-card .thumb img{width:100%;height:100%;object-fit:cover;display:block;}
    .video-card .play-icon{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:44px;height:44px;background:rgba(229,57,53,.92);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;}
    .video-card .info{flex:1;min-width:0;color:var(--text);}
    .video-card .v-title{font-weight:700;font-size:15px;margin-bottom:4px;}
    .video-card .v-meta{font-size:13px;opacity:.75;margin-bottom:6px;}
    .video-card .v-link{font-size:13px;color:var(--standard);word-break:break-all;}
    .controls.hybrid-toolbar{position:sticky;top:0;z-index:50;margin:-24px -20px 20px;padding:10px 16px;background:var(--bg);border-bottom:1px solid var(--border);}
    .controls.hybrid-toolbar .spacer{flex:1;}
    .controls.hybrid-toolbar a.back{padding:7px 14px;border-radius:8px;border:1px solid var(--standard);background:var(--standard);color:#fff;text-decoration:none;font-weight:600;font-size:.9em;}
    .pdf-toolbar{top:64px !important;}
    @media(max-width:600px){.video-card{flex-direction:column;align-items:stretch;}.video-card a.thumb{width:100%;}}
"""

TOOLBAR = """<div class="controls hybrid-toolbar">
    <a class="back" id="gallery-back" href="../../index.html">🏠 갤러리</a>
    <button id="darkModeToggle" onclick="toggleDarkMode()">🌙 다크모드</button>
    <span class="spacer"></span>
    <button onclick="filterLevel('all', this)" class="active">전체</button>
    <button onclick="filterLevel('basic', this)">기초</button>
    <button onclick="filterLevel('standard', this)">기본</button>
    <button onclick="filterLevel('advanced', this)">심화</button>
    <button onclick="filterLevel('exam-style', this)">수능 대비</button>
  </div>
"""


def build_hero(header_html: str) -> str:
    m = re.search(r"<h1>(.*?)</h1>", header_html, re.S)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "학습자료"
    url_m = re.search(r'href="(https?://[^"]*(?:youtube\.com|youtu\.be)[^"]*)"', header_html)
    url = url_m.group(1) if url_m else ""
    vid_m = VID_RE.search(url)
    vid = vid_m.group(1) if vid_m else ""
    paren = re.search(r"📺[^(]*\(([^)]*)\)", header_html)
    meta = paren.group(1).strip() if paren else ""
    goal = re.search(r"🎯[^:：]*[:：]\s*(.*?)</p>", header_html, re.S)
    sub = re.sub(r"\s+", " ", goal.group(1)).strip() if goal else ""
    tag = re.search(r"📚[^:：]*[:：]\s*(\[[^\]]*\])", header_html)
    tagtxt = tag.group(1) if tag else "수학 학습자료"

    vcard = ""
    if vid:
        vcard = (
            f'<div class="video-card"><a class="thumb" href="{url}" target="_blank" rel="noopener">'
            f'<img src="https://img.youtube.com/vi/{vid}/hqdefault.jpg" alt="영상 썸네일" loading="lazy" />'
            f'<span class="play-icon">▶</span></a><div class="info">'
            f'<div class="v-title">원본 영상</div><div class="v-meta">📺 {meta}</div>'
            f'<a class="v-link" href="{url}" target="_blank" rel="noopener">{url}</a></div></div>'
        )
    sub_html = f'<p class="sub">🎯 {sub}</p>' if sub else ""
    return (f'<div class="hero"><div class="tag">{tagtxt}</div><h1>{title}</h1>'
            f'{sub_html}{vcard}</div>')


def migrate(html: str) -> str:
    html = re.sub(r"(</style>)", lambda m: HERO_CSS + "  " + m.group(1), html, count=1)
    html = re.sub(r"\n?<nav id=\"gallery-back\".*?</nav>\n?", "", html, flags=re.S)
    hm = re.search(r"<header>(.*?)</header>", html, re.S)
    hero = build_hero(hm.group(1)) if hm else ""
    html = re.sub(r"<header>.*?</header>", lambda m: hero, html, count=1, flags=re.S)
    html = re.sub(r'<div class="controls">.*?</div>', "", html, count=1, flags=re.S)      # 기존 컨트롤 제거
    html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n  " + TOOLBAR, html, count=1, flags=re.I)  # 툴바 맨 위로
    return html


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    files = sorted(f for f in glob.glob(os.path.join(OUTPUT, "**", "*.html"), recursive=True)
                   if os.path.basename(f) != "index.html")
    done = skip = 0
    for f in files:
        if args.only and args.only not in f:
            continue
        html = open(f, encoding="utf-8", errors="replace").read()
        rel = os.path.relpath(f, OUTPUT)
        if ('class="controls"' not in html or '<article class="problem' not in html
                or 'class="hero"' in html):
            skip += 1; print(f"  - skip(A형 아님/이미 hero): {rel}", file=sys.stderr); continue
        open(f, "w", encoding="utf-8").write(migrate(html))
        done += 1; print(f"  + 변환: {rel}", file=sys.stderr)
    print(f"[OK] 변환 {done} / skip {skip}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

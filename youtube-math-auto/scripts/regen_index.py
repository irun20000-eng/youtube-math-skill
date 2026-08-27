"""output/ 디렉토리를 스캔해 INDEX.md + index.html(갤러리)을 자동 재생성.

- 명명 규칙(output_path.parse_output_path)을 만족하는 .html만 카탈로그함
- 각 HTML의 <title>·URL·채널을 추출해 보강
- INDEX.md: 학년 → 단원 → 날짜 역순 마크다운 카탈로그
- index.html: 썸네일·필터·검색·다크모드 갤러리

사용:
    python regen_index.py [output_dir]
"""
from __future__ import annotations

import html as html_mod
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from output_path import extract_video_id_from_url, parse_output_path

TITLE_RE = re.compile(r"<title>(.+?)</title>", re.IGNORECASE | re.DOTALL)
# 표준 형식 (PC 자료): <p class="meta-row">📺 영상: <a href="...">
URL_RE_STRICT = re.compile(r'영상[:\s]*<a[^>]*href="(https?://[^"]+)"', re.IGNORECASE)
# 폴백: 본문 어디든 첫 YouTube URL 매칭 (모바일/타 세션 자료 호환)
URL_RE_FALLBACK = re.compile(
    r'href="(https?://(?:www\.|m\.)?'
    r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/live/|youtube\.com/embed/|youtube\.com/shorts/)'
    r'[A-Za-z0-9_-]{11}[^"]*)"',
    re.IGNORECASE,
)
# 채널: 표준 패턴 + 폴백 (다른 형식)
CHANNEL_RE_STRICT = re.compile(r'\((.+?),\s*\d+분\)', re.IGNORECASE)
CHANNEL_RE_FALLBACK = re.compile(
    r'(?:채널|channel)[:\s]*<[^>]*>([^<]+)<', re.IGNORECASE
)


def extract_meta(html_path: Path) -> dict:
    """HTML 파일에서 title·URL·채널 정보 추출 (실패해도 None으로 채움).

    URL 추출은 두 단계:
    1. 표준 헤더 패턴 ("영상: <a href=...>") 우선
    2. 못 찾으면 본문 어디서든 첫 YouTube URL 채택 (모바일·타 세션 자료 커버)
    """
    try:
        text = html_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {"title": None, "url": None, "channel": None}

    title_m = TITLE_RE.search(text)
    title = title_m.group(1).strip() if title_m else None
    if title:
        title = re.sub(r"\s*[—\|-]\s*학습자료.*$", "", title).strip()
        # 갤러리는 KaTeX 미적용 → $...$ 수식 평문으로 보이므로 제거.
        title = title.replace("$", "").replace("\\", "")
        title = re.sub(r"\s+", " ", title).strip()

    # URL: 엄격 패턴 → 폴백 순으로 시도
    url_m = URL_RE_STRICT.search(text) or URL_RE_FALLBACK.search(text)
    url = url_m.group(1) if url_m else None

    # 채널: 엄격 패턴 → 폴백
    chan_m = CHANNEL_RE_STRICT.search(text) or CHANNEL_RE_FALLBACK.search(text)
    channel = chan_m.group(1).strip() if chan_m else None

    return {"title": title, "url": url, "channel": channel}


def git_added_map(output_dir: Path) -> dict[str, str]:
    """파일별 '갤러리에 처음 추가된 시각'(git 최초 커밋)을 rel_path → ISO 로 반환.

    갤러리 기본 정렬을 '영상 게시일'이 아니라 '자료 추가일'로 쓰기 위한 자료.
    (옛날 영상으로 오늘 만든 자료가 목록 한참 아래에 묻히는 문제를 없앤다.)

    git 이 없거나 저장소가 아니면 빈 dict → 호출부에서 영상 게시일로 폴백하므로
    이 함수 실패가 카탈로그 생성 자체를 막지 않는다.
    한 번의 git log 로 전부 훑어 파일 수만큼 git 을 호출하지 않는다.
    """
    try:
        out = subprocess.run(
            # core.quotepath=false: 이걸 안 끄면 git 이 한글 경로를
            # "output/\352\263\2401/..." 처럼 8진수로 인용해 매칭이 전부 어긋난다.
            # --no-renames: 이름이 바뀐 파일은 rename(R)로 잡혀 --diff-filter=A 에서
            # 통째로 빠진다. 껐을 때 D+A 로 쪼개져 '현재 경로에 등장한 시점'이 잡힌다.
            ["git", "-c", "core.quotepath=false",
             "log", "--diff-filter=A", "--no-renames", "--name-only",
             "--format=%H%x09%aI", "--", "."],
            cwd=output_dir, capture_output=True, text=True, timeout=60,
        )
        if out.returncode != 0:
            return {}
    except (OSError, subprocess.SubprocessError):
        return {}

    added: dict[str, str] = {}
    stamp = None
    for line in out.stdout.splitlines():
        if not line.strip():
            continue
        if "\t" in line:                      # "<sha>\t<iso>" 헤더 줄
            stamp = line.split("\t", 1)[1].strip()
            continue
        if stamp is None:
            continue
        # git 은 저장소 루트 기준 경로를 준다 → output/ 기준으로 바꾼다
        rel = line.strip()
        rel = rel[len("output/"):] if rel.startswith("output/") else rel
        # 최초 추가가 최종값이 되도록: git log 는 최신→과거 순이라 계속 덮어쓴다
        added[rel] = stamp
    return added


def gather(output_dir: Path) -> list[dict]:
    added_map = git_added_map(output_dir)
    rows = []
    for html in sorted(output_dir.rglob("*.html")):
        if html.name == "index.html":
            continue
        rel = html.relative_to(output_dir)
        is_concept = html.stem.endswith("_개념")
        parsed = parse_output_path(rel)
        if not parsed and is_concept and len(rel.parts) >= 3:
            # 개념 자료(_개념): 영상 ID 대신 명시 접미사 → 폴백 파싱
            m = re.match(r"(\d{8})_(.+)_개념$", html.stem)
            if m:
                parsed = {"grade": rel.parts[0], "unit": rel.parts[1],
                          "date": m.group(1), "topic": m.group(2),
                          "video_id_short": html.stem}
        if not parsed:
            continue
        meta = extract_meta(html)
        # URL에서 풀 11자 video_id 복구 (썸네일·중복 감지에 필요)
        full_vid = extract_video_id_from_url(meta["url"]) if meta["url"] else None
        rel_posix = rel.as_posix()
        d = parsed["date"]
        rows.append({
            **parsed,
            **meta,
            "video_id_full": full_vid,
            "rel_path": rel_posix,
            "source": "concept" if is_concept else "video",
            # 추가일(git 최초 커밋). 못 구하면 영상 게시일 자정으로 폴백해
            # 정렬이 뒤섞이지 않게 한다.
            "added": added_map.get(
                rel_posix, f"{d[:4]}-{d[4:6]}-{d[6:8]}T00:00:00+00:00"),
        })
    return rows


def detect_duplicates(rows: list[dict]) -> dict[str, list[dict]]:
    """같은 video_id_short(8자)를 가진 자료가 2개 이상 있으면 보고."""
    by_vid: dict[str, list[dict]] = {}
    for r in rows:
        if r.get("source") == "concept":   # 개념 자료는 영상 중복 판정 제외
            continue
        by_vid.setdefault(r["video_id_short"], []).append(r)
    return {k: v for k, v in by_vid.items() if len(v) > 1}


def render_markdown(rows: list[dict], output_dir: Path) -> str:
    """학년 → 단원 → 날짜(역순) 그룹핑 마크다운."""
    by_grade: dict[str, dict[str, list[dict]]] = {}
    for r in rows:
        by_grade.setdefault(r["grade"], {}).setdefault(r["unit"], []).append(r)

    lines = [
        "# 학습자료 인덱스",
        "",
        f"_마지막 갱신: {datetime.now():%Y-%m-%d %H:%M}_",
        f"_총 {len(rows)}개 자료 / {len(by_grade)}개 학년_",
        "",
    ]

    for grade in sorted(by_grade.keys()):
        units = by_grade[grade]
        total = sum(len(v) for v in units.values())
        lines.append(f"## 📚 {grade} ({total}개)")
        lines.append("")
        for unit in sorted(units.keys()):
            items = sorted(units[unit], key=lambda x: x["date"], reverse=True)
            lines.append(f"### {unit}")
            lines.append("")
            lines.append("| 생성일 | 주제 | 영상 | 파일 |")
            lines.append("|--------|------|------|------|")
            for r in items:
                d = r["date"]
                date_fmt = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
                topic = r["topic"]
                title = r.get("title") or "(제목 없음)"
                url = r.get("url")
                channel = r.get("channel")
                video_label = (
                    f"[{title}]({url})" + (f" — {channel}" if channel else "")
                    if url else title
                )
                file_link = f"[HTML]({r['rel_path']})"
                lines.append(f"| {date_fmt} | {topic} | {video_label} | {file_link} |")
            lines.append("")
        lines.append("")

    if not rows:
        lines.append("_아직 생성된 자료가 없습니다._")

    return "\n".join(lines) + "\n"


GALLERY_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>aftermath — 수학 학습자료</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
  :root {
    --bg: #f7f7f9; --card: #fff; --text: #1a1a1a; --muted: #666;
    --border: #e0e0e0; --accent: #2196f3; --tag-bg: #eef2ff; --tag-text: #4338ca;
    --grade-bg: #fef3c7; --grade-text: #92400e;
    --warning-bg: #fef2f2; --warning-text: #991b1b; --warning-border: #fca5a5;
  }
  body.dark {
    --bg: #0f0f12; --card: #1a1a1f; --text: #e0e0e0; --muted: #999;
    --border: #2d2d33; --accent: #60a5fa; --tag-bg: #1e1b4b; --tag-text: #c7d2fe;
    --grade-bg: #422006; --grade-text: #fbbf24;
    --warning-bg: #2d1414; --warning-text: #fca5a5; --warning-border: #7f1d1d;
  }
  * { box-sizing: border-box; }
  body {
    font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
    background: var(--bg); color: var(--text); margin: 0; padding: 24px 16px 60px;
    line-height: 1.5; transition: background 0.2s, color 0.2s;
  }
  .wrap { max-width: 1200px; margin: 0 auto; }
  header { margin-bottom: 24px; }
  /* 브랜드 워드마크 — aftermath. 파랑/회색이라 라이트·다크 양쪽에서 읽힌다 */
  .brandbar { display:flex; align-items:baseline; gap:10px; margin:0 0 10px; flex-wrap:wrap; }
  .wordmark { display:inline-block; line-height:0; }
  .wordmark img { width:200px; height:auto; display:block; }
  /* 핸들은 이미지가 아니라 텍스트 — 브랜드 자산의 핸들은 네이비라 다크에서 사라진다 */
  .handle { font-family:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
            font-size:.82em; color:var(--muted); letter-spacing:.02em; }
  @media (max-width:600px){ .wordmark img { width:168px; } .handle{ font-size:.76em; } }
  header h1 { margin: 0 0 4px; font-size: 1.35em; font-weight:600; letter-spacing:-.01em; }
  .stats { color: var(--muted); font-size: 0.95em; }
  .controls {
    display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
    margin: 18px 0; padding: 14px 16px; background: var(--card);
    border: 1px solid var(--border); border-radius: 10px;
  }
  .controls .group { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .controls .group .label { color: var(--muted); font-size: 0.9em; margin-right: 4px; }
  .controls input[type=search] {
    flex: 1; min-width: 180px; padding: 8px 12px;
    border: 1px solid var(--border); border-radius: 6px;
    background: var(--bg); color: var(--text); font: inherit;
  }
  .controls button {
    padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px;
    background: var(--bg); color: var(--text); cursor: pointer; font: inherit; font-size: 0.9em;
    transition: all 0.15s;
  }
  .controls button:hover { border-color: var(--accent); }
  .controls button.active {
    background: var(--accent); color: #fff; border-color: var(--accent);
  }
  .gallery {
    display: grid; gap: 16px;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    overflow: hidden; transition: transform 0.15s, box-shadow 0.15s;
    display: flex; flex-direction: column;
  }
  .card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
  .card.hidden { display: none; }
  .thumb-wrap {
    position: relative; aspect-ratio: 16/9; background: var(--border);
    overflow: hidden;
  }
  .thumb-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .thumb-wrap .badge {
    position: absolute; top: 8px; left: 8px;
    background: rgba(0,0,0,0.7); color: #fff; padding: 3px 8px;
    border-radius: 4px; font-size: 0.78em; font-weight: 600;
  }
  .thumb-wrap .date {
    position: absolute; bottom: 8px; right: 8px;
    background: rgba(0,0,0,0.7); color: #fff; padding: 3px 8px;
    border-radius: 4px; font-size: 0.78em;
  }
  /* 최근 추가분 표시 — '언제 추가됐나'는 보는 시점 기준이라 JS가 켠다
     (빌드 결과에 '지금'을 굽지 않아 재생성해도 파일이 안 흔들린다) */
  .thumb-wrap .new-badge {
    position: absolute; top: 8px; right: 8px;
    background: #e53935; color: #fff; padding: 3px 8px;
    border-radius: 4px; font-size: 0.78em; font-weight: 700;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
  }
  .thumb-wrap .new-badge[hidden] { display: none; }
  .result-count { font-size: 0.88em; opacity: 0.75; align-self: center; }
  .info { padding: 12px 14px; flex: 1; display: flex; flex-direction: column; gap: 6px; }
  .info h3 {
    margin: 0; font-size: 1.0em; line-height: 1.35;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }
  .info .channel { color: var(--muted); font-size: 0.85em; }
  .info .tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: auto; padding-top: 8px; }
  .tag {
    padding: 2px 8px; border-radius: 4px; font-size: 0.78em;
    background: var(--tag-bg); color: var(--tag-text);
  }
  .tag.grade { background: var(--grade-bg); color: var(--grade-text); font-weight: 600; }
  .actions { display: flex; border-top: 1px solid var(--border); }
  .actions a {
    flex: 1; text-align: center; padding: 9px 8px;
    text-decoration: none; color: var(--text); font-size: 0.88em; font-weight: 500;
    transition: background 0.1s;
  }
  .actions a:hover { background: var(--bg); }
  .actions a.primary { color: var(--accent); }
  .actions a + a { border-left: 1px solid var(--border); }
  .empty { text-align: center; padding: 40px 20px; color: var(--muted); }
  .duplicates {
    background: var(--warning-bg); color: var(--warning-text);
    border: 1px solid var(--warning-border); border-radius: 8px;
    padding: 12px 16px; margin: 14px 0;
  }
  .duplicates summary { cursor: pointer; font-weight: 600; }
  .duplicates ul { margin: 8px 0 0; padding-left: 20px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="brandbar"><a class="wordmark" href="./index.html" aria-label="aftermath — 수학 학습자료 갤러리 홈">
      <img src="assets/brand/wordmark.png" alt="aftermath" width="200" height="41">
    </a>
    <span class="handle">@irun20000</span></div>
    <h1>수학 학습자료</h1>
    <div class="stats">__STATS__ · 갱신 __UPDATED__</div>
  </header>

  __DUPLICATES_BLOCK__

  <div class="controls">
    <input type="search" id="q" placeholder="🔎 제목 · 주제 · 채널 검색">
    <button id="darkBtn" type="button">🌙</button>
  </div>

  <div class="controls">
    <div class="group">
      <span class="label">학년</span>
      __GRADE_BUTTONS__
    </div>
  </div>

  <div class="controls">
    <div class="group" id="sourceFilter">
      <span class="label">출처</span>
      <button data-source="all" class="active">전체</button>
      <button data-source="video">🎬 영상</button>
      <button data-source="concept">📘 개념</button>
    </div>
  </div>

  <div class="controls">
    <div class="group" id="unitFilter">
      <span class="label">단원</span>
      <button data-unit="all" class="active">전체</button>
    </div>
  </div>

  <div class="controls">
    <div class="group" id="sortGroup">
      <span class="label">정렬</span>
      <button data-sort="added" class="active">🆕 최근 추가순</button>
      <button data-sort="date">📅 영상 게시일순</button>
    </div>
    <span class="result-count" id="resultCount"></span>
  </div>

  <main class="gallery" id="gallery">
    __CARDS__
  </main>

  <div class="empty" id="empty" style="display:none">조건에 맞는 자료가 없습니다.</div>
</div>

<script>
const ITEMS = __ITEMS_JSON__;
const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);
let state = { grade: 'all', unit: 'all', source: 'all', q: '', sort: 'added' };

function rebuildUnitFilter() {
  const units = new Set();
  ITEMS.forEach(it => {
    if (state.grade === 'all' || it.grade === state.grade) units.add(it.unit);
  });
  const wrap = $('#unitFilter');
  wrap.querySelectorAll('button:not([data-unit="all"])').forEach(b => b.remove());
  [...units].sort().forEach(u => {
    const b = document.createElement('button');
    b.dataset.unit = u; b.textContent = u;
    b.onclick = () => { state.unit = u; setActive(wrap, b); apply(); };
    wrap.appendChild(b);
  });
  if (![...units].includes(state.unit)) {
    state.unit = 'all';
    wrap.querySelector('[data-unit="all"]').classList.add('active');
  }
}

function setActive(group, btn) {
  group.querySelectorAll('button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

function apply() {
  const q = state.q.trim().toLowerCase();
  let visible = 0;
  $$('.card').forEach(card => {
    const ok =
      (state.grade === 'all' || card.dataset.grade === state.grade) &&
      (state.unit === 'all' || card.dataset.unit === state.unit) &&
      (state.source === 'all' || card.dataset.source === state.source) &&
      (!q || card.dataset.search.includes(q));
    card.classList.toggle('hidden', !ok);
    if (ok) visible++;
  });
  $('#empty').style.display = visible === 0 ? 'block' : 'none';
  const total = $$('.card').length;
  $('#resultCount').textContent =
    visible === total ? `${total}개 전체` : `${visible} / ${total}개 표시`;
}

// 정렬 — 카드를 실제로 재배치한다. 'added'(추가일)가 기본이고 'date'(영상 게시일)로 전환 가능.
function applySort() {
  const gallery = $('#gallery');
  const cards = [...$$('.card')];
  const key = state.sort === 'date' ? 'date' : 'added';
  cards.sort((a, b) => {
    const av = a.dataset[key] || '', bv = b.dataset[key] || '';
    if (av !== bv) return av < bv ? 1 : -1;          // 최신순
    // 동률이면 나머지 키로 갈라 순서가 흔들리지 않게 한다
    const a2 = a.dataset[key === 'added' ? 'date' : 'added'] || '';
    const b2 = b.dataset[key === 'added' ? 'date' : 'added'] || '';
    return a2 === b2 ? 0 : (a2 < b2 ? 1 : -1);
  });
  cards.forEach(c => gallery.appendChild(c));
}

// 최근 7일 안에 추가된 자료에 🆕 — 보는 시점 기준으로 JS가 판단한다
function markNew() {
  const WEEK = 7 * 24 * 60 * 60 * 1000;
  const now = Date.now();
  $$('.card').forEach(card => {
    const t = Date.parse(card.dataset.added || '');
    const badge = card.querySelector('.new-badge');
    if (badge) badge.hidden = !(t && now - t < WEEK);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // .controls 로 한정 — 카드(article)도 data-grade/data-source 를 갖고 있어서
  // 범위를 안 좁히면 카드를 누르는 것만으로 필터가 바뀐다.
  $$('.controls [data-grade]').forEach(b => {
    b.onclick = () => {
      state.grade = b.dataset.grade;
      setActive(b.parentElement, b);
      rebuildUnitFilter();
      apply();
    };
  });
  $$('.controls [data-source]').forEach(b => {
    b.onclick = () => {
      state.source = b.dataset.source;
      setActive(b.parentElement, b);
      apply();
    };
  });
  $$('[data-sort]').forEach(b => {
    b.onclick = () => {
      state.sort = b.dataset.sort;
      setActive(b.parentElement, b);
      applySort();
    };
  });
  rebuildUnitFilter();
  markNew();
  applySort();
  apply();
  $('#q').oninput = e => { state.q = e.target.value; apply(); };
  $('#darkBtn').onclick = () => {
    document.body.classList.toggle('dark');
    localStorage.setItem('gallery-dark', document.body.classList.contains('dark') ? '1' : '0');
  };
  if (localStorage.getItem('gallery-dark') === '1') document.body.classList.add('dark');
  document.addEventListener('keydown', e => {
    if (e.target.tagName === 'INPUT') return;
    if (e.key === 'd' || e.key === 'D') $('#darkBtn').click();
    if (e.key === '/' && document.activeElement !== $('#q')) {
      e.preventDefault(); $('#q').focus();
    }
  });
});
</script>
</body>
</html>
"""


def _esc(s: str | None) -> str:
    return html_mod.escape(s or "", quote=True)


def render_html(rows: list[dict], dups: dict[str, list[dict]]) -> str:
    grades = sorted({r["grade"] for r in rows})

    grade_btns = ['<button data-grade="all" class="active">전체</button>']
    for g in grades:
        grade_btns.append(f'<button data-grade="{_esc(g)}">{_esc(g)}</button>')

    cards = []
    items = []
    # 기본 정렬 = 자료 추가일(최신순). 영상 게시일순은 갤러리에서 토글로 전환한다.
    for r in sorted(rows, key=lambda x: (x["added"], x["date"], x["grade"]),
                    reverse=True):
        vid = r.get("video_id_full")
        thumb = (
            f"https://img.youtube.com/vi/{vid}/mqdefault.jpg"
            if vid else ""
        )
        title = r.get("title") or r["topic"]
        channel = r.get("channel") or ""
        url = r.get("url") or ""
        rel_path = r["rel_path"]
        d = r["date"]
        date_fmt = f"{d[:4]}.{d[4:6]}.{d[6:8]}"
        search_text = " ".join(filter(None, [
            title, r["topic"], channel, r["unit"], r["grade"]
        ])).lower()

        is_concept = r.get("source") == "concept"
        if thumb:
            thumb_html = f'<img src="{_esc(thumb)}" loading="lazy" alt="{_esc(title)}">'
        elif is_concept:
            thumb_html = '<div style="display:flex;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#6a1b9a,#8e24aa);color:#fff;font-weight:700">📘 개념 학습자료</div>'
        else:
            thumb_html = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#999">썸네일 없음</div>'
        src_badge = '📘 개념' if is_concept else '🎬 영상'
        original_link = (
            f'<a href="{_esc(url)}" target="_blank" rel="noopener">▶ 원본</a>'
            if url else ''
        )
        cards.append(f'''<article class="card" data-grade="{_esc(r["grade"])}" data-unit="{_esc(r["unit"])}" data-source="{_esc(r.get("source","video"))}" data-added="{_esc(r["added"])}" data-date="{_esc(r["date"])}" data-search="{_esc(search_text + " " + src_badge)}">
  <a href="{_esc(rel_path)}" class="thumb-wrap">
    {thumb_html}
    <span class="badge">{_esc(r["grade"])}</span>
    <span class="new-badge" hidden>🆕 NEW</span>
    <span class="date">{date_fmt}</span>
  </a>
  <div class="info">
    <h3><a href="{_esc(rel_path)}" style="color:inherit;text-decoration:none">{_esc(title)}</a></h3>
    {f'<div class="channel">📺 {_esc(channel)}</div>' if channel else ''}
    <div class="tags">
      <span class="tag grade">{_esc(r["grade"])}</span>
      <span class="tag">{src_badge}</span>
      <span class="tag">{_esc(r["unit"])}</span>
    </div>
  </div>
  <div class="actions">
    <a href="{_esc(rel_path)}" class="primary">📖 학습자료 열기</a>
    {original_link}
  </div>
</article>''')
        items.append({
            "grade": r["grade"], "unit": r["unit"], "title": title,
        })

    dup_block = ""
    if dups:
        items_html = []
        for vid, group in dups.items():
            paths = ", ".join(f"<code>{_esc(g['rel_path'])}</code>" for g in group)
            items_html.append(f"<li><strong>{_esc(vid)}</strong> ({len(group)}개 파일): {paths}</li>")
        dup_block = (
            '<details class="duplicates" open>'
            f'<summary>⚠️ 중복 영상 감지: {len(dups)}개 (같은 video_id로 여러 파일)</summary>'
            f'<ul>{"".join(items_html)}</ul>'
            '</details>'
        )

    if not rows:
        cards = ['<div class="empty">아직 생성된 자료가 없습니다.</div>']

    stats = f"총 {len(rows)}개 자료 · {len(grades)}개 학년"
    if dups:
        stats += f" · ⚠️ 중복 {len(dups)}건"

    return (GALLERY_TEMPLATE
            .replace("__STATS__", stats)
            .replace("__UPDATED__", f"{datetime.now():%Y-%m-%d %H:%M}")
            .replace("__DUPLICATES_BLOCK__", dup_block)
            .replace("__GRADE_BUTTONS__", "\n      ".join(grade_btns))
            .replace("__CARDS__", "\n    ".join(cards))
            .replace("__ITEMS_JSON__", json.dumps(items, ensure_ascii=False)))


def render_manifest(rows: list[dict]) -> str:
    """이룬 서재(허브)가 편수를 읽어 가는 조회표를 만든다.

    허브는 같은 오리진의 /youtube-math-skill/manifest.json 을 런타임에 fetch 해
    편수를 채우고, 없거나 실패하면 조용히 '바로가기'로 남긴다.
    생성 시각 같은 가변값을 넣지 않아 빌드는 결정적으로 유지된다.
    """
    items = []
    for r in sorted(rows, key=lambda x: (x.get("grade") or "", x.get("unit") or "",
                                         x.get("date") or "", x.get("rel_path") or "")):
        items.append({
            "title": r.get("title") or r.get("topic"),
            "grade": r.get("grade"),
            "unit": r.get("unit"),
            "date": r.get("date"),
            "source": r.get("source"),
            "url": r.get("rel_path"),
        })
    return json.dumps({"count": len(items), "items": items},
                      ensure_ascii=False, indent=1) + chr(10)

def main() -> int:
    output_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path("output").resolve()
    if not output_dir.is_dir():
        print(f"[ERR] output 디렉토리 없음: {output_dir}", file=sys.stderr)
        return 1
    rows = gather(output_dir)
    dups = detect_duplicates(rows)

    md = render_markdown(rows, output_dir)
    (output_dir / "INDEX.md").write_text(md, encoding="utf-8")

    html = render_html(rows, dups)
    (output_dir / "index.html").write_text(html, encoding="utf-8")

    (output_dir / "manifest.json").write_text(render_manifest(rows), encoding="utf-8")

    msg = f"[OK] INDEX.md + index.html + manifest.json ({len(rows)}개 자료"
    if dups:
        msg += f", ⚠️ 중복 {len(dups)}건"
    msg += ")"
    print(msg)
    if dups:
        print("\n중복 영상:", file=sys.stderr)
        for vid, group in dups.items():
            print(f"  - {vid}: {len(group)}개 파일", file=sys.stderr)
            for g in group:
                print(f"      {g['rel_path']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""갤러리 HTML 학습자료 → 옵시디언 수학 스텁 노트 백필.

기존 갤러리(output/**/*.html)의 각 학습자료에 대해, 옵시디언에 얇은 스텁 노트를 생성한다.
스텁 = frontmatter + 한 줄 요지 + 핵심 개념 위키링크 + HTML 학습자료 링크 (본체는 HTML).

실제 HTML에서 추출(지어내지 않음): 제목, 출처 유튜브 URL, video_id.
경로에서: 학년/단원. 파일명에서: 생성일. 제목에서: 개념 위키링크(best-effort).

사용법:
    python make_math_stubs.py [--force]   # --force: 기존 스텁 덮어쓰기

기본 동작: 이미 있는 스텁은 건너뜀(idempotent).
"""
import argparse
import re
import sys
import urllib.parse
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
OUTPUT = REPO / "output"
# 볼트 폴더의 숫자 접두사가 바뀌어도(020→010 등) 안 깨지게 glob 으로 해석
_VAULT_BASE = Path(r"G:\내 드라이브\00_Obsidian_Second Brain\Insight Miner\000-수집")
_vmatch = sorted(_VAULT_BASE.glob("*-Youtube-Obsi/수학영상노트"))
VAULT_STUB = _vmatch[0] if _vmatch else _VAULT_BASE / "010-Youtube-Obsi" / "수학영상노트"
PAGES_BASE = "https://irun20000-eng.github.io/youtube-math-skill/"

YT_RE = re.compile(r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\"'<> )]+")
VID_RE = re.compile(r"(?:v=|/live/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)


def _clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)            # 태그 제거
    return re.sub(r"\s+", " ", s).strip()


def extract_title(html: str) -> str:
    m = TITLE_RE.search(html)
    title = _clean(m.group(1)) if m else ""
    if "|" in title:                          # "제목 | 학습자료" → 제목
        title = title.split("|")[0].strip()
    if not title:
        m = H1_RE.search(html)
        title = _clean(m.group(1)) if m else ""
    return title


NON_CONCEPT = {
    "풀이", "유형", "정리", "완벽", "공식", "총정리", "마스터", "핵심", "비법",
    "꿀팁", "특강", "개념", "방법", "전략", "본질", "관점",
}


_PARTICLE = re.compile(r"(의|을|를|과|와|은|는|이|가|에|로|으로)$")


def _clean_concept(p: str) -> str:
    if " " in p:                              # 여러 단어면 첫 토큰
        p = p.split()[0]
    p = re.split(r"[(){}\[\]]", p)[0]         # 괄호 이후 제거 ("b)" 등)
    p = _PARTICLE.sub("", p.strip())          # 끝 조사 제거
    return p.strip()


def concepts_from_title(title: str) -> list[str]:
    head = re.split(r"[—–\-:|]", title)[0]    # 대시/콜론 앞부분
    out: list[str] = []
    for raw in re.split(r"[·/×+,、&]", head):
        p = _clean_concept(raw.strip())
        if (1 < len(p) <= 14 and re.search(r"[가-힣]", p)
                and p not in out and p not in NON_CONCEPT):
            out.append(p)
    return out


def yq(s: str) -> str:
    """YAML 큰따옴표 안전화."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_stub(html_path: Path) -> tuple[Path, str]:
    rel = html_path.relative_to(OUTPUT)          # 고1/단원/파일.html
    parts = rel.parts
    grade = parts[0]
    unit = parts[1] if len(parts) >= 3 else ""
    slug = html_path.stem
    m = re.match(r"(\d{4})(\d{2})(\d{2})", slug)
    yyyy, mm, dd = (m.group(1), m.group(2), m.group(3)) if m else ("0000", "00", "00")
    created = f"{yyyy}-{mm}-{dd}" if m else ""

    html = html_path.read_text(encoding="utf-8", errors="replace")
    title = extract_title(html) or slug
    url_m = YT_RE.search(html)
    url = url_m.group(0) if url_m else ""
    vid_m = VID_RE.search(url) if url else None
    vid = vid_m.group(1) if vid_m else ""
    concepts = concepts_from_title(title)

    # Pages URL — deploy-pages.yml이 output/를 Pages 루트로 발행하므로 output/ 제외
    rel_out = html_path.relative_to(OUTPUT).as_posix()
    html_url = PAGES_BASE + urllib.parse.quote(rel_out)

    related = ", ".join(f'"[[{c}]]"' for c in concepts)
    concept_line = " · ".join(f"[[{c}]]" for c in concepts) if concepts else "(보강 필요)"

    body = f"""---
type: youtube-math-stub
title: {yq(title)}
created: {created}
url: {url}
video_id: {vid}
channel: ""
published: ""
grade: {yq(grade)}
unit: {yq(unit)}
difficulty: ""
topics: [{yq(unit)}]
tags: [math]
related: [{related}]
html_url: {html_url}
oneliner: {yq(title)}
source: backfill
---

## 💎 한 줄 요지
{title}

## 💡 핵심 개념
- {concept_line}

## 🔗 학습자료
[인터랙티브 학습자료 열기]({html_url})

> 갤러리 백필로 자동 생성한 **스텁(index)** — 본체(수식·수준별 문항·풀이)는 HTML 학습자료에 있다.
> 한 줄 요지·개념은 제목 기반 초안이므로 필요 시 보강.
"""
    dest = VAULT_STUB / yyyy / mm / f"{slug}.md"
    return dest, body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="기존 스텁 덮어쓰기")
    args = ap.parse_args()

    htmls = sorted(p for p in OUTPUT.rglob("*.html") if p.name != "index.html")
    print(f"[OK] 갤러리 HTML {len(htmls)}개", file=sys.stderr)
    made = skipped = 0
    for h in htmls:
        dest, body = build_stub(h)
        if dest.exists() and not args.force:
            skipped += 1
            print(f"  - skip(존재): {dest.relative_to(VAULT_STUB)}", file=sys.stderr)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
        made += 1
        print(f"  + 생성: {dest.relative_to(VAULT_STUB)}", file=sys.stderr)
    print(f"[OK] 생성 {made} / 건너뜀 {skipped} / 총 {len(htmls)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

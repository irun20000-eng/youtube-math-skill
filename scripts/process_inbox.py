"""INBOX 라우터 백본 — Gemini 통합 Gem 기초자료(.md)를 읽어 타입을 판별하고
가공 작업 매니페스트(JSON)를 생성한다.

흐름에서의 위치:
    Gemini 통합 Gem → 기초자료 .md → 사용자가 INBOX에 저장
    → [이 스크립트] INBOX 스캔 → 타입 파싱 → 작업 매니페스트
    → (오케스트레이터가) 수학=HTML 갤러리+옵시디언 스텁 / 일반=옵시디언 풀노트

이 스크립트는 "파싱·라우팅"만 한다(결정적). 실제 생성·발행·파일 이동은 하지 않는다
(생성 후 이동해야 하므로). 출력 매니페스트를 오케스트레이터가 소비한다.

사용법:
    python process_inbox.py [--inbox "<INBOX 경로>"] [--json-only]

출력:
    stdout — 작업 매니페스트 JSON (list)
    stderr — 사람용 진단 요약

종료 코드:
    0 — 정상(처리할 작업 0건 포함)
    3 — INBOX 경로 없음
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Windows 콘솔(cp949) 등에서도 UTF-8로 출력(이모지·한글 깨짐/크래시 방지)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

VIDEO_ID_RE = re.compile(
    r"(?:v=|/live/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})"
)


def _field(text: str, key: str) -> str | None:
    """'키: 값' 한 줄에서 값 추출(콜론은 ':' 또는 전각 '：')."""
    m = re.search(rf"^\s*{re.escape(key)}\s*[:：]\s*(.+?)\s*$", text, re.MULTILINE)
    return m.group(1).strip() if m else None


def _section(text: str, header: str) -> str | None:
    """'## 헤더' 다음 ~ 다음 '##' 전까지의 본문."""
    m = re.search(
        rf"^#+\s*{re.escape(header)}[^\n]*\n(.*?)(?=^#+\s|\Z)",
        text, re.MULTILINE | re.DOTALL,
    )
    return m.group(1).strip() if m else None


def normalize_type(raw: str | None) -> str:
    """타입 문자열 → math | general | uncertain."""
    if not raw:
        return "uncertain"
    v = raw.strip()
    # 템플릿을 그대로 echo("일반지식 | 수학강의 | 불확실")한 경우 → 미선택
    if v.count("|") >= 1:
        return "uncertain"
    if "수학" in v:
        return "math"
    if "일반" in v:
        return "general"
    if "불확실" in v:
        return "uncertain"
    return "uncertain"


def _strip_code_fence(text: str) -> str:
    """출력이 통째로 ```...``` 코드블록에 싸여 들어온 경우 펜스를 제거."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("```"):
        del lines[i]
        for j in range(len(lines) - 1, -1, -1):
            if lines[j].strip().startswith("```"):
                del lines[j]
                break
    return "\n".join(lines)


def parse_report(path: Path) -> dict:
    text = _strip_code_fence(path.read_text(encoding="utf-8", errors="replace"))
    nonempty = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # 시청 불가 정직 실패 마커 (앞쪽 몇 줄 내)
    warn = next((ln for ln in nonempty[:3] if "시청 불가" in ln), None)
    if warn:
        return {
            "file": str(path), "name": path.name,
            "status": "unwatchable", "type": None,
            "reason": warn,
        }

    url = _field(text, "URL") or ""
    vid_m = VIDEO_ID_RE.search(url)
    rtype = normalize_type(_field(text, "타입"))

    job = {
        "file": str(path),
        "name": path.name,
        "status": "ready" if rtype != "uncertain" else "needs_review",
        "type": rtype,                       # math | general | uncertain
        "route": {
            "math": "html_gallery + obsidian_stub",
            "general": "obsidian_note",
            "uncertain": "_review",
        }[rtype],
        "title": _field(text, "제목"),
        "channel": _field(text, "채널"),
        "published": _field(text, "게시일"),
        "duration": _field(text, "영상 길이"),
        "url": url,
        "video_id": vid_m.group(1) if vid_m else None,
        "oneliner": _section(text, "한 줄 요지"),
    }
    if rtype == "math":
        job["grade_unit"] = _section(text, "추정 학년·단원")
    return job


def main() -> int:
    p = argparse.ArgumentParser(description="INBOX 기초자료 → 라우팅 매니페스트")
    p.add_argument("--inbox", default="INBOX", help="INBOX 폴더 경로")
    p.add_argument("--json-only", action="store_true",
                   help="stdout에 JSON만(진단 요약 생략)")
    args = p.parse_args()

    inbox = Path(args.inbox)
    if not inbox.is_dir():
        print(f"[ERR] INBOX 경로 없음: {inbox}", file=sys.stderr)
        return 3

    md_files = sorted(f for f in inbox.glob("*.md") if not f.name.startswith("_"))
    jobs = [parse_report(f) for f in md_files]

    if not args.json_only:
        n_math = sum(j["type"] == "math" for j in jobs)
        n_gen = sum(j["type"] == "general" for j in jobs)
        n_rev = sum(j["status"] in ("needs_review", "unwatchable") for j in jobs)
        print(f"[OK] INBOX: {inbox}", file=sys.stderr)
        print(f"[OK] {len(jobs)}건 — 수학 {n_math} / 일반 {n_gen} / 검토필요 {n_rev}",
              file=sys.stderr)
        for j in jobs:
            print(f"  - {j['name']}  →  [{j['type'] or j['status']}] {j['route'] if j.get('route') else j.get('reason','')}",
                  file=sys.stderr)

    print(json.dumps(jobs, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

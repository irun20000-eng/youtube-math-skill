"""INBOX 라우터 백본 (트랙 A, 스파크 기반, 2026-08-06 개편) — 구글 스파크(Spark) 요약본
(Google Docs, 제목만 .md)을 읽어 "수학 영상인가"를 판별하고 처리 매니페스트(JSON)를 만든다.

흐름에서의 위치:
    구글 스파크 → 요약 Google Docs(제목 {YYYY-MM-DD}_[카테고리]_{제목}.md)
       → 사용자/자동 파이프라인이 스파크 폴더에 저장
    → (오케스트레이터가) Drive MCP search_files 로 스파크 폴더 목록 + _done 폴더 목록 확보
       → _done/{video_id}.done 이 이미 있는 문서는 제외
       → 남은 문서를 Drive MCP read_file_content 로 읽어 로컬 스테이징 폴더에 평문 저장
    → [이 스크립트] 스테이징 폴더 스캔 → 타입 판별(수학 여부) → 처리 매니페스트
    → (오케스트레이터가) math 인 것만 youtube-math-lesson 스킬로 HTML 생성 + 후처리 + push
       + 옵시디언 스텁 + _done/{video_id}.done(pipeline: math) 마커 생성
    → math 가 아닌 것은 마커를 만들지 않고 그대로 skip
       (claude_work 리포의 routines/spark-reconstruct-curator.md 가 일반 노트로 처리하고
        자기 마커를 남긴다 — 두 파이프라인은 같은 _done 폴더를 공유하되 서로의 담당 영상엔 관여하지 않는다)

이 스크립트는 "파싱·분류"만 한다(결정적, Drive 접근 없음). 이 스크립트 자체는 MCP 도구를
호출할 수 없으므로 스파크 목록 조회·본문 읽기·완료 마커 생성은 오케스트레이터(에이전트)가
Drive MCP 도구로 직접 수행하고, 그 결과(평문 스테이징 폴더)만 이 스크립트에 넘긴다.

스파크 Google Docs 는 frontmatter 가 YAML `---` 펜스 없이 `-----` 구분선 + 모든 필드가
줄바꿈 없이 한 문단에 이어 붙는 형태로 변환되어 온다(예:
`type: youtube-insight title: "..." ... video_id: xxx channel: "..." ... topics: [a, b] tags: [c, d]`).
또한 이모지가 깨져 `ð` 등으로 나오는 경우가 있다(파싱에는 영향 없음, 무시).

사용법:
    python process_inbox.py [--inbox "<스테이징 폴더>"] [--skip-ids "<video_id 목록 파일>"] [--json-only]

출력:
    stdout — 처리 매니페스트 JSON (list)
    stderr — 사람용 진단 요약

종료 코드:
    0 — 정상(처리할 작업 0건 포함)
    3 — 스테이징 폴더 없음
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

# 수학 판별 2순위(휴리스틱) 키워드 — 제목([카테고리] 태그 포함)·채널·topics·tags 를 합친
# 문자열에서 하나라도 뚜렷이 매치하면 수학으로 판정한다.
MATH_KEYWORDS = [
    "수학", "미적분", "확률과통계", "기하", "대수", "함수", "방정식", "부등식",
    "수열", "극한", "미분", "적분", "벡터", "행렬", "삼각함수", "로그", "지수",
    "도형", "확률", "통계", "수능", "모의고사", "학력평가", "내신", "N제", "기출",
    "문제풀이",
]

# 공부법 판별(2026-09-04 신설) 키워드 — "분야: 수학강의"로 태그된 채널이라도
# 실제 내용이 수학 개념·문제풀이가 아니라 시험전략/시간관리/메타인지/오답분석 같은
# "공부법" 영상인 경우를 math 판정보다 먼저 걸러낸다. 이 신호가 잡히면 type="study_method"
# 로 라우팅해 별도 경량 템플릿(templates/study-method-skeleton.html)으로 처리한다 —
# 8~10문항 문제집을 억지로 만들지 않기 위함. classify_math()보다 먼저 실행한다.
STUDY_METHOD_KEYWORDS = [
    "공부법", "시간관리", "메타인지", "오답노트", "오답분석", "슬럼프", "멘탈관리",
    "학습전략", "시험전략", "실전전략", "자기주도학습", "공부습관", "9모분석",
    "수능전략",
]


def classify_study_method(text: str, filename: str) -> tuple[bool, str]:
    """(공부법 여부, 판정 근거) 반환. classify_math() 보다 먼저 호출해야 한다.

    스파크 파일명의 [카테고리] 태그(예: [수학][수학공부법])·title·topics·tags 를 합쳐
    STUDY_METHOD_KEYWORDS 매치 여부로 판정. 수학 개념 키워드(MATH_KEYWORDS)보다
    좁고 구체적인 신호만 모아뒀으므로, 매치되면 곧바로 공부법으로 확정한다.
    """
    title = _field(text, "title") or filename
    topics = _field(text, "topics") or ""
    tags = _field(text, "tags") or ""
    signal = " ".join([filename, title, topics, tags])
    hit = next((kw for kw in STUDY_METHOD_KEYWORDS if kw in signal), None)
    if hit:
        return True, f"공부법 키워드('{hit}')"
    return False, ""


def _field(text: str, key: str) -> str | None:
    """'키: 값' 을 텍스트에서 추출.

    스파크 문서는 줄바꿈 없이 한 문단에 필드가 이어 붙으므로(예:
    `title: "..." created: 2026-08-06`), 값의 형태별로 3단계로 시도한다:
      1) 따옴표로 감싼 값 — `key: "..."`
      2) 대괄호 리스트 — `key: [...]`
      3) 맨 값 — 다음 `무언가:` 토큰이나 줄바꿈 전까지 (구식 '한 줄에 필드 하나' 형식도 커버)
    콜론은 반각 ':' 또는 전각 '：' 모두 허용.
    """
    m = re.search(rf'{re.escape(key)}\s*[:：]\s*"([^"]*)"', text)
    if m:
        return m.group(1).strip()
    m = re.search(rf'{re.escape(key)}\s*[:：]\s*\[([^\]]*)\]', text)
    if m:
        return m.group(1).strip()
    m = re.search(
        rf'{re.escape(key)}\s*[:：]\s*(.+?)(?=\s+[A-Za-z_가-힣]+\s*[:：]|\n|$)',
        text,
    )
    return m.group(1).strip() if m else None


def _section(text: str, header: str) -> str | None:
    """'## 헤더' 다음 ~ 다음 '##' 전까지의 본문(구식 리포트 형식용, 스파크엔 없을 수 있음)."""
    m = re.search(
        rf"^#+\s*{re.escape(header)}[^\n]*\n(.*?)(?=^#+\s|\Z)",
        text, re.MULTILINE | re.DOTALL,
    )
    return m.group(1).strip() if m else None


def classify_math(text: str, filename: str) -> tuple[bool, str]:
    """(수학 여부, 판정 근거) 반환.

    1순위: 본문에 명시적 '타입:'/'분야:' 필드가 있고 값에 '수학'/'수학강의' 포함 → 확정 수학.
           (스파크 표준 템플릿엔 이 필드가 없다 — 옛 리포트 형식이 섞여 들어온 경우를 위한 폴백)
    2순위: 명시 필드가 없으면 제목(파일명의 [카테고리] 태그 포함)·채널·topics·tags 에서
           MATH_KEYWORDS 매치 여부로 판정.
    둘 다 아니면 수학 아님(이 레포의 담당이 아님 → skip).
    """
    explicit = _field(text, "타입") or _field(text, "분야")
    if explicit and ("수학" in explicit):
        return True, f"명시 필드('{explicit}')"

    title = _field(text, "title") or filename
    channel = _field(text, "channel") or ""
    topics = _field(text, "topics") or ""
    tags = _field(text, "tags") or ""
    signal = " ".join([filename, title, channel, topics, tags])
    hit = next((kw for kw in MATH_KEYWORDS if kw in signal), None)
    if hit:
        return True, f"키워드 휴리스틱('{hit}')"
    return False, "명시 필드 없음 + 키워드 매치 없음"


def _unescape_md(text: str) -> str:
    """Google Docs→마크다운 변환이 `_`·`[`·`]`·`*` 를 백슬래시로 이스케이프해
    `video\\_id`, `\\[math, calculus\\]` 처럼 보내는 것을 되돌린다.
    이걸 안 하면 키 이름(`video_id` 등)과 `[...]` 리스트 값이 전혀 매칭되지 않는다."""
    return re.sub(r'\\([_\[\]*])', r'\1', text)


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


def parse_report(path: Path, skip_ids: set[str]) -> dict:
    text = _unescape_md(_strip_code_fence(path.read_text(encoding="utf-8", errors="replace")))
    nonempty = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # 시청 불가 정직 실패 마커 (앞쪽 몇 줄 내, 구식 리포트 형식 폴백)
    warn = next((ln for ln in nonempty[:3] if "시청 불가" in ln), None)
    if warn:
        return {
            "file": str(path), "name": path.name,
            "status": "unwatchable", "type": None,
            "reason": warn,
        }

    url = _field(text, "url") or _field(text, "URL") or ""
    vid_field = _field(text, "video_id")
    vid_m = VIDEO_ID_RE.search(url)
    video_id = vid_field or (vid_m.group(1) if vid_m else None)

    if video_id and video_id in skip_ids:
        return {
            "file": str(path), "name": path.name,
            "status": "skip_done", "type": None,
            "video_id": video_id,
            "reason": "_done 마커 이미 존재 — 어느 파이프라인이든 처리 완료",
        }

    is_study, study_why = classify_study_method(text, path.name)
    is_math, math_why = (False, "") if is_study else classify_math(text, path.name)

    if is_study:
        content_type, why = "study_method", study_why
    elif is_math:
        content_type, why = "math", math_why
    else:
        content_type, why = "not_math", "명시 필드 없음 + 키워드 매치 없음"

    job = {
        "file": str(path),
        "name": path.name,
        "status": "ready" if content_type != "not_math" else "skip_not_math",
        "type": content_type,
        "reason": why,
        "route": {
            "math": "html_gallery + obsidian_stub",
            "study_method": "study_method_gallery + obsidian_stub",
            "not_math": "_skip(claude_work 담당)",
        }[content_type],
        "title": _field(text, "title") or _field(text, "제목"),
        "channel": _field(text, "channel") or _field(text, "채널"),
        "published": _field(text, "published") or _field(text, "게시일"),
        "duration_min": _field(text, "duration_min"),
        "url": url,
        "video_id": video_id,
        "topics": _field(text, "topics"),
        "tags": _field(text, "tags"),
        "oneliner": _field(text, "oneliner") or _section(text, "한 줄 요지"),
    }
    return job


def main() -> int:
    p = argparse.ArgumentParser(description="스파크 스테이징 폴더 → 수학 판별 매니페스트")
    p.add_argument("--inbox", default="INBOX_STAGE", help="스테이징 폴더 경로(평문 .md)")
    p.add_argument("--skip-ids", default=None,
                   help="이미 _done 마커가 있는 video_id 목록 파일(줄당 1개) — 2차 방어")
    p.add_argument("--json-only", action="store_true",
                   help="stdout에 JSON만(진단 요약 생략)")
    args = p.parse_args()

    inbox = Path(args.inbox)
    if not inbox.is_dir():
        print(f"[ERR] 스테이징 폴더 없음: {inbox}", file=sys.stderr)
        return 3

    skip_ids: set[str] = set()
    if args.skip_ids:
        sp = Path(args.skip_ids)
        if sp.is_file():
            skip_ids = {ln.strip() for ln in sp.read_text(encoding="utf-8").splitlines() if ln.strip()}

    md_files = sorted(f for f in inbox.glob("*.md") if not f.name.startswith("_"))
    jobs = [parse_report(f, skip_ids) for f in md_files]

    if not args.json_only:
        n_math = sum(j["type"] == "math" for j in jobs)
        n_study = sum(j["type"] == "study_method" for j in jobs)
        n_skip = sum(j["status"] == "skip_not_math" for j in jobs)
        n_done = sum(j["status"] == "skip_done" for j in jobs)
        n_unw = sum(j["status"] == "unwatchable" for j in jobs)
        print(f"[OK] 스테이징: {inbox}", file=sys.stderr)
        print(f"[OK] {len(jobs)}건 — 수학 {n_math} / 공부법 {n_study} / 비수학 skip {n_skip} / "
              f"이미완료 skip {n_done} / 시청불가 {n_unw}", file=sys.stderr)
        for j in jobs:
            print(f"  - {j['name']}  →  [{j['type'] or j['status']}] {j.get('reason','')}",
                  file=sys.stderr)

    print(json.dumps(jobs, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

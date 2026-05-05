"""학습자료 출력 경로 명명 규칙.

규칙:
    output/{학년}/{단원}/{YYYYMMDD}_{핵심주제}_{video_id8}.html

예시:
    output/고1/수학Ⅰ-삼각함수의활용/20260505_사인법칙코사인법칙_W9ReLryy.html

Windows 금지문자(\\ / : * ? " < > |)는 자동으로 제거 또는 치환된다.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

WIN_FORBIDDEN = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
WHITESPACE = re.compile(r"\s+")
PUNCT_TO_STRIP = re.compile(r"[·,.()\[\]{}!@#$%^&+=`~]")

VALID_GRADES = {"중1", "중2", "중3", "고1", "고2", "고3"}

VIDEO_ID_FROM_URL = re.compile(
    r"(?:v=|/live/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})"
)


def sanitize(text: str, max_len: int | None = None) -> str:
    """파일/디렉토리 이름으로 안전한 형태로 정제.

    - Windows 금지문자 제거
    - 점/쉼표/괄호/구두점 제거
    - 공백을 단일 _ 로 변경 후 _ 제거 (한글이 붙는 게 가독성 좋음)
    - 양 끝의 _ . 제거
    - max_len 지정 시 그래프emes 단위가 아니라 그냥 글자수로 잘라냄
    """
    s = WIN_FORBIDDEN.sub("", text)
    s = PUNCT_TO_STRIP.sub("", s)
    s = WHITESPACE.sub("", s)
    s = s.strip("._-")
    if max_len and len(s) > max_len:
        s = s[:max_len].rstrip("._-")
    return s or "untitled"


def normalize_grade(grade: str) -> str:
    """'고등학교 1학년', '고1', '고1수학' 등을 '고1'로 정규화. 알 수 없으면 '미분류'."""
    g = grade.strip()
    for canonical in VALID_GRADES:
        if canonical in g:
            return canonical
    return "미분류"


def normalize_unit(unit: str) -> str:
    """단원명을 정규화. 예: '[고1-수학Ⅰ-삼각함수의 활용]' → '수학Ⅰ-삼각함수의활용'.

    - 대괄호/꺾쇠 제거
    - 학년 코드("고1-", "중3-" 등)가 앞에 붙어 있으면 제거
    - 코드/공백 정제
    - 30자 제한
    """
    s = unit.strip()
    s = re.sub(r"^\[|\]$", "", s).strip()
    s = re.sub(r"^(중\d|고\d)-", "", s).strip()
    return sanitize(s, max_len=30)


def short_video_id(video_id: str, n: int = 8) -> str:
    """video_id 앞 n자만 사용 (충돌 방지에 충분, 파일명 단축)."""
    return video_id[:n]


def build_output_path(
    base_dir: Path | str,
    grade: str,
    unit: str,
    topic: str,
    video_id: str,
    when: date | None = None,
) -> Path:
    """규약에 맞는 절대 경로를 반환.

    Args:
        base_dir: 기준 디렉토리 (예: 작업디렉토리/output)
        grade: 학년 ("고1" 등)
        unit: 단원명 (정규화 전 원문 가능)
        topic: 핵심 주제 (영상의 핵심 1~2개 개념)
        video_id: YouTube video ID (11자)
        when: 생성 일자 (기본: 오늘)

    Returns:
        예: Path("output/고1/수학Ⅰ-삼각함수의활용/20260505_사인법칙코사인법칙_W9ReLryy.html")
    """
    base = Path(base_dir)
    when = when or date.today()
    g = normalize_grade(grade)
    u = normalize_unit(unit)
    t = sanitize(topic, max_len=24)
    vid = short_video_id(video_id)
    fname = f"{when:%Y%m%d}_{t}_{vid}.html"
    return base / g / u / fname


def parse_output_path(path: Path | str) -> dict | None:
    """build_output_path의 역과정. 파일명 패턴이 안 맞으면 None."""
    p = Path(path)
    parts = p.parts
    fname_match = re.match(
        r"^(\d{8})_(.+)_([A-Za-z0-9_-]{6,11})\.html$", p.name
    )
    if not fname_match or len(parts) < 3:
        return None
    return {
        "date": fname_match.group(1),
        "topic": fname_match.group(2),
        "video_id_short": fname_match.group(3),
        "unit": parts[-2],
        "grade": parts[-3],
        "filename": p.name,
    }


def extract_video_id_from_url(url: str) -> str | None:
    """URL에서 11자 video_id를 추출. 실패 시 None."""
    m = VIDEO_ID_FROM_URL.search(url)
    return m.group(1) if m else None


def find_existing(base_dir: Path | str, video_id: str) -> list[Path]:
    """base_dir 하위에서 같은 video_id(앞 8자 매칭)를 가진 기존 .html 파일을 모두 반환.

    중복 영상을 다시 처리하기 전에 호출해 사용자에게 알린다.
    같은 영상이라도 날짜·주제가 다르면 별도 파일로 존재 가능 (수정본 등).
    """
    base = Path(base_dir)
    if not base.is_dir():
        return []
    short = short_video_id(video_id)
    matches = []
    for html in base.rglob("*.html"):
        if html.name == "index.html":
            continue
        parsed = parse_output_path(html.relative_to(base))
        if parsed and parsed["video_id_short"] == short:
            matches.append(html)
    return matches


if __name__ == "__main__":
    # 자체 테스트
    out = build_output_path(
        base_dir="output",
        grade="고1",
        unit="[고1-수학Ⅰ-삼각함수의 활용]",
        topic="사인법칙·코사인법칙",
        video_id="W9ReLryydQg",
        when=date(2026, 5, 5),
    )
    print(f"build: {out}")
    parsed = parse_output_path(out)
    print(f"parse: {parsed}")
    assert parsed is not None
    assert parsed["grade"] == "고1"
    assert parsed["unit"] == "수학Ⅰ-삼각함수의활용"
    assert parsed["date"] == "20260505"
    assert parsed["video_id_short"] == "W9ReLryy"

    # URL에서 video_id 추출
    cases = [
        "https://www.youtube.com/watch?v=W9ReLryydQg",
        "https://www.youtube.com/live/W9ReLryydQg?si=abc",
        "https://youtu.be/W9ReLryydQg",
        "https://www.youtube.com/shorts/W9ReLryydQg",
    ]
    for url in cases:
        assert extract_video_id_from_url(url) == "W9ReLryydQg", url
    print("OK")

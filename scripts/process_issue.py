"""GitHub Issue body를 파싱해 학습자료 HTML을 정확한 경로에 저장.

GitHub Issue Forms 형식의 body에서 학년/단원/주제/영상ID/HTML을 추출하고,
youtube-math-auto/scripts/output_path.py 의 명명 규칙으로 경로를 빌드한다.

환경 변수:
    ISSUE_BODY: Issue 본문 텍스트 (GitHub Actions에서 주입)
    GITHUB_OUTPUT: GitHub Actions output 파일 경로 (선택)

종료 코드:
    0 — 성공
    1 — ISSUE_BODY 없음
    2 — 필드 누락
    3 — HTML 코드 블록 없음
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# youtube-math-auto/scripts 의 명명 규칙 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent / "youtube-math-auto" / "scripts"))
from output_path import build_output_path


def extract_field(body: str, label: str) -> str:
    """### {label} 다음 줄부터 다음 ### 또는 끝까지의 내용을 반환."""
    pattern = rf'###\s*{re.escape(label)}\s*\n+(.+?)(?=\n###\s|\Z)'
    m = re.search(pattern, body, re.DOTALL)
    if not m:
        raise ValueError(f"필드 '{label}' 을 찾을 수 없습니다")
    return m.group(1).strip()


def extract_html(field_value: str) -> str:
    """필드 값 안에서 HTML 코드 블록을 추출. 코드 블록이 없으면 전체를 반환."""
    # ```html\n...\n``` 또는 ```\n<!DOCTYPE...\n```
    m = re.search(r'```(?:html)?\s*\n(.*?)\n```', field_value, re.DOTALL)
    if m:
        return m.group(1).strip()
    return field_value.strip()


def main() -> int:
    body = os.environ.get("ISSUE_BODY", "").strip()
    if not body:
        print("[ERR] ISSUE_BODY 환경변수가 비어있음", file=sys.stderr)
        return 1

    try:
        grade = extract_field(body, "학년")
        unit = extract_field(body, "단원")
        topic = extract_field(body, "핵심 주제")
        video_id = extract_field(body, "영상 ID (YouTube)")
        html_field = extract_field(body, "HTML 코드")
    except ValueError as e:
        print(f"[ERR] {e}", file=sys.stderr)
        print(f"\n전체 body:\n{body[:500]}...", file=sys.stderr)
        return 2

    # video_id 정제 (URL이 통째로 들어왔을 가능성 처리)
    vid_match = re.search(r"([A-Za-z0-9_-]{11})", video_id)
    if vid_match:
        video_id = vid_match.group(1)

    html = extract_html(html_field)
    if not html.startswith("<!DOCTYPE") and "<html" not in html[:200].lower():
        print("[ERR] HTML 코드가 유효한 HTML 문서가 아닌 것 같음", file=sys.stderr)
        print(f"앞 200자: {html[:200]}", file=sys.stderr)
        return 3

    # 출력 경로 빌드
    out_path = build_output_path(
        base_dir="output",
        grade=grade,
        unit=unit,
        topic=topic,
        video_id=video_id,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print(f"[OK] 저장: {out_path}")
    print(f"  학년={grade}, 단원={unit}, 주제={topic}, ID={video_id}")
    print(f"  크기: {len(html):,}자")

    # GitHub Actions output 변수 설정
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"path={out_path.as_posix()}\n")
            f.write(f"filename={out_path.name}\n")
            f.write(f"grade={grade}\n")
            f.write(f"unit={unit}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

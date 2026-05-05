"""유튜브 URL → 한국어 자막 평문 추출 (yt-dlp + VTT 정제 통합).

사용법:
    python fetch_subtitle.py "<YouTube URL>" [--out subs] [--lang ko]

출력 (stdout):
    마지막 줄에 정제된 .txt 파일 절대 경로

진단 (stderr):
    각 단계 진행 메시지

종료 코드:
    0 — 성공
    2 — yt-dlp 미설치
    3 — 영상 ID 추출 실패 (URL 잘못됨)
    4 — 자막 트랙 없음 (사용자 요약 입력 필요)
    5 — yt-dlp 다운로드 실패 (네트워크/차단 등)
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from vtt_to_text import parse_cues, dedupe_sliding, to_timestamped_text


VIDEO_ID_RE = re.compile(
    r"(?:v=|/live/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})"
)
DEFAULT_LANG_GROUPS = (
    ("ko", "ko-KR", "ko-orig"),
    ("en", "en-US", "en-GB"),
)


def extract_video_id(url: str) -> str:
    m = VIDEO_ID_RE.search(url)
    if not m:
        raise ValueError(f"YouTube video ID를 찾을 수 없습니다: {url}")
    return m.group(1)


def check_yt_dlp() -> str:
    try:
        r = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, check=True,
        )
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError(
            "yt-dlp가 설치되어 있지 않습니다. 다음 명령으로 설치하세요:\n"
            "  pip install yt-dlp"
        ) from e


def _try_group(url: str, out_dir: Path, video_id: str, group: tuple[str, ...]) -> tuple[Path, str] | None:
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--write-sub", "--write-auto-sub",
        "--sub-lang", ",".join(group),
        "--sub-format", "vtt",
        "--skip-download",
        "--no-warnings",
        "-o", str(out_dir / "%(id)s.%(ext)s"),
        url,
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    for lang in group:
        candidate = out_dir / f"{video_id}.{lang}.vtt"
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate, lang
    return None


def download_subtitle(url: str, out_dir: Path,
                      lang_groups=DEFAULT_LANG_GROUPS) -> tuple[Path, str]:
    """단계적으로 언어 그룹을 시도. yt-dlp exit code는 무시하고 .vtt 존재로 판단.

    YouTube가 일부 언어 트랙에서 429를 던져도, 다른 언어가 받아졌으면 성공.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    video_id = extract_video_id(url)

    for group in lang_groups:
        result = _try_group(url, out_dir, video_id, group)
        if result is not None:
            return result

    raise FileNotFoundError(
        f"자막 트랙을 찾을 수 없습니다 (수동·자동, ko/en 모두 없음): {video_id}"
    )


def vtt_to_clean_text(vtt_path: Path) -> tuple[Path, dict]:
    cues = parse_cues(vtt_path)
    deduped = dedupe_sliding(cues)
    text = to_timestamped_text(deduped)
    txt_path = vtt_path.with_suffix(".txt")
    txt_path.write_text(text, encoding="utf-8")
    stats = {
        "raw_cues": len(cues),
        "deduped_cues": len(deduped),
        "chars": len(text),
    }
    return txt_path, stats


def main() -> int:
    p = argparse.ArgumentParser(description="YouTube URL → 한국어 자막 평문 추출")
    p.add_argument("url", help="YouTube 영상 URL")
    p.add_argument("--out", default="subs", help="자막 저장 디렉토리 (기본: subs)")
    p.add_argument("--lang", default=None,
                   help="우선 언어 그룹 (콤마 구분, 기본: ko,ko-KR,ko-orig 후 폴백 en,en-US,en-GB)")
    args = p.parse_args()

    try:
        version = check_yt_dlp()
        print(f"[OK] yt-dlp {version}", file=sys.stderr)
    except RuntimeError as e:
        print(f"[ERR] {e}", file=sys.stderr)
        return 2

    try:
        video_id = extract_video_id(args.url)
        print(f"[OK] video_id: {video_id}", file=sys.stderr)
    except ValueError as e:
        print(f"[ERR] {e}", file=sys.stderr)
        return 3

    out_dir = Path(args.out).resolve()
    if args.lang:
        lang_groups = (tuple(args.lang.split(",")),)
    else:
        lang_groups = DEFAULT_LANG_GROUPS

    try:
        vtt_path, lang_used = download_subtitle(args.url, out_dir, lang_groups)
        print(f"[OK] 자막 다운로드: {vtt_path.name} ({lang_used})", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"[NO_SUBS] {e}", file=sys.stderr)
        return 4
    except RuntimeError as e:
        print(f"[ERR] {e}", file=sys.stderr)
        return 5

    txt_path, stats = vtt_to_clean_text(vtt_path)
    print(
        f"[OK] 정제 완료: cues {stats['raw_cues']} → {stats['deduped_cues']}, "
        f"{stats['chars']}자",
        file=sys.stderr,
    )
    print(str(txt_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

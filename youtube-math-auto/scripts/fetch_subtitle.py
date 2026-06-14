"""유튜브 URL → 한국어 자막 평문 추출 (innertube/timedtext 우선 + yt-dlp 폴백 + VTT 정제).

사용법:
    python fetch_subtitle.py "<YouTube URL>" [--out subs] [--lang ko]

출력 (stdout):
    마지막 줄에 정제된 .txt 파일 절대 경로

진단 (stderr):
    각 단계 진행 메시지

종료 코드:
    0 — 성공
    2 — (사용 안 함; yt-dlp는 이제 선택적 폴백)
    3 — 영상 ID 추출 실패 (URL 잘못됨)
    4 — 자막 트랙 없음 (사용자 요약 입력 필요)
    5 — 모든 자막 경로 실패 (네트워크/차단 등)

설계 메모:
    yt-dlp의 자막 스크래핑은 YouTube 서명/봇탐지 변화에 자주 깨진다(특히 폰/클라우드).
    그래서 1순위로 watch 페이지의 ytInitialPlayerResponse / youtubei player API에서
    captionTracks(timedtext baseUrl)를 직접 받아 처리한다. 이 경로는 yt-dlp 없이도 동작하며
    거주지(residential) IP에서 적중률이 더 높은 경우가 많다. 실패 시에만 yt-dlp로 폴백한다.
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
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
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
# 공개적으로 알려진 WEB innertube 키 (없으면 watch 페이지 경로가 폴백).
_INNERTUBE_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
_PLAYER_RE = re.compile(r"ytInitialPlayerResponse\s*=\s*({.+?})\s*;", re.DOTALL)


def extract_video_id(url: str) -> str:
    m = VIDEO_ID_RE.search(url)
    if not m:
        raise ValueError(f"YouTube video ID를 찾을 수 없습니다: {url}")
    return m.group(1)


def yt_dlp_version() -> str | None:
    """yt-dlp가 있으면 버전, 없으면 None (더 이상 필수 아님)."""
    try:
        r = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, check=True,
        )
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


# ---------------------------------------------------------------------------
# 1순위: innertube / timedtext (yt-dlp 불필요)
# ---------------------------------------------------------------------------
def _http_get(url: str, timeout: int = 15) -> bytes | None:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": _UA,
            "Accept-Language": "ko,en;q=0.8",
            # EU 동의 쿠키 우회 (없으면 consent 페이지로 리다이렉트되는 경우)
            "Cookie": "CONSENT=YES+1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None


def _player_via_watch_page(video_id: str) -> dict | None:
    raw = _http_get(f"https://www.youtube.com/watch?v={video_id}&hl=ko&gl=KR")
    if not raw:
        return None
    m = _PLAYER_RE.search(raw.decode("utf-8", "replace"))
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def _player_via_innertube(video_id: str) -> dict | None:
    body = json.dumps({
        "context": {"client": {
            "clientName": "WEB", "clientVersion": "2.20240101.00.00",
            "hl": "ko", "gl": "KR",
        }},
        "videoId": video_id,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://www.youtube.com/youtubei/v1/player?key={_INNERTUBE_KEY}",
        data=body,
        headers={"User-Agent": _UA, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, urllib.error.HTTPError,
            TimeoutError, json.JSONDecodeError):
        return None


def _pick_caption_track(player: dict, lang_groups) -> tuple[str, str] | None:
    """captionTracks에서 (baseUrl, lang) 선택. 그룹 순서 우선, 수동자막>자동자막."""
    try:
        tracks = (player["captions"]
                  ["playerCaptionsTracklistRenderer"]["captionTracks"])
    except (KeyError, TypeError):
        return None
    if not tracks:
        return None
    for group in lang_groups:
        for prefer_manual in (True, False):
            for lang in group:
                for t in tracks:
                    code = t.get("languageCode", "")
                    is_asr = t.get("kind") == "asr"
                    if code == lang and (prefer_manual != is_asr) and t.get("baseUrl"):
                        return t["baseUrl"], code
    # 그룹과 정확히 안 맞아도 첫 트랙이라도 (예: ko-* 변형)
    for group in lang_groups:
        head = group[0].split("-")[0]
        for t in tracks:
            if t.get("languageCode", "").startswith(head) and t.get("baseUrl"):
                return t["baseUrl"], t["languageCode"]
    return None


def _timedtext_to_vtt(base_url: str, out_path: Path) -> bool:
    raw = _http_get(base_url + "&fmt=json3")
    if not raw:
        return False
    try:
        data = json.loads(raw.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return False
    events = data.get("events") or []
    lines = ["WEBVTT", ""]
    wrote = 0
    for ev in events:
        segs = ev.get("segs")
        if not segs:
            continue
        text = "".join(s.get("utf8", "") for s in segs).strip()
        if not text:
            continue
        start = int(ev.get("tStartMs", 0))
        end = start + int(ev.get("dDurationMs", 0) or 0)
        lines.append(f"{_ms_to_ts(start)} --> {_ms_to_ts(end)}")
        lines.append(text)
        lines.append("")
        wrote += 1
    if wrote == 0:
        return False
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return True


def _ms_to_ts(ms: int) -> str:
    s, ms = divmod(max(ms, 0), 1000)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def download_subtitle_innertube(out_dir: Path, video_id: str,
                                lang_groups) -> tuple[Path, str] | None:
    for fetch in (_player_via_watch_page, _player_via_innertube):
        player = fetch(video_id)
        if not player:
            continue
        picked = _pick_caption_track(player, lang_groups)
        if not picked:
            continue
        base_url, lang = picked
        vtt_path = out_dir / f"{video_id}.{lang}.vtt"
        if _timedtext_to_vtt(base_url, vtt_path):
            return vtt_path, lang
    return None


# ---------------------------------------------------------------------------
# 2순위(폴백): yt-dlp
# ---------------------------------------------------------------------------
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
    """1순위 innertube/timedtext → 2순위 yt-dlp. .vtt 존재로 성공 판단."""
    out_dir.mkdir(parents=True, exist_ok=True)
    video_id = extract_video_id(url)

    # 1순위: innertube (yt-dlp 불필요, 거주지 IP 친화)
    result = download_subtitle_innertube(out_dir, video_id, lang_groups)
    if result is not None:
        print("[OK] 자막 경로: innertube/timedtext", file=sys.stderr)
        return result

    # 2순위: yt-dlp (있을 때만)
    if yt_dlp_version() is not None:
        print("[..] innertube 실패 → yt-dlp 폴백", file=sys.stderr)
        for group in lang_groups:
            result = _try_group(url, out_dir, video_id, group)
            if result is not None:
                print("[OK] 자막 경로: yt-dlp", file=sys.stderr)
                return result

    raise FileNotFoundError(
        f"자막 트랙을 찾을 수 없습니다 (innertube·yt-dlp 모두 실패): {video_id}"
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

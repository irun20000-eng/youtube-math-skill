"""VTT (YouTube auto-caption) → 평문 변환.

YouTube 자동자막은 슬라이딩 윈도우 형태로 동일 문구가 반복된다.
중간 큐(이미 표시된 텍스트)는 버리고 새로 추가된 토큰만 살린다.
"""
import re
import sys
from pathlib import Path

TIME_RE = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*$")
TAG_RE = re.compile(r"<\d{2}:\d{2}:\d{2}\.\d{3}>|</?c[^>]*>")


def parse_cues(vtt_path: Path) -> list[tuple[float, str]]:
    cues: list[tuple[float, str]] = []
    current_start: float | None = None
    current_lines: list[str] = []

    def flush():
        nonlocal current_start, current_lines
        if current_start is not None and current_lines:
            text = " ".join(line.strip() for line in current_lines if line.strip())
            text = TAG_RE.sub("", text).strip()
            if text:
                cues.append((current_start, text))
        current_start = None
        current_lines = []

    for raw in vtt_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        m = TIME_RE.match(line)
        if m:
            flush()
            h, mn, s = line.split(" --> ")[0].split(":")
            current_start = int(h) * 3600 + int(mn) * 60 + float(s)
            continue
        if not line:
            flush()
            continue
        current_lines.append(line)
    flush()
    return cues


def dedupe_sliding(cues: list[tuple[float, str]]) -> list[tuple[float, str]]:
    """인접 큐의 공통 prefix를 제거하여 새로 추가된 부분만 남긴다."""
    out: list[tuple[float, str]] = []
    prev_text = ""
    for start, text in cues:
        if text == prev_text:
            continue
        if prev_text and text.startswith(prev_text):
            new_part = text[len(prev_text):].strip()
            if new_part:
                out.append((start, new_part))
            prev_text = text
            continue
        if prev_text:
            prev_tokens = prev_text.split()
            cur_tokens = text.split()
            overlap = 0
            max_check = min(len(prev_tokens), len(cur_tokens))
            for i in range(max_check, 0, -1):
                if prev_tokens[-i:] == cur_tokens[:i]:
                    overlap = i
                    break
            new_part = " ".join(cur_tokens[overlap:]).strip()
            if new_part:
                out.append((start, new_part))
        else:
            out.append((start, text))
        prev_text = text
    return out


def to_timestamped_text(cues: list[tuple[float, str]]) -> str:
    lines: list[str] = []
    last_stamp = -60
    buf: list[str] = []
    for start, text in cues:
        if start - last_stamp >= 30 and buf:
            lines.append(" ".join(buf))
            buf = []
        if not buf:
            mm = int(start // 60)
            ss = int(start % 60)
            lines.append(f"\n[{mm:02d}:{ss:02d}]")
            last_stamp = start
        buf.append(text)
    if buf:
        lines.append(" ".join(buf))
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python vtt_to_text.py <input.vtt> [output.txt]", file=sys.stderr)
        return 1
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".txt")
    cues = parse_cues(src)
    deduped = dedupe_sliding(cues)
    out = to_timestamped_text(deduped)
    dst.write_text(out, encoding="utf-8")
    print(f"OK: {src.name} -> {dst.name}")
    print(f"  cues: {len(cues)} -> {len(deduped)}")
    print(f"  chars: {len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

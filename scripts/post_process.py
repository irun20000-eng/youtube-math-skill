"""학습자료 생성 후 후처리 체인 단일 진입점.

새 .html 자료를 output/ 에 만든 뒤 이거 하나만 호출하면 5단계가 순서대로 돈다.
한 단계 빠뜨려서 옵시디언 동기화가 silent 하게 누락되던 사고(2026-06-16)를 막기 위함.

체인 순서 (모두 idempotent):
    1. add_back_button.py         갤러리 복귀 버튼
    2. add_related.py             관련 자료 카드
    3. make_math_stubs.py         옵시디언 스텁 (★ 자주 빠뜨리던 단계)
    4. regen_index.py             갤러리 index 재생성
    5. patch_pdf_mode.py          PDF 인쇄 모드

make_math_stubs 는 볼트가 없는 샌드박스에서 자동 dry-run 으로 떨어지므로
G:\ 폴더 오염 없이 "다음 09:00 루틴에 어디로 생성될지" 만 리포트한다.

사용법:
    python scripts/post_process.py [output_dir]   # 기본 output/
"""
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
AUTO = REPO / "youtube-math-auto" / "scripts"


def run(label: str, argv: list[str]) -> tuple[bool, str]:
    """스크립트 1개 실행. (성공여부, 마지막 [OK]/요약 줄) 반환."""
    print(f"\n=== {label} ===", file=sys.stderr)
    proc = subprocess.run(argv, cwd=str(REPO), capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    sys.stderr.write(out)
    ok = proc.returncode == 0
    # 요약 한 줄 뽑기 ([OK] 로 시작하는 마지막 줄)
    summary = ""
    for line in out.splitlines():
        if line.strip().startswith("[OK]") or "예정" in line and line.strip().startswith("[OK]"):
            summary = line.strip()
    return ok, summary


def main() -> int:
    out_dir = sys.argv[1] if len(sys.argv) > 1 else str(REPO / "output")
    py = sys.executable

    steps = [
        ("① 갤러리 복귀 버튼", [py, str(SCRIPTS / "add_back_button.py")]),
        ("② 관련 자료 카드", [py, str(SCRIPTS / "add_related.py")]),
        ("③ 옵시디언 스텁", [py, str(SCRIPTS / "make_math_stubs.py")]),
        ("④ 갤러리 index 재생성", [py, str(AUTO / "regen_index.py"), out_dir]),
        ("⑤ PDF 인쇄 모드", [py, str(AUTO / "patch_pdf_mode.py"), out_dir]),
    ]

    results: list[tuple[str, bool, str]] = []
    for label, argv in steps:
        ok, summary = run(label, argv)
        results.append((label, ok, summary))

    print("\n" + "=" * 56, file=sys.stderr)
    print("후처리 체인 결과 요약", file=sys.stderr)
    print("=" * 56, file=sys.stderr)
    all_ok = True
    for label, ok, summary in results:
        mark = "✅" if ok else "❌"
        all_ok = all_ok and ok
        print(f"{mark} {label:22} {summary}", file=sys.stderr)
    print("=" * 56, file=sys.stderr)
    if all_ok:
        print("✅ 전 단계 성공. git push → PR 머지 시 갤러리 갱신.", file=sys.stderr)
        print("   옵시디언 스텁은 위 ③ 'DRY-RUN 예정' 경로로 "
              "다음 09:00 사용자 PC 루틴에서 실제 생성.", file=sys.stderr)
    else:
        print("❌ 실패 단계 있음. 위 로그 확인 후 재실행.", file=sys.stderr)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

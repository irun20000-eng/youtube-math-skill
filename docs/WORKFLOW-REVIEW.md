# 워크플로우 리뷰 & 보강안 (2026-06-16)

옵시디언 개념 스텁이 며칠간 silent 하게 누락된 사고를 계기로, 전체 파이프라인을
진단하고 보강안을 정리한다. 이 문서는 "왜 이렇게 하는지"의 단일 참조점.

## 1. 전체 워크플로우

```
[입력]
  (a) STAGE 1 보고서 (영상 자막+요약)
  (b) 구글드라이브 INBOX  → process_inbox.py 가 매일 09:00 KST 처리
  (c) 자연어 개념 요청     → Claude 세션에서 즉시 생성

[생성]  박PM 5단계 / 하이브리드 표준
  templates/lesson-hybrid-skeleton.html 베이스
  → output/{학년}/{단원}/{YYYYMMDD}_{주제}_{video_id8}.html   (영상)
     output/{학년}/{단원}/{YYYYMMDD}_{주제}_개념.html          (개념)

[후처리 체인]  ★ scripts/post_process.py 하나로 5단계 일괄 (모두 idempotent)
  ① add_back_button.py        갤러리 복귀 버튼
  ② add_related.py            관련 자료 카드
  ③ make_math_stubs.py        옵시디언 스텁  ← 과거 자주 누락
  ④ regen_index.py            갤러리 index 재생성
  ⑤ patch_pdf_mode.py         PDF 인쇄 모드

[배포]
  git push → MCP PR 생성 → rebase merge → deploy-pages → 갤러리 URL
  옵시디언 실제 .md 생성 = 사용자 PC(Windows) 일일 09:00 루틴
```

## 2. 영상 자료 vs 개념 자료 차이

| 항목 | 영상 자료 | 개념 자료 |
|------|-----------|-----------|
| 파일명 | `..._{video_id8}.html` | `..._개념.html` |
| hero | 영상 썸네일/링크 | `src-badge` + 보라 그라데이션 |
| 갤러리 | 일반 카드 | `data-source="concept"` |
| 옵시디언 라우팅 | `수학영상노트/{YYYY}/{MM}/` | `수학개념노트/{YYYY}/{MM}/` |
| 스텁 frontmatter | `type: youtube-math-stub` | `type: math-concept-stub` |

## 3. 발견된 약점 & 조치 상태

| # | 약점 | 영향 | 조치 |
|---|------|------|------|
| ① | `make_math_stubs.py` 누락이 **silent failure** (갤러리는 정상이라 며칠 후 발견) | 🔴 | ✅ `post_process.py` 통합 진입점으로 단계 누락 차단 |
| ② | 샌드박스에서 옵시디언 실파일 검증 불가 | 🟠 | ✅ dry-run 리포트로 "생성 예정 경로" 명시 |
| ③ | `_개념` 라우팅 누락이 코드만 보면 안 보임 (커밋 메시지와 실제 코드 불일치) | 🟠 | ✅ PR #28 라우팅 구현 + 본 문서로 명문화 |
| ④ | 자연어 개념 요청 워크플로우 미문서화 | 🟡 | ✅ CLAUDE.md 섹션 추가 |
| ⑤ | 후처리 체인이 사람 손에 의존 (한 단계 빠뜨려도 push 됨) | 🟠 | ✅ `post_process.py` 일괄 + 결과 요약표 |

## 4. 핵심 안전장치 (이번 도입)

### `scripts/post_process.py`
- 자료 생성 후 **이거 하나만** 호출하면 5단계가 순서대로 돈다.
- 끝에 ✅/❌ 요약표 출력 → 어느 단계가 돌았는지 한눈에.
- 단계 누락으로 인한 옵시디언 silent failure 재발 차단.

### `make_math_stubs.py --dry-run` (+ 비Windows 자동 dry-run)
- 옵시디언 볼트는 Windows 전용 경로(`G:\...`). **비Windows(샌드박스/CI)에선 자동 dry-run**.
- 샌드박스에 가짜 `G:\` 폴더가 생기던 오염 차단 (`os.name != "nt"` 기준).
- dry-run 은 실제 파일을 안 쓰고 "어디에 생성될 예정인지"만 출력 → 사용자가 다음날 그 경로로 검증.

## 5. 미적용 / 향후 (확장성)

- **D. PR template 체크리스트** — 후처리 5단계 체크박스 강제 (자기검증)
- **E. CI 검증 워크플로우** — 새 HTML PR 에 `--dry-run` 결과를 코멘트로 자동 게시
- **F. INBOX 통합** — 자연어 요청도 INBOX 텍스트로 떨어뜨려 단일 파이프라인
- **G. 옵시디언 동기화 요약 노트** — 일일 루틴 후 "오늘 N개 동기화/실패 0" 노트 자동 생성

## 6. 사용자 검증 포인트

1. **갤러리**: https://irun20000-eng.github.io/youtube-math-skill/ (push 1~2분 후, Ctrl+Shift+R)
2. **옵시디언**: 다음 09:00 루틴 후 `수학개념노트/{YYYY}/{MM}/` 에 `_개념.md` 생성 확인.
   - 안 보이면 → 루틴이 옛 스크립트 캐싱했거나 git pull 실패. 이 둘이 거의 유일한 실패 경로.

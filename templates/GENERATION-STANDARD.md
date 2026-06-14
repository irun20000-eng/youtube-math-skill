# 학습자료 생성 표준 (하이브리드, 2026-06-14)

신규 수학 학습자료는 **하이브리드 표준**(`templates/lesson-hybrid-skeleton.html`)으로 생성한다.
정본 구현 예시: `output/고3/미적분-여러가지미분법/20260614_다변수실제변수연쇄법칙_10NhvK7s.html`.

## 전체 파이프라인

```
유튜브 영상 → Gemini 통합 Gem(영상 시청) → 기초자료 .md
   → G:\내 드라이브\Claude_Project\INBOX 에 저장
   → process_inbox.py 로 타입 판별(수학강의/일반)
   → [수학] 박PM 5단계 생성(하이브리드 골격에 채움) → output/{학년}/{단원}/{YYYYMMDD}_{주제}_{vid8}.html
   → 후처리 체인 → 커밋·PR·rebase 머지 → Pages 라이브
```

## 파일명·경로 규칙
- 경로: `output/{학년}/{단원}/{YYYYMMDD}_{주제16~24자}_{video_id 앞8자}.html`
- 학년: `중1`~`고3`. 단원: `{과목}-{단원}` (예: `미적분-여러가지미분법`, `수학Ⅰ-삼각함수의활용`). 공백 제거, 로마숫자 Ⅰ Ⅱ 보존.
- 상대경로 `../../` 가 `pdf-mode.css/js`·`index.html`(갤러리)을 가리킴 — 깊이 2 고정.

## 스켈레톤 자리표시자 (채울 것)
`{{TITLE}}` `{{GRADE}}` `{{SUBJECT}}` `{{UNIT}}` `{{SUBTITLE}}` `{{QUOTE_VERBATIM}}` `{{QUOTE_TIME}}`
`{{VIDEO_ID}}`(11자 풀ID) `{{VIDEO_TITLE}}` `{{CHANNEL}}` `{{DURATION}}` `{{LEARN_GOAL}}` `{{DATE}}`
도입(`{{HOOK_*}}`·`{{ASCII_DIAGRAM}}`) / 개념(`{{CONCEPT_*}}`) / 문항(`{{PROBLEM_*}}`·`{{ANSWER}}`·`{{WARN}}`) / 검증.

## 내용 규칙 (박PM 운영 원칙)
- **대상 = 중수준(하위 40%)**: 강사가 생략한 공식·단계를 모두 풀어쓴다. 유도 1회는 직접 보인다.
- **인용은 verbatim**, 영상에 실제로 나온 수치·예제를 그대로 사용.
- 문항: 기초 2 / 기본 2 / 심화 2 / 수능대비 2, **모든 문항에 정답+풀이+오답주의**. 각 풀이 STEP에 근거(`why`).
- **금지**: 실재 기출 출처 표기(❌ "2024학년도 9월 21번" → ✅ "수능 ~유형"). 정답 없는 문항. 풀이 비약.
- **검증 박스 필수**: 영상 맥락 반영 요약 + 한계/재구성 사유 + "수능 대비는 난이도 라벨, 실재 기출 아님" 명시.
- 난이도 필터 동작 조건: `#problems` 안의 `level-header`·`problem-card` 모두에 `filterable {basic|standard|advanced|csat}` 클래스.

## 후처리 체인 (HTML 저장 후, repo 루트에서)
```
python scripts/add_back_button.py        # 🏠 갤러리 복귀 버튼 (skeleton에 이미 있으면 자동 skip)
python scripts/add_related.py            # 관련 자료(같은 단원/공유 개념일 때만, REL 마커)
python scripts/make_math_stubs.py        # 옵시디언 수학 스텁 생성(수학영상노트/{YYYY}/{MM})
python youtube-math-auto/scripts/regen_index.py output/   # 갤러리 카탈로그 재생성
```
- 모두 idempotent. `make_math_stubs`는 신규만 생성(기존 skip).

## 배포
- 브랜치 커밋 → `git push` → `gh pr create` → `gh pr merge --rebase` → `deploy-pages`(~15초) → Pages 라이브.
- `--delete-branch`는 Drive 잠금으로 로컬 정리 실패 가능 → 생략, 이후 `git merge --ff-only origin/main` 로 로컬 동기화.
- 실행 중 `python -m http.server` 가 output/ 잠그면 git 실패 → 배포 전 서버 종료.

## 일반(비수학) 영상
`process_inbox.py` 가 `type=general` 로 라우팅 → claude_work 의 youtube-curator(옵시디언 풀노트). 본 표준은 수학 HTML 전용.

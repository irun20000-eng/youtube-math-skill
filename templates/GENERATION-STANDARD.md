# 학습자료 생성 표준 (하이브리드, 2026-06-14)

신규 수학 학습자료는 **하이브리드 표준**(`templates/lesson-hybrid-skeleton.html`)으로 생성한다.
정본 구현 예시: `output/고3/미적분-여러가지미분법/20260614_다변수실제변수연쇄법칙_10NhvK7s.html`.

## 전체 파이프라인 (2026-08-06 스파크 개편)

```
유튜브 영상 → 구글 스파크(Spark) 요약본 → Google Docs(제목만 .md) → 스파크 Drive 폴더에 자동 저장
   → (오케스트레이터) Drive MCP search_files/read_file_content 로 목록·본문 확보
      + _done 공유 폴더로 이미 처리된 video_id 제외
   → process_inbox.py 로 타입 판별(수학 여부 — 명시 필드 1순위, 키워드 휴리스틱 2순위. 수학 아니면 skip)
   → [수학] 박PM 5단계 생성(하이브리드 골격에 채움) → output/{학년}/{단원}/{YYYYMMDD}_{주제}_{vid8}.html
   → 후처리 체인 → 커밋·PR·rebase 머지 → Pages 라이브 → _done/{video_id}.done 마커(pipeline: math)
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

## 후처리 체인 (HTML 저장 후, repo 루트에서, idempotent 4단계)
```
python scripts/add_back_button.py                              # ① 🏠 갤러리 복귀 버튼
python scripts/add_related.py                                  # ② 관련 자료(REL 마커)
python youtube-math-auto/scripts/regen_index.py output/        # ③ 갤러리 카탈로그 재생성
python youtube-math-auto/scripts/patch_pdf_mode.py output/     # ④ PDF 인쇄 모드 링크 주입
```
## PDF 인쇄 모드 (2026-08-27 개편)

인쇄 동작은 자료 파일이 아니라 **공유 파일 두 개**(`output/pdf-mode.css`, `output/pdf-mode.js`)에
들어 있다. 70편이 모두 이 둘을 상대경로로 참조하므로, 인쇄 서식을 바꿀 때는
**여기만 고치면 전 자료에 일관 적용**된다. 자료 파일을 일괄 수정하지 말 것.

인쇄 전 두 가지 중 고른다(선택은 localStorage 에 기억된다):
- **해설 뒤로** — 문항만 앞에, 정답·풀이는 맨 뒤 `[정답·풀이]` 섹션에 모음. 학생 배포용.
  문항 아래에 손글씨 풀이 공간 2.5cm 확보.
- **해설 함께** — 문항 바로 아래에 정답·풀이를 펼쳐 출력. 교사용·자습용.
  뒷장 답지는 통째로 빠진다(같은 내용을 두 번 찍지 않음).

**문항 셀렉터는 반드시 두 템플릿을 모두 잡을 것**: `.problem-card`(A형 스켈레톤) +
`article.problem`(B형). 예전에 A형만 적혀 있어 B형 29편에서는 재배치가 아예 일어나지
않았는데 배너만 "해설은 뒷장에 모았습니다"라고 말해, 설명과 실제가 어긋나 있었다.

- `make_math_stubs.py`는 **PC(Windows) 백필 전용** — 세션·클라우드(비Windows)에선 호출 안 함(자동 dry-run으로 떨어지지만 애초에 부르지 않는다). 일상 옵시디언 스텁은 Drive MCP `create_file` 직접 호출(CLAUDE.md "옵시디언 = Drive" 섹션 참조).

## 배포
- 작업 브랜치 commit + push → MCP `create_pull_request`(base=main) → MCP `merge_pull_request`(merge_method=rebase) → `deploy-pages`(~1~2분) → Pages 라이브.
- rebase 머지가 사용자 인증 채널이라 deploy-pages 를 정상 트리거한다(CLAUDE.md "PR 머지가 가장 안정" 섹션 참조). `git push origin main` 직접 시도나 `gh` CLI 는 이 환경에서 사용하지 않는다.
- 실행 중 `python -m http.server` 가 output/ 잠그면 git 실패 → 배포 전 서버 종료.

## 일반(비수학) 영상
`process_inbox.py` 가 수학 아님으로 판별하면 마커를 만들지 않고 skip — claude_work 의 `routines/spark-reconstruct-curator.md`(옵시디언 풀노트)가 담당. 본 표준은 수학 HTML 전용.

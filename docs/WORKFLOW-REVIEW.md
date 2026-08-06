# 워크플로우 리뷰 & 보강안 (2026-06-16, v2)

이 문서는 **두 트랙(A·B) 의 단일 참조점**이다. "어제는 됐는데 오늘은" 같은 혼선의 재발을 막기 위해 입력원·실행 환경·옵시디언 작성 방식의 차이를 명문화한다.

## 1. 두 트랙

### 트랙 A — INBOX 루틴 (자동, 매일 09:00 KST, 2026-08-06 스파크 개편)

```
입력  : 구글 스파크(Spark) 요약본 → Google Docs(제목만 .md) → 스파크 폴더에 자동 저장
        스파크 folder ID: 1TEHzkORlQLtsu2CKGgy2TZMIiW-NWMdr
        공유 _done folder ID: 1_XTvautWp8O40l1ZX8Jea97I26SJofAL (claude_work 와 공용)
실행자: "클라우드 에이전트" — 09:00 KST Routine, 매 실행마다 새 세션(Linux 컨테이너)
처리  :
  1. Drive MCP search_files(parentId=스파크) 로 문서 목록, search_files(parentId=_done)
     로 완료 마커 목록 확보 → video_id 가 이미 _done/{video_id}.done 있으면 skip(1차 방어)
  2. 남은 문서 read_file_content(fileId) 로 읽어(Google Docs 라 로컬 파일처럼 못 읽음)
     로컬 스테이징 폴더에 평문 .md 로 저장
  3. python scripts/process_inbox.py --inbox <스테이징폴더> → 수학 여부 판별
       1순위: 명시적 '타입:'/'분야:' 필드(스파크 표준엔 없음, 옛 형식 호환용)
       2순위: 제목([카테고리] 태그 포함)·채널·topics·tags 키워드 휴리스틱
       (process_inbox.py 는 순수 파싱만 — Google Docs 변환이 만드는 '\_'·'\[...\]' 이스케이프,
        줄바꿈 없는 inline frontmatter 를 자체 해제/파싱한다. Drive 접근은 오케스트레이터 몫)
  4. type=math 아니면 skip, 마커 안 만듦(claude_work 의 spark-reconstruct-curator.md 담당)
  5. (수학) HTML 생성 → output/{학년}/{단원}/{YYYYMMDD}_{주제}_{vid8}.html
  6. add_back_button → add_related → regen_index → patch_pdf_mode
  7. git commit + push → 작업 브랜치 → MCP PR → rebase 머지 → deploy-pages → 갤러리
  8. ★ Drive MCP create_file → 수학영상노트/..._{vid8}.md (YYYY/MM 폴더 안 씀)
       (수학영상노트 ID: 1zDFrYoqtRLZP3QxpPKnPkwvP2UZav__k) → get_file_metadata 검증
  9. ★ 처리 완료한 video_id → _done/{video_id}.done 마커 생성
       (Drive MCP create_file, contentMimeType='text/plain', disableConversionToGoogleType=true)
       내용에 pipeline: math 필수 포함 — 실제로 완료했을 때만 생성
  10. 새 수학 영상 없으면 "처리할 새 자료 없음"만 보고
출력  : 수학영상노트, frontmatter type: youtube-math-stub, source: backfill
```

**❌ 폐지(2026-08-06)**: 옛 GAS INBOX 폴더(`1K1KndlwA4iY2VVasAcW8aDPu6AfyL2Bv`, 죽은 경로), 그 전용 `_done`(`1bkWZTT-OhPHuAlCagXnwgUgLpRqiWFL2`), `_queue`(`1aZb2Xuy_xFaPLdkgBxeca3YxYZ5-pM_5` — 실제 로직에서 한 번도 쓰인 적 없어 대체 없이 삭제).

### 트랙 B — 자연어 요청 (즉시, 사용자 세션에서 직접)

```
입력  : 사용자가 Claude Code 세션에서 자연어로 요청
        (예: "등차수열의 합과 이차함수 관련성, 함정")
        INBOX 거치지 않음 → 09:00 루틴이 영원히 못 봄
실행자: 현재 대화 중인 세션 (Linux 컨테이너)
처리  :
  1. 학년·단원 매핑 확인 (애매하면 사용자 질문, 자의 판단 ❌)
  2. HTML 생성 → output/{학년}/{단원}/{YYYYMMDD}_{주제}_개념.html
     (파일명 _개념 끝, hero src-badge + 보라 그라데이션)
  3. 갤러리 후처리 4단계 (make_math_stubs 제외):
     add_back_button → add_related → regen_index → patch_pdf_mode
  4. git push (작업 브랜치) → MCP PR → rebase 머지 → 갤러리
  5. ★ Drive MCP create_file → 수학개념노트/..._개념.md  (★ 2026-06-20: YYYY/MM 폴더 안 씀)
       (수학개념노트 ID: 1FwBBxoaoKBMpd8dqZxGzyvxI3pUoBWSX)
  6. get_file_metadata(id) 로 검증
  7. 결과 보고 (갤러리 URL + Drive 파일 링크 + PR 해시)
출력  : 수학개념노트, frontmatter type: math-concept-stub, source: concept-request
```

### 공통

- HTML 표준: `templates/lesson-hybrid-skeleton.html` + `GENERATION-STANDARD.md`
- 출력 경로: `output/{학년}/{단원}/...html`
- 문항 2/2/2/2, `filterable {level}` 클래스, 검산·오답주의 박스
- 실재 기출 출처 표기 ❌, "수능 대비 — N번 유형(준킬러)" 만
- 갤러리 발행: GitHub Pages (`deploy-pages.yml`)
- **옵시디언 노트 작성은 Drive MCP** — 로컬 `G:\` ❌, `make_math_stubs.py` ❌

## 2. 트랙 차이 한눈에

| 항목 | 트랙 A (INBOX) | 트랙 B (자연어) |
|------|---------------|-----------------|
| 입력원 | Drive INBOX `.md` | 세션 채팅 |
| 트리거 | 매일 09:00 KST cron | 사용자 발화 즉시 |
| 실행자 | 클라우드 에이전트 | 현재 세션 |
| 자료 종류 | 영상 (수학강의·일반지식) | 개념 (영상 없음) |
| 파일명 | `..._{vid8}.html` | `..._개념.html` |
| hero | 영상 썸네일/링크 | `src-badge` 보라 |
| 갤러리 카드 | 일반 | `data-source="concept"` |
| 옵시디언 폴더 | `수학영상노트/` | `수학개념노트/` |
| 스텁 type | `youtube-math-stub` | `math-concept-stub` |
| 스텁 source | `backfill` | `concept-request` |
| 처리 끝 후 | `_done` 마커 + 카카오 알림 | PR 머지 + 세션 보고 |

## 3. 누적 발견된 약점

| # | 약점 | 트랙 | 상태 |
|---|------|------|------|
| ① | "옵시디언 = 로컬 `G:\`" 오해 → 샌드박스 가짜 `G:\` 폴더 + 거짓 "성공" 로그 | A·B | ✅ 정정: Drive MCP 가 정답. `make_math_stubs.py` 는 비Windows 자동 dry-run + PC 백필 전용 |
| ② | CLAUDE.md 자연어 워크플로우가 `post_process.py`(=`make_math_stubs` 포함) 호출 권장 | B | ✅ 정정: 4단계 갤러리 후처리 + Drive MCP 직접 호출로 변경 |
| ③ | Drive 폴더 ID 가 사용자 루틴 프롬프트에만 있고 레포에 없음 | A·B | ✅ CLAUDE.md "옵시디언 = Drive" 섹션에 박제 |
| ④ | Drive MCP `create_file` 첫 호출 권한 게이트 거부 | B | ⚠️ Auto mode 시 통과. 매 세션 1회 마찰 → `/permissions` 등록 권장 |
| ⑤ | 작성 후 검증 부재 → silent failure 위험 | A·B | ✅ `get_file_metadata(id)` 검증 1회 명문화 |
| ⑥ | 폴더 이름 변경(020→010)에 자동 대응? | A·B | ✅ ID 기반 호출이라 무관 — but **이름 검색 ❌, ID 만 사용** 명문화 |
| ⑦ | 트랙 명문화 부재 → "어제는 됐는데 오늘은" 혼선 | 메타 | ✅ 본 문서로 명문화 |
| ⑧ | 트랙 A "09:00 KST INBOX 루틴"이 문서엔 있는데 실제 Routine 이 계정에 없었음(확인: 2026-08-06, `list_triggers`에 youtube-math-skill 대상 트리거 0건) | A | ✅ 신규 Routine 생성(§본 파일 트랙 A) |
| ⑨ | 옛 GAS INBOX 경로가 죽어 있었음(GAS가 더 이상 안 채움) → `process_inbox.py`가 로컬 평문 `.md`만 파싱 가능해 스파크의 Google Docs·inline frontmatter를 못 읽음 | A | ✅ 스파크 입력원 전환 + `process_inbox.py` 파싱 로직 재작성(이스케이프 해제 + inline 필드 추출) |
| ⑩ | `_queue` 폴더가 문서에만 언급되고 실제 로직에서 쓰인 적 없음(죽은 개념) | A | ✅ 대체 없이 삭제 |

## 4. 검증 체크리스트 (트랙 B 종료 직전)

- [ ] HTML 파일이 `output/{학년}/{단원}/{YYYYMMDD}_{주제}_개념.html` 에 있는가
- [ ] `filterable basic/standard/advanced/csat` 클래스가 8문항 전부에 있는가
- [ ] 갤러리 후처리 4단계 모두 "추가/건너뜀" 정상 종료했는가 (실패 0)
- [ ] 작업 브랜치 push → PR 생성 → rebase 머지 성공했는가
- [ ] Drive MCP `create_file` 응답에 `id` 가 있는가
- [ ] `get_file_metadata(id)` 결과 `title`·`parentId` 일치하는가
- [ ] 사용자 보고에 3개 링크(갤러리 URL · Drive 링크 · PR 해시) 포함했는가

## 5. 코드/도구 위치 (혼동 방지)

| 도구 | 환경 | 용도 |
|------|------|------|
| `scripts/add_back_button.py` | 어디서나 | 갤러리 복귀 버튼 패치 |
| `scripts/add_related.py` | 어디서나 | 관련 자료 카드 |
| `youtube-math-auto/scripts/regen_index.py` | 어디서나 | 갤러리 index 재생성 |
| `youtube-math-auto/scripts/patch_pdf_mode.py` | 어디서나 | PDF 인쇄 모드 |
| **Drive MCP `create_file`** | 세션·클라우드 | **옵시디언 스텁 작성 (일상 경로)** |
| `scripts/make_math_stubs.py` | **PC(Windows) 전용** | 갤러리→옵시디언 **백필**(과거 자료 일괄) 용. 비Windows 에선 자동 dry-run |
| `scripts/post_process.py` | 어디서나 | 후처리 5단계 통합 — 단 ③ 스텁은 비Windows 자동 dry-run. 일상 트랙 A·B 에선 4단계 개별 호출 권장 |

## 6. 미적용 / 향후 (참고)

- **d. `post_process.py` 의 ③ 단계 기본 OFF**: `--include-stubs` 플래그로 옵트인. PC 백필 시만 켜기.
- **e. `make_math_stubs.py` 헤더에 "PC 백필 전용" 명시**: 미래 세션 혼동 방지.
- **g. 갤러리 카드 sanity check**: push 전에 `index.html` 에 새 카드 존재 + `data-source` 정확한지 1회 확인.
- **h. PR template 체크리스트**: §4 체크리스트를 PR body 에 박아 자기검증 강제.
- **i. Drive MCP 권한 자동 허용**: 세션 시작 시 `create_file` 권한 ask → allow 자동 처리.
- **j. INBOX 통합**: 자연어 요청도 INBOX 텍스트로 떨어뜨려 단일 파이프라인. 단 사용자 결정: **"자연어는 세션에서 바로 처리, 루틴에 포함 안 함"** — 이 결정 유지 시 j 불필요.

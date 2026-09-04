# Claude Code 세션 가이드 — youtube-math-skill

이 파일은 Claude Code가 매 세션 시작 시 자동으로 읽는 컨텍스트입니다. 새 세션이든 이어가는 세션이든, 다음 규칙을 따라 작업하세요.

## 🔄 세션 시작 시 (매번, 환경 불문)

작업 시작 전 **무조건** GitHub 레포에서 최신 변경사항을 가져옵니다. 다른 기기(모바일·PC·샌드박스)에서 push 했을 가능성이 있고, 동기화 안 하면 갤러리가 옛날 상태로 보입니다.

```bash
# 작업 디렉토리로 이동 (사용자 OS 별)
cd "G:/내 드라이브/Claude_Project/Youtube-math_skill"   # Windows PC (현 정본 경로)
# 또는 cd ~/youtube-math-skill   # Mac/Linux/샌드박스
git fetch origin
git checkout main && git pull --rebase
git checkout <작업브랜치> 2>/dev/null && git rebase main 2>/dev/null || true
```

git pull 결과:
- "Already up to date" → 그대로 진행
- 새 커밋 받음 → 어떤 파일이 변경됐는지 확인하고 사용자에게 공유 (모바일·다른 PC 작업이 있을 수 있음)
- 충돌 발생 → 사용자 결정 받기. 강제 해결 ❌.

## 🌐 "갤러리는 항상 최신" 원칙 (사용자 명시 요청)

사용자 요청 (2026-05-05): **"항시 갤러리 최신화되도록 작업"**.

이를 보장하기 위해 모든 세션은 다음 두 조건을 반드시 만족시킨다.

### A. 작업 종료 전 main 강제 동기화
output/ 또는 카탈로그가 바뀌었으면 작업 끝나기 전에 무조건:
1. 작업 브랜치에 commit + push
2. main 으로 ff-merge + push (없으면 갤러리 배포 안 됨)
3. 사용자에게 "갤러리 1~2분 내 갱신" 알림 + 갤러리 URL 명시

### B. 사용자에게 "정답 보기" 안내
PC 로컬 `output/index.html` 파일은 git pull 안 하면 옛날 그대로다. 사용자가 다른 기기 작업을 보려면 두 방법 중 하나:
1. **권장 — 갤러리 URL 직접 열기**: https://irun20000-eng.github.io/youtube-math-skill/ (모든 기기에서 항상 최신, 캐시 의심되면 Ctrl+Shift+R)
2. **PC 로컬 파일 쓸 거면**: 먼저 PC 에서 `git pull --rebase` 후 `output/index.html` 새로고침

세션 마지막 멘트에 갤러리 URL 을 항상 포함해 사용자가 즉시 검증 가능하게 한다.

## 📁 단일 진실 소스 = GitHub 레포

이 프로젝트의 모든 자료는 GitHub 레포(`youtube-math-skill`) 가 최종 진실 소스입니다.
- 로컬 파일은 작업 중간 상태일 뿐
- 작업 완료 시 반드시 commit + push
- push 안 한 자료는 다른 기기에서 못 봄

## ✅ 자료 생성 후 push — 빠른 경로 (작업 브랜치만, fallback용)

> ⚠️ **정식 방법은 아래 "PR + 머지가 가장 안정" 섹션이다.** 이 빠른 경로는 작은 변경의 임시 fallback — 작업 브랜치 push만으로는 main 갤러리 배포가 트리거되지 않으니, 갤러리 갱신이 필요하면 아래 PR+머지를 쓸 것.

새 학습자료(.html)를 `output/` 에 만들었거나 카탈로그가 갱신됐으면, 사용자가 별도 요청 없어도 다음만 수행:

```bash
# 작업 브랜치에 commit + push만 — 끝!
git add output/
git -c user.name="Local" -c user.email="local@local" commit -m "<적절한 메시지>"
git push -u origin <작업브랜치>
```

## ✅ 자료 생성 후 자동 push (PR + 머지가 가장 안정)

새 학습자료(.html)를 `output/` 에 만들었거나 카탈로그가 갱신됐으면 다음 순서로 처리:

```bash
# 1. 카탈로그 재생성 후 작업 브랜치에 commit + push
python youtube-math-auto/scripts/regen_index.py output/
git add output/
git -c user.name="Local" -c user.email="local@local" commit -m "<적절한 메시지>"
git push -u origin <작업브랜치>
```

그 다음 **MCP로 PR 생성 + rebase 머지**:
```
mcp__github__create_pull_request (head=<작업브랜치>, base=main)
mcp__github__merge_pull_request (merge_method=rebase)
```

**PR 머지가 가장 안정적인 이유 (2026-05-15 검증)**:
- 인라인 content 안 보내도 됨 (작업 브랜치 commit 그대로 main으로 옮김)
- rebase 머지 = 머지 commit이 **사용자 인증(`irun20`)** 으로 처리됨 → 일반 push event → deploy-pages 트리거
- 봇 자동 트리거가 비활성화 상태라 [skip ci] commit 가로채기 없음

**충돌 시**: 작업 브랜치를 `git rebase main` 후 force-push 재시도. PR 다시 머지.

**MCP fallback 옵션 (작은 변경만)**:
- `mcp__github__create_or_update_file` (단일 파일, content 인라인)
- `mcp__github__push_files` (여러 파일 한 commit, content 인라인)
- 둘 다 사용자 인증 채널이라 deploy-pages 트리거 ✔

**❌ 신뢰하지 말 것**:
- `auto-merge-to-main.yml` 통합 워크플로우 — 2026-05-11·14·15 세 차례 4분 내 실행 실패. 원인 불명. 무시하고 PR 머지 방식 사용.
- Claude 직접 `git push origin main` — 환경 정책상 HTTP 403 간헐 차단. 봇은 GITHUB_TOKEN 별개 채널이라 통과하지만 그것도 별 의미 없음 (위 워크플로우 미동작).

**카탈로그 갱신 책임 (2026-05-15)**:
- `auto-regen-catalog.yml` 은 **자동 트리거 비활성**. 봇이 [skip ci] commit 으로 deploy-pages 가로채던 문제 해소.
- 사용자 push 측에서 `regen_index.py` 를 돌려 INDEX.md/index.html 을 함께 commit.

push 후 사용자에게 알림: "GitHub Actions 가 1~2분 내 갤러리 갱신 — https://irun20000-eng.github.io/youtube-math-skill/"

## 🗂️ 옵시디언 = Google Drive (로컬 G:\ 아님, 2026-06-16 명문화)

옵시디언 볼트는 사용자 PC 의 로컬 `G:\` 가 아니라 **Google Drive** 에 동기화돼 있다.
세션/클라우드 컨테이너는 `G:\` 에 접근 불가 → 옵시디언 스텁 `.md` 는 **Drive MCP `create_file` 로 직접 작성**한다.

| 용도 | Drive folder ID |
|------|----------------|
| **스파크(Spark) 요약본** (INBOX 입력원, 2026-08-06 교체) | `1TEHzkORlQLtsu2CKGgy2TZMIiW-NWMdr` |
| **스파크 `_done`** (공유 완료 마커, claude_work 와 공용) | `1_XTvautWp8O40l1ZX8Jea97I26SJofAL` |
| Vault root (010-Youtube-Obsi)* | `11kYZv_E3Go4_jhSIaNSqrVw1TjlJ8J7d` |
| **수학영상노트** (영상 자료 스텁) | `1zDFrYoqtRLZP3QxpPKnPkwvP2UZav__k` |
| **수학개념노트** (자연어 개념 자료 스텁) | `1FwBBxoaoKBMpd8dqZxGzyvxI3pUoBWSX` |
| 일반 YouTube (일반지식 노트) | `1j8jRPbq9WmBHYilcX4v8R4qv_hObM664` |

> *볼트 root 폴더 이름은 `020-Youtube-Obsi` → `010-Youtube-Obsi` 처럼 바뀔 수 있음.
> Drive **ID 기반 호출**이라 이름 변경에 무관. ID 만 신뢰할 것 (이름 검색 ❌).

> **❌ 폐지(2026-08-06)**: 옛 GAS INBOX 폴더(`1K1KndlwA4iY2VVasAcW8aDPu6AfyL2Bv`, 죽은 경로 — GAS가 더 이상 채우지 않음), 옛 INBOX 전용 `_done`(`1bkWZTT-OhPHuAlCagXnwgUgLpRqiWFL2`), `_queue`(`1aZb2Xuy_xFaPLdkgBxeca3YxYZ5-pM_5`). `_queue`는 애초에 실제 로직에서 한 번도 쓰인 적 없는 죽은 개념이라 대체 없이 삭제. 아래 "스파크 기반 트랙 A" 섹션 참조.

### 📥 스파크(Spark) 기반 트랙 A — 입력원 전환 (2026-08-06)

claude_work 리포가 노트 파이프라인을 구글 스파크 요약본 기반으로 전환하면서, 이 레포도 같은 스파크 폴더를 입력원으로 본다.

- 스파크 폴더의 파일은 제목이 `.md`로 끝나지만 **실제로는 Google Docs 문서**다. 로컬 파일처럼 읽을 수 없다 — 반드시 Drive MCP `read_file_content(fileId)` 로 읽는다.
- 파일명 패턴: `{YYYY-MM-DD}_[카테고리]_{영상제목}.md`.
- 본문엔 `type: youtube-insight`, `title`, `url`, `video_id`, `channel`, `published`, `duration_min`, `topics`, `tags` 등 frontmatter 유사 텍스트가 있지만, Google Docs 변환 과정에서 **`---` YAML 펜스가 없고 모든 필드가 줄바꿈 없이 한 문단에 이어붙으며**, `_`·`[`·`]`·`*` 가 `\_`·`\[`·`\]`·`\*` 로 이스케이프되고, 이모지가 `ð` 등으로 깨진다. `scripts/process_inbox.py` 가 이 형태를 그대로 파싱하도록 되어 있다(이스케이프 해제 + 줄바꿈 없는 inline 필드 추출).

**타입 판별 — `process_inbox.py`의 `classify_study_method()` → `classify_math()`**:
0. **0순위(공부법)**: `classify_study_method()` 를 먼저 실행 — 제목(파일명의 `[카테고리]` 태그 포함)·topics·tags 에서 `STUDY_METHOD_KEYWORDS`(공부법·시간관리·메타인지·오답노트·오답분석·실전전략 등) 매치 시 `type=study_method` 로 확정(아래 math 판정보다 우선 — "분야: 수학강의" 같은 넓은 필드에 낚이지 않도록). 상세는 아래 "📝 수학 공부법 자료 워크플로우 (트랙 C)" 참조.
1. **1순위(명시적 필드)**: 0순위에서 안 걸리면, 본문에 `타입:`/`분야:` 필드가 있고 값에 `수학`이 포함되면 확정 수학(옛 리포트 형식 호환용 — 스파크 표준 템플릿엔 이 필드가 없어 사실상 항상 2순위로 감).
2. **2순위(휴리스틱)**: 제목(파일명의 `[카테고리]` 태그 포함)·채널·topics·tags 를 합쳐 `MATH_KEYWORDS`(수학·미적분·확률과통계·기하·대수·함수·방정식·부등식·수열·극한·미분·적분·벡터·행렬·삼각함수·로그·지수·도형·확률·통계·수능·모의고사·학력평가·내신·N제·기출·문제풀이) 매치 여부로 판정.
3. 셋 다 아니면 **이 레포는 관여하지 않고 skip** — claude_work 의 `routines/spark-reconstruct-curator.md` 가 일반 노트로 처리한다.

**공유 완료 마커 (`_done` 폴더, claude_work 와 공용)**:
- 마커 파일명 `{video_id}.done`, video_id 당 하나만 존재. **처리 시작 전 반드시 먼저 `_done/{video_id}.done` 존재 여부 확인 — 있으면(내용의 `pipeline` 값과 무관하게) 즉시 skip**(이미 어느 쪽이든 처리 완료).
- **이 레포가 실제로 처리를 완료했을 때만** 마커 생성, 내용에 `pipeline: math` 또는 `pipeline: study_method` 필수 포함(처리한 트랙에 맞게). 수학도 공부법도 아니라고 판단해 skip한 문서엔 마커를 만들지 않는다(claude_work 쪽이 자기 마커를 남긴다).
- 생성은 Drive MCP `create_file(contentMimeType='text/plain', disableConversionToGoogleType=true, parentId=스파크 _done ID)`.
- `output/` 내 `find_existing()` dedup 은 2차 방어로 계속 유지(공유 마커가 1차 방어).

### 옵시디언 스텁 작성 절차 (Drive MCP)

> **★ 2026-06-20 변경**: YYYY/MM 하위 폴더를 만들지 않는다. 노트는 **`수학영상노트/`, `수학개념노트/` 바로 아래**에 작성. 정렬·검색은 파일명 접두사 `YYYYMMDD_` 로 충분.

1. `create_file (contentMimeType="text/markdown", disableConversionToGoogleType=true, parentId={수학영상노트 또는 수학개념노트 ID})` 로 `.md` 작성. **YYYY/MM 폴더 만들지 말 것.**
2. **★ 작성 후 검증**: 응답에서 받은 `id` 로 `get_file_metadata(id)` → `title`·`parentId` 가 의도(부모 폴더 ID 와 일치) 와 맞는지 1회 확인. silent failure 의 마지막 안전망.
3. 사용자 보고에 Drive 파일 링크 `https://drive.google.com/file/d/{id}/view` 를 항상 포함.

### `make_math_stubs.py` 위치 (혼동 방지)

- **PC(Windows) 갤러리→옵시디언 백필 전용** 도구. 정기 워크플로우 아님.
- 세션·클라우드(=비 Windows) 환경에선 호출 금지 — 어차피 `os.name != "nt"` 자동 dry-run 으로 떨어지지만, 처음부터 부르지 말 것.
- 일상 옵시디언 스텁 작성은 위 **Drive MCP 직접 호출**.

## 🎬 영상 → 학습자료 워크플로우 (트랙 A)

### A-1. 09:00 KST 자동 루틴 (스파크 기반, 2026-08-06 신규 생성)

매일 09:00 KST, 새 세션을 띄우는 Routine 이 자동 수행(정기 처리):

1. Drive MCP `search_files(parentId=스파크 1TEHzkORlQLtsu2CKGgy2TZMIiW-NWMdr)` 로 문서 목록, `search_files(parentId=_done 1_XTvautWp8O40l1ZX8Jea97I26SJofAL)` 로 완료 마커 목록 확보.
2. video_id 가 이미 `_done/{video_id}.done` 로 있으면 skip(1차 방어).
3. 남은 문서를 `read_file_content(fileId)` 로 읽어 로컬 스테이징 폴더에 평문 `.md` 로 저장.
4. `python scripts/process_inbox.py --inbox <스테이징폴더>` 로 타입 판별(위 "스파크 기반 트랙 A" 섹션 참조 — 공부법 0순위 → 수학 1/2순위).
5. `type=math` 인 것만 아래 A-2 의 3~8단계(자료 생성 ~ 결과 보고)를 그대로 수행. `type=study_method` 인 것은 "📝 수학 공부법 자료 워크플로우 (트랙 C)" 절차를 수행.
6. 완료한 건은 `_done/{video_id}.done` 마커 생성(math는 `pipeline: math`, 공부법은 `pipeline: study_method` 필수 포함). 어느 쪽도 아니라 skip한 문서는 마커를 만들지 않는다.
7. 처리할 새 수학 영상이 없으면 "처리할 새 자료 없음"만 보고.

### A-2. 세션에서 직접 처리할 때 (URL + 자동 자막 추출)

09:00 루틴과 별개로, **사용자가 세션에서 직접 처리**할 때의 절차.

1. **메타데이터 확인**: `youtube-math-auto/scripts/output_path.py` 의 `find_existing()` 으로 중복 체크
2. **자막 추출**: `python youtube-math-auto/scripts/fetch_subtitle.py "URL" --out subs/` (yt-dlp 사용, 사용자 IP라 차단 회피)
3. **자료 생성**: `youtube-math-lesson` 본 스킬 호출 — 박PM 페르소나, 8단계 페르소나, 5단계 워크플로우
4. **출력 경로**: `youtube-math-auto/scripts/output_path.py` 의 `build_output_path()` 로 정확한 경로 빌드
5. **갤러리 후처리** (idempotent, 4단계 — `make_math_stubs.py` 는 제외):
   - `python scripts/add_back_button.py`           ① 갤러리 복귀 버튼
   - `python scripts/add_related.py`               ② 관련 자료 카드
   - `python youtube-math-auto/scripts/regen_index.py output/`   ③ 갤러리 index 재생성
   - `python youtube-math-auto/scripts/patch_pdf_mode.py output/` ④ PDF 인쇄 모드 링크 주입
6. **push**: 위 "자동 push" 단계 (작업 브랜치 → MCP PR → rebase 머지 → deploy-pages)
7. **★ 옵시디언 스텁 — Drive MCP `create_file` 로 직접 작성** (위 "옵시디언 = Drive" 섹션 절차 사용):
   - 부모: 수학영상노트 ID `1zDFrYoqtRLZP3QxpPKnPkwvP2UZav__k` **바로 아래** (YYYY/MM ❌)
   - frontmatter `type: youtube-math-stub`, `source: backfill`, `tags: [math]`
   - 작성 후 `get_file_metadata(id)` 검증 필수
8. **결과 보고 (3개 링크 + 상태)**: 갤러리 URL · Drive 파일 링크 · PR 머지 해시

## 🆕 자연어 개념 요청 워크플로우 (트랙 B — 영상 없이, 2026-06-16 명문화)

사용자가 URL 없이 자연어로 개념 학습자료를 요청하면 (예: "등차수열 합과 이차함수 관련성").
**INBOX 루틴(트랙 A) 안 거침** — 사용자가 명시: 자연어 요청은 INBOX에 떨어뜨리지 않으니 09:00 루틴이 못 봄. 따라서 같은 세션에서 즉시 완결한다.

1. **학년/단원 매핑 확인** — 애매하면 사용자에게 질문. 자의적 판단 ❌.
2. **출력 경로**: `output/{학년}/{단원}/{YYYYMMDD}_{핵심주제}_개념.html`
   - 파일명 **반드시 `_개념` 으로 끝낼 것** → 갤러리 `data-source="concept"`, 옵시디언 `수학개념노트/` 라우팅 트리거.
3. **베이스**: `templates/lesson-hybrid-skeleton.html` + hero 에 `src-badge` + 보라 그라데이션. 기존 `_개념.html` 자료를 참조 복제 권장.
4. **문항**: 기초 2 / 기본 2 / 심화 2 / 수능대비 2, `filterable {level}` 클래스 필수.
5. **갤러리 후처리** (idempotent, 4단계 — `make_math_stubs.py` 는 제외):
   - `python scripts/add_back_button.py`
   - `python scripts/add_related.py`
   - `python youtube-math-auto/scripts/regen_index.py output/`
   - `python youtube-math-auto/scripts/patch_pdf_mode.py output/`
6. **push**: 작업 브랜치 commit + push → MCP PR rebase 머지 → deploy-pages.
7. **★ 옵시디언 스텁 — Drive MCP `create_file` 로 직접 작성** (위 "옵시디언 = Drive" 섹션 절차 사용):
   - 부모: 수학개념노트 ID `1FwBBxoaoKBMpd8dqZxGzyvxI3pUoBWSX` **바로 아래** (YYYY/MM ❌)
   - frontmatter `type: math-concept-stub`, `source: concept-request`, `tags: [math, concept]`
   - 작성 후 `get_file_metadata(id)` 검증 필수
8. **결과 보고 (3개 링크 + 상태)**:
   - 갤러리 URL (예: `https://irun20000-eng.github.io/youtube-math-skill/{경로}.html`)
   - Drive 파일 링크 (`https://drive.google.com/file/d/{id}/view`)
   - PR 머지 해시

> 트랙 A·B 비교, 검증 체크리스트, 약점 진단은 `docs/WORKFLOW-REVIEW.md` 참조.

## 📝 수학 공부법 자료 워크플로우 (트랙 C, 2026-09-04 신설)

스파크 문서 중 "분야: 수학강의"로 태그되어 있지만 실제 내용은 수학 개념·문제풀이가 아니라
시험전략·시간관리·메타인지·오답분석 같은 **"공부법" 영상**인 경우가 있다(예: 이동준 채널의
"9모 시험 끝나자마자 해야 할 일", "ABC 공부법"). 이런 영상에 `youtube-math-lesson` 의
8~10문항 문제집 형식을 강제하면 영상에 없는 수학 문제를 지어내야 해서 사용하지 않는다.

**분류 (A-1 09:00 루틴에 통합됨)**: `scripts/process_inbox.py` 의 `classify_study_method()` 가
`classify_math()` 보다 먼저 실행되어 파일명 `[카테고리]` 태그·title·topics·tags 에서
`STUDY_METHOD_KEYWORDS`(공부법·시간관리·메타인지·오답노트·오답분석·슬럼프·멘탈관리·
학습전략·시험전략·실전전략·자기주도학습·공부습관·9모분석·수능전략)를 매치하면
`type: "study_method"` 로 확정 라우팅한다(math 판정보다 우선 — "수학강의" 같은 넓은 명시
필드에 낚이지 않도록). 매치 없으면 기존처럼 `classify_math()` 로 폴백.

**자료 생성 절차** (A-1 5단계에서 `type=study_method` 인 것만 이 경로를 탄다):
1. **베이스**: `templates/study-method-skeleton.html` (보라 그라데이션 히어로, KaTeX는 선택적).
   영상의 실천 프로토콜(단계별 체크리스트) · 인상적 발언(타임스탬프 인용) · 핵심 개념/공식(있을 때만)
   · 복습 퀴즈 · 기억할 것(플래시카드) 섹션으로 구성. 문항 8~10개, 난이도 필터는 넣지 않는다.
2. **출력 경로**: `output_path.build_study_method_path()` 사용 →
   `output/공부법/{단원}/{YYYYMMDD}_{핵심주제}_공부법.html`. 파일명 **반드시 `_공부법` 으로 끝낼 것**
   → 갤러리 `data-source="study"`(📝 공부법 필터 탭) 라우팅 트리거. video_id는 파일명에 넣지 않고
   본문 영상 카드 링크에만 담는다(썸네일은 본문 URL에서 자동 복구되므로 정상 표시됨).
3. **갤러리 후처리**: 트랙 A/B와 동일 4단계(add_back_button → add_related → regen_index →
   patch_pdf_mode).
4. **push**: 작업 브랜치 commit + push → MCP PR rebase 머지 → deploy-pages.
5. **옵시디언 스텁**: 수학영상노트 폴더에 동일 절차로 작성하되 frontmatter
   `type: study-method-stub`, `tags: [math, study-method]`.
6. **`_done` 마커**: `pipeline: study_method` 로 생성(트랙 A의 math 마커와 동일 폴더/방식).
7. **결과 보고**: 갤러리 URL · Drive 스텁 링크 · PR 머지 해시(트랙 A/B와 동일 형식).

## 🎯 학습자 수준 가이드 (반드시 적용)

`youtube-math-auto/SKILL.md` 의 "학습자 수준 가이드" 섹션을 본 스킬 호출 시 반드시 전달:

> **대상**: 중수준(하위 40%) 학생도 따라갈 수 있는 호흡.
> 영상에서 강사가 "당연하다"고 생략한 모든 공식·정리·용어를 개념 설명에서 풀어쓸 것. 결과 공식만 제시 ❌, 유도 1번은 반드시 포함. 선수 학습은 1~2문장으로 환기. 풀이 STEP은 한 줄에 한 단계로 분리, 비약 금지.

## 📐 교육과정 범위 제한 (현 고2 학생 대상, 2026-05-06 정정)

**교과명 변경 (2022 개정 교육과정 적용)**:
- **현 고3**: 수학Ⅰ + 수학Ⅱ (기존 명칭)
- **현 고2**: **대수 + 미적분Ⅰ** (명칭·내용 재편성)
  - 기존 수학Ⅰ → 대체로 "대수" 로 이전
  - 기존 수학Ⅱ → 대체로 "미적분Ⅰ" 로 이전 (단, 삼각함수 미분 등 일부 추가 가능)

**수능에서 빠진 것 (현 고2 기준)**:
- ❌ **고3 선택과목 "미적분"** (= 기존 미적분Ⅱ 영역, 가장 어려운 미적분).
- ⚠️ "미적분" ≠ "미적분Ⅰ". 미적분Ⅰ 은 필수 과목으로 수능 범위에 포함됨.

**삼각함수 덧셈정리 등 — 사용 가능 여부는 사용자 확인 필요**:
- 한국 교육과정에서 삼각함수의 덧셈정리·배각·반각이 미적분Ⅰ 에 포함되는지, 선택 미적분에만 포함되는지가 개정 시점마다 달라짐.
- **확신 안 들면 사용자에게 단원 매핑 확인 후 결정**. 자의적 판단 ❌.

**활용 가능 (현 고2 대수 + 미적분Ⅰ 범위 — 안전하게 사용 가능한 영역)**:
- ✅ 삼각함수의 정의·그래프·주기, 사인법칙·코사인법칙 (대수)
- ✅ 일반각의 삼각함수, 단위원 기반 사고 (대수)
- ✅ 지수·로그 함수, 수열의 합 시그마 (대수)
- ✅ 다항함수의 극한·미분·적분, 도함수 활용 (미적분Ⅰ)
- ✅ 정적분의 기본정리, 다항함수 정적분의 도형 응용 (미적분Ⅰ)

**확실히 제외 (선택 미적분 영역, 현 고2 수능 미포함)**:
- ❌ **삼각함수의 덧셈정리·배각·반각·합곱 변환** ($\sin(\alpha\pm\beta)$, $\cos 2\alpha$ 등) — 사용자 확인 (2026-05-06): 현 고2 수능 범위 외.
- ❌ 부분적분, 치환적분, 회전체 부피 등 미적분Ⅱ 고난도 영역
- ❌ 수열의 극한·급수의 수렴 발산 (선택 미적분)
- ❌ 매개변수 미분, 음함수 미분 (선택 미적분)
- ❌ 삼각함수의 극한·미분 ($\lim_{x\to 0}\sin x/x$, $(\sin x)'$ 등) — 덧셈정리에 의존하므로 동일 제외

**판단 어려운 영역 (사용자에게 확인 후 진행)**:
- ❓ 합성함수 미분 (다항함수만이라면 미적분Ⅰ 가능, 일반은 선택 미적분)
- ❓ 새 단원 등장 시 사용자에게 학생 교과서 단원명 확인 후 결정

문항이 위 ❌ 영역을 사용해야 한다면, **다른 풀이로 우회**: 특수각 활용, 기하적 풀이, 코사인법칙 직접 적용 등. 우회 안 되면 해당 문항 제외하고 다른 패턴으로 대체.

## 🖨️ PDF 인쇄 모드 (2026-08-27 개편)

인쇄 동작은 자료 파일이 아니라 **공유 파일 두 개**에 있다:
`output/pdf-mode.css`, `output/pdf-mode.js`. 70편이 모두 상대경로로 이 둘을 참조하므로
**인쇄 서식은 여기만 고치면 전 자료에 일관 적용**된다. 자료 파일을 일괄 수정하지 말 것.

인쇄 전 사용자가 두 가지 중 고른다(선택은 localStorage 기억):
| 선택 | 결과 | 용도 |
|------|------|------|
| **해설 뒤로**(기본) | 문항만 앞에, 정답·풀이는 맨 뒤 `[정답·풀이]` 섹션에 모음. 문항 아래 손글씨 공간 2.5cm | 학생 배포용 |
| **해설 함께** | 문항 바로 아래에 정답·풀이를 펼쳐 출력. 뒷장 답지는 빠짐 | 교사용·자습용 |

**인쇄본 바닥글**: 페이지마다 좌측하단에 워드마크 + `@irun20000` 이 찍힌다(`.print-brand-footer`).
`@page` 여백 상자(`@bottom-left`)에는 이미지를 안정적으로 넣을 수 없어 고정 요소로 구현했다.
페이지 번호만 `@bottom-right` 에 남겨 뒀다.

**PDF 버튼 위치**: 자료 툴바(🏠 갤러리 · 🌙 다크모드) 안, 다크모드 바로 뒤에 끼워 넣는다.
우상단 고정으로 띄우면 난이도 필터(전체·기초·기본…)를 덮는다(2026-08-27 수정).

**문항 셀렉터는 두 템플릿을 모두 잡을 것** — `.problem-card`(A형 스켈레톤) + `article.problem`(B형).
예전엔 A형만 적혀 있어 **B형 29편은 해설 재배치가 아예 안 되는데도** 배너는
"해설은 뒷장에 모았습니다"라고 표시해, 설명과 실제가 어긋나 있었다(2026-08-27 수정).

## 🔤 `<title>` 태그 작성 규약 (KaTeX 수식 금지)

학습자료 HTML 의 `<title>` 태그는 **갤러리(`output/index.html`) 가 그대로 가져다 쓰는데, 갤러리는 KaTeX 가 적용되지 않는다**. `<title>` 안에 `$y=\sin x$` 처럼 KaTeX 수식 구문을 넣으면 갤러리 카드에 `$y=\sin x$` 가 그대로 노출된다.

**규약**:
- `<title>` 태그: **평문만** 사용. 수식은 `y=sin x`, `a=2RsinA` 처럼 평문 표기로 환원.
- `<h1>` 본문 헤더: KaTeX 적용되므로 `$y=\sin x$` 처럼 수식 구문 자유롭게 사용 가능.

**안전장치**: `regen_index.py` 의 `extract_meta()` 가 추출한 title 에서 `$` 와 `\` 를 자동 제거 (2026-05-06 추가). 그래도 작성 단계에서 평문으로 쓰는 게 가독성·검색성에 좋음.

## 📂 명명 규칙 (반드시 준수)

```
output/{학년}/{단원}/{YYYYMMDD}_{핵심주제}_{video_id8}.html
```

- `학년`: `중1~고3` 또는 `미분류`
- `단원`: 학년 코드(`고1-`) 빼고. 30자 한도. 한글·로마숫자 OK.
- `핵심주제`: 16~24자, 공백·구두점 제거.
- `video_id8`: YouTube ID 앞 8자.

빌드는 `output_path.build_output_path()` 사용. 직접 문자열로 만들지 말 것.

## 🚫 절대 금지

- ❌ **실재 기출문제 출처 표기** (예: "2024학년도 9월 모의고사 21번"). "수능 대비 — N번 유형(준킬러)" 으로만.
- ❌ 자막/요약 없이 영상 추측 분석.
- ❌ 진행 중 라이브 스트림 처리 (자막 없음).
- ❌ git push 없이 작업 종료. 사용자가 명시적으로 "push하지 마"라고 안 한 이상 반드시 push.

## ⚠️ 충돌·중복 처리

- **`git pull` 실패 (충돌)**: 사용자에게 즉시 알림. 강제 해결 ❌. 사용자 결정 받기.
- **중복 영상 감지** (`find_existing()` 매치 1+개): 사용자에게 옵션 제시 — 건너뛰기 / 덮어쓰기 / `_v2` 새 버전.

## 🌐 갤러리 URL

생성된 자료 + 갤러리는 항상 `https://irun20000-eng.github.io/youtube-math-skill/` 에서 즉시 확인 가능. 학생 공유 시 이 URL.

## 📱 다른 진입점들

이 레포는 PC뿐 아니라 다음에서도 작업 가능:
- 모바일 Claude 앱 + GitHub Connector → 직접 push
- 모바일 GitHub 앱 → Issue 자동화 (`.github/workflows/add-lesson-from-issue.yml`) → 자동 처리

세 경로 모두 같은 GitHub 레포에 모이므로 갤러리는 항상 동기화.

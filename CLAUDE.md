# Claude Code 세션 가이드 — youtube-math-skill

이 파일은 Claude Code가 매 세션 시작 시 자동으로 읽는 컨텍스트입니다. 새 세션이든 이어가는 세션이든, 다음 규칙을 따라 작업하세요.

## 🔄 세션 시작 시 (매번)

작업 시작 전 GitHub 레포에서 최신 변경사항을 가져옵니다 (다른 기기·세션이 push 했을 수 있음):

```bash
cd C:/Users/user/Desktop/Claude_ProjecT/Youtube-math_skill  # 또는 사용자 OS 경로
git pull --rebase
```

git pull 결과:
- "Already up to date" → 그대로 진행
- 새 커밋 받음 → 어떤 파일이 변경됐는지 확인하고 사용자에게 공유

## 📁 단일 진실 소스 = GitHub 레포

이 프로젝트의 모든 자료는 GitHub 레포(`youtube-math-skill`) 가 최종 진실 소스입니다.
- 로컬 파일은 작업 중간 상태일 뿐
- 작업 완료 시 반드시 commit + push
- push 안 한 자료는 다른 기기에서 못 봄

## ✅ 자료 생성 후 자동 push + main 머지 (반드시 둘 다)

새 학습자료(.html)를 `output/` 에 만들었거나 카탈로그(`INDEX.md`, `index.html`)가 갱신됐으면, 사용자가 별도 요청 없어도 다음을 수행:

```bash
# 1. 작업 브랜치(예: claude/...)에 commit + push
git add output/
git -c user.name="Local" -c user.email="local@local" commit -m "<적절한 메시지>"
git push -u origin <작업브랜치>

# 2. main 으로 ff-merge + push (갤러리 자동 배포 트리거)
git fetch origin main
git checkout main
git merge --ff-only <작업브랜치>
git push origin main

# 3. 다시 작업브랜치로 복귀 (다음 작업 대비)
git checkout <작업브랜치>
```

**왜 main 까지 푸시하는가**: `.github/workflows/deploy-pages.yml` 은 `main` 브랜치 push 에만 GitHub Pages 배포를 트리거. 작업 브랜치만 푸시하면 갤러리가 갱신되지 않음. 사용자가 2026-05-05 세션에서 "앞으로 main 까지 작업해라" 명시 허락함.

**ff-merge 충돌 시**: `--ff-only` 가 실패하면 사용자 결정 받기 (rebase / merge commit / 작업 보류 중 택일). 강제 해결 ❌.

push 후 사용자에게 알림: "GitHub Actions가 1~2분 내 갤러리 자동 갱신합니다 — https://irun20000-eng.github.io/youtube-math-skill/"

## 🎬 영상 → 학습자료 워크플로우

사용자가 YouTube URL을 던지면 `youtube-math-auto` 스킬을 트리거하거나 다음 흐름을 따라 직접 처리:

1. **메타데이터 확인**: `youtube-math-auto/scripts/output_path.py` 의 `find_existing()` 으로 중복 체크
2. **자막 추출**: `python youtube-math-auto/scripts/fetch_subtitle.py "URL" --out subs/` (yt-dlp 사용, 사용자 IP라 차단 회피)
3. **자료 생성**: `youtube-math-lesson` 본 스킬 호출 — 박PM 페르소나, 8단계 페르소나, 5단계 워크플로우
4. **출력 경로**: `youtube-math-auto/scripts/output_path.py` 의 `build_output_path()` 로 정확한 경로 빌드
5. **카탈로그 갱신**: `python youtube-math-auto/scripts/regen_index.py output/`
6. **push**: 위 "자동 push" 단계

## 🎯 학습자 수준 가이드 (반드시 적용)

`youtube-math-auto/SKILL.md` 의 "학습자 수준 가이드" 섹션을 본 스킬 호출 시 반드시 전달:

> **대상**: 중수준(하위 40%) 학생도 따라갈 수 있는 호흡.
> 영상에서 강사가 "당연하다"고 생략한 모든 공식·정리·용어를 개념 설명에서 풀어쓸 것. 결과 공식만 제시 ❌, 유도 1번은 반드시 포함. 선수 학습은 1~2문장으로 환기. 풀이 STEP은 한 줄에 한 단계로 분리, 비약 금지.

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

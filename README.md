# YouTube Math Skill — 유튜브 수학 영상 → 학습자료 자동 생성

YouTube 수학 강의 영상의 URL 한 줄로, 학년·단원에 맞춘 인터랙티브 HTML 학습자료(개념 설명 + 수준별 문항 + 풀이)를 자동 생성하는 Claude Code 스킬 모음.

PC뿐 아니라 **Android 폰(Termux)에서도 동일하게 동작**하며, GitHub 레포 + Pages를 통해 모든 기기에서 동일한 자료 카탈로그를 공유합니다.

## 🎯 무엇을 하는가

1. URL 입력 → yt-dlp로 한국어 자막 자동 추출
2. 자막 정제 (슬라이딩 윈도우 중복 제거 + 타임스탬프 정리)
3. 박PM 페르소나 8명이 5단계 워크플로우로 학습자료 제작:
   - STAGE 1 영상분석 → STAGE 2 커리큘럼 설계 → STAGE 3 개념·문항 작성 → STAGE 4 3중 검증 → STAGE 5 HTML 마감
4. **출력**: 단일 .html (KaTeX 수식 + 다크모드 + 난이도 필터 + 인쇄 최적화)
5. **카탈로그**: `output/INDEX.md` (마크다운) + `output/index.html` (썸네일 갤러리, 검색·필터 가능)
6. **중복 감지**: 같은 영상 재처리 시 알림

## 📁 디렉토리 구조

```
.
├── README.md                       ← 이 파일
├── MOBILE_SETUP.md                 ← Android Termux 셋업 가이드
├── requirements.txt                ← Python 의존성 (yt-dlp)
├── youtube-math-auto/              ← Wrapper 스킬 (URL → 학습자료 무인 자동화)
│   ├── SKILL.md
│   └── scripts/
│       ├── fetch_subtitle.py       ← yt-dlp 호출 + VTT 정제
│       ├── vtt_to_text.py          ← VTT → 평문 변환
│       ├── output_path.py          ← 명명 규칙 + 중복 감지
│       └── regen_index.py          ← INDEX.md + index.html 자동 갱신
├── youtube-math-auto.skill         ← 배포용 ZIP (Claude.ai/공유용)
├── scripts/
│   └── package_skill.py            ← 위 ZIP 재패키징
├── subs/                           ← 자막 캐시 (.gitignore됨)
└── output/                         ← 생성된 학습자료
    ├── INDEX.md
    ├── index.html                  ← 갤러리 (GitHub Pages로 공개 가능)
    └── 학년/단원/날짜_주제_id.html
```

## 🖥️ PC 셋업 (Windows / macOS / Linux)

### 사전 요구사항
- Python 3.10+
- Git
- (Claude Code 사용자) Claude Code 설치

### 1회 셋업
```bash
# 레포 받기
git clone <YOUR_REPO_URL>
cd youtube-math-skill

# 의존성 설치
pip install -r requirements.txt

# Claude Code에 스킬 등록 (사용자 레벨)
# Windows (PowerShell):
mkdir $HOME\.claude\skills -Force
xcopy /E /I /Y youtube-math-auto $HOME\.claude\skills\youtube-math-auto

# macOS / Linux:
mkdir -p ~/.claude/skills
ln -sf "$PWD/youtube-math-auto" ~/.claude/skills/youtube-math-auto
```

### 사용
Claude Code에서:
```
이 영상으로 학습자료 만들어줘 https://youtube.com/watch?v=...
```
스킬이 자동 트리거됩니다. 결과는 `output/학년/단원/...html` 에 저장되고 `output/index.html` 갤러리도 자동 갱신.

### 직접 사용 (Claude Code 없이)
```bash
# 자막만 추출
python youtube-math-auto/scripts/fetch_subtitle.py "https://youtube.com/watch?v=..." --out subs/

# 카탈로그 갱신
python youtube-math-auto/scripts/regen_index.py output/
```

## 📱 모바일 (Android Termux)

별도 가이드: [MOBILE_SETUP.md](MOBILE_SETUP.md)

요약:
1. F-Droid에서 Termux 설치
2. `pkg install python git nodejs-lts && pip install yt-dlp`
3. `npm install -g @anthropic-ai/claude-code` (Claude Code 모바일)
4. 이 레포 clone → PC와 동일한 워크플로우

## 🌐 GitHub Pages 갤러리 공개

이 레포의 `output/index.html` 을 GitHub Pages로 공개하면, **모바일 브라우저로 어디서든 자료 갤러리에 즉시 접근** 가능. 학생 공유도 링크 한 줄.

설정:
1. GitHub 레포 → Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, Folder: `/output`
4. Save → 1~2분 후 `https://<your-id>.github.io/<repo-name>/` 에서 갤러리 접근 가능

## 🔄 다중 PC 동기화

모든 PC가 같은 GitHub 레포를 바라보면 자료가 자동으로 통합됩니다:

```bash
# 작업 시작 전
git pull

# 작업 후
git add output/
git commit -m "고2 도함수 자료 추가"
git push
```

## 📚 카탈로그 명명 규칙

```
output/{학년}/{단원}/{YYYYMMDD}_{핵심주제}_{video_id8}.html
```

예시:
- `output/고1/수학Ⅰ-삼각함수의활용/20260505_사인법칙코사인법칙_W9ReLryy.html`
- `output/고3/수학Ⅱ-도함수의활용/20260505_3차함수극값2대1분할_00ByGXdH.html`

학년/단원/주제는 `youtube-math-lesson` 본 스킬의 STAGE 1에서 자동 추출.

## ⚠️ 절대 금지

- 실재하지 않는 기출문제 출처 표기 (예: "2024학년도 9월 모의고사 21번")
  - ✅ 대신: "수능 대비 — 21번 유형(준킬러)"
- 자막/요약 없이 영상 추측 분석
- 진행 중인 라이브 스트림 처리 (자막 미생성)

## 🤝 라이선스 / 출처

영상 출처 URL은 모든 학습자료 헤더에 명시. 자료는 교육 목적의 2차 가공물이며, 학생 배포 전 교사 검토 권장.

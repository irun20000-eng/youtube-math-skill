# 📱 Android Termux 셋업 가이드 — 폰에서 PC와 동일하게 작업

이 가이드를 따라하면 **Android 폰만으로 PC와 100% 동일한 워크플로우**가 가능합니다. 영상을 보다가 URL 던지면 학습자료가 생성되고, GitHub Pages 갤러리에 자동 반영됩니다.

## 왜 Termux 인가?

- **폰의 IP를 사용** → YouTube가 클라우드 IP를 차단해도 폰 IP는 정상 사용자로 인식 → yt-dlp 작동 ✅
- **Linux 환경 그대로** → Python, Git, Node.js, Claude Code 모두 동일하게 설치 가능
- **무료 / 광고 없음** (F-Droid 공식 빌드)

> ⚠️ Google Play 스토어의 Termux는 오래된 버전입니다. **반드시 [F-Droid](https://f-droid.org/)** 또는 [Termux GitHub Releases](https://github.com/termux/termux-app/releases) 에서 설치하세요.

## 셋업 단계 (한 번만)

### 1. Termux 설치 (5분)

1. F-Droid 앱 설치: https://f-droid.org/
2. F-Droid 안에서 "Termux" 검색 → 설치
3. (선택) "Termux:API" 도 설치하면 클립보드 등 폰 기능 연동 가능

### 2. 기본 패키지 설치 (10분)

Termux 첫 실행 후:

```bash
# 패키지 저장소 갱신
pkg update -y && pkg upgrade -y

# 기본 도구
pkg install -y python git nodejs-lts openssh

# yt-dlp 설치
# 주의: Termux에서는 'pip install --upgrade pip' 가 의도적으로 차단됩니다.
# (Termux 자체 패키지 시스템과 충돌 방지) — pip 업그레이드는 건너뛰고 yt-dlp만 설치하세요.
pip install yt-dlp

# 작동 확인
python -m yt_dlp --version
# → 2026.03.17 같은 버전 번호가 나오면 정상
```

> 💡 만약 *"ERROR: Installing pip is forbidden"* 메시지가 보이면 Termux의 정상 동작입니다. yt-dlp 설치만 진행하세요. pip 업그레이드가 필요하면 `pkg upgrade python-pip` 으로 처리.

### 3. 저장 공간 권한 부여

```bash
# Termux에서 폰 저장공간 접근 허용 (팝업 → 허용)
termux-setup-storage
```

### 4. 이 레포 받기 (5분)

```bash
# 홈으로
cd ~

# (옵션 A — HTTPS, 가장 단순)
git clone https://github.com/<YOUR_USER>/<YOUR_REPO>.git youtube-math-skill

# (옵션 B — SSH, 한 번 push 권한 셋업하면 더 편함)
# 키 생성: ssh-keygen -t ed25519
# 공개키를 GitHub Settings → SSH keys 에 등록
# 그 후: git clone git@github.com:<YOUR_USER>/<YOUR_REPO>.git youtube-math-skill

cd youtube-math-skill

# Git 사용자 정보 (1회)
git config --global user.name "<YOUR_NAME>"
git config --global user.email "<YOUR_EMAIL>"
```

### 5. Claude Code 설치 (10분)

```bash
# Claude Code 글로벌 설치
npm install -g @anthropic-ai/claude-code

# 첫 실행 (로그인 안내 따라가기)
claude
```

> 참고: Termux에서 npm 글로벌 설치 시 권한 이슈 있으면 `npm config set prefix ~/.npm-global` 후 `~/.bashrc` 에 `export PATH=~/.npm-global/bin:$PATH` 추가.

### 6. 스킬을 Claude Code 에 등록

```bash
mkdir -p ~/.claude/skills
ln -sf "$HOME/youtube-math-skill/youtube-math-auto" ~/.claude/skills/youtube-math-auto

# 확인
ls ~/.claude/skills/
```

이제 셋업 끝.

## 📲 실제 사용 흐름

YouTube 앱에서 영상을 보다 학습자료를 만들고 싶을 때:

```bash
# Termux 실행

# 1) 다른 PC가 새 자료 만들었을 수 있으니 동기화
cd ~/youtube-math-skill && git pull

# 2) Claude Code 시작
claude

# 3) Claude Code 안에서 한 줄
이 URL로 학습자료 만들어줘 https://youtube.com/watch?v=...
```

(자동) 자막 추출 → 학습자료 생성 → 갤러리 갱신.

```bash
# 4) GitHub로 push (다른 기기와 공유 + Pages 자동 배포)
git add output/
git commit -m "고1 사인법칙 자료 추가"
git push
```

1~2분 후 GitHub Pages가 자동 배포 → 모바일 브라우저에서 갤러리 즉시 확인 → 학생 공유.

## ⚡ 단축 명령 (선택)

자주 쓰는 흐름을 한 줄로 묶고 싶다면 `~/.bashrc` 에 추가:

```bash
# Termux 안에서
cat >> ~/.bashrc << 'EOF'
alias ymsync='cd ~/youtube-math-skill && git pull'
alias ympush='cd ~/youtube-math-skill && git add output/ && git commit -m "Add lesson" && git push'
alias ymclaude='cd ~/youtube-math-skill && git pull && claude'
EOF

source ~/.bashrc
```

이제:
- `ymclaude` → 동기화 + Claude Code 시작
- 작업 후 `ympush` → 결과 푸시

## 🎬 사용 시나리오 예시

**버스에서 EBS 영상 보다가 좋은 강의 발견**

1. YouTube 앱에서 URL 복사
2. Termux 실행 → `ymclaude` 입력
3. Claude Code 안에서: `이 URL로 https://youtu.be/xxx 학습자료 만들어줘`
4. 1~2분 대기 → 학습자료 생성 완료
5. Termux로 돌아가서 `ympush`
6. 도착 후 학생에게 GitHub Pages URL 카톡으로 전송

## ⚠️ 알려진 제약 / 팁

- **배터리**: yt-dlp 자막 추출 30초 + Claude Code 처리 1~3분. 한 번 처리에 약 2~5% 배터리.
- **메모리**: Claude Code는 약 200~500MB 사용. 4GB+ 폰 권장.
- **화면**: 가로 모드 + Termux 폰트 크기 줄이면 코드 보기 한결 편함. (Termux 볼륨↑ + Q → 키보드 보조 메뉴)
- **VPN**: VPN 사용 중이면 yt-dlp가 차단될 수 있음 (해당 IP가 클라우드면). 자막 추출만은 VPN OFF 권장.
- **백그라운드 종료 방지**: 안드로이드 배터리 최적화에서 Termux 제외 설정 권장 (장시간 작업 시).

## 🆘 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `yt-dlp` 명령 없음 | PATH 미설정 | `python -m yt_dlp ...` 로 호출 |
| `git push` 시 인증 실패 | HTTPS 토큰 미설정 | GitHub Personal Access Token 생성 후 password 자리에 입력 |
| 자막 다운로드 실패 (HTTP 429) | 영상 IP 차단 일시적 | 잠시 대기 또는 yt-dlp 업데이트 (`pip install -U yt-dlp`) |
| Claude Code가 스킬 인식 못 함 | 심볼릭 링크 깨짐 | `ls ~/.claude/skills/` 확인 후 다시 ln |
| Termux 종료 후 작업 끊김 | OS가 백그라운드 종료 | Termux 알림 표시 ON + 배터리 최적화 예외 |

## 📚 참고

- 본 스킬 사용 가이드: [README.md](README.md)
- 명명 규칙·스킬 내부 구조: [youtube-math-auto/SKILL.md](youtube-math-auto/SKILL.md)

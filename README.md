# yt-inbox — 유튜브 기초자료(brief) 수신함

이 브랜치는 **코드가 없는 고아(orphan) 브랜치**다. `main` 과 히스토리를 공유하지 않으며,
배포·CI 와 무관하다. 여기에는 **Aside(사용자 PC)가 만든 영상 기초자료**만 쌓인다.

2026-10-15 도입. 구글 스파크(Gemini Spark)가 10월 초 산출을 멈춘 뒤, 스파크가 하던
「영상을 보고 원재료를 만드는 단계」를 Aside 로 대체했다. 클라우드 루틴은 유튜브 자막이
IP 차단되지만 Aside 는 사용자 PC 에서 돌기 때문에 자막을 직접 받을 수 있다.

## 흐름

```
[유튜브 재생목록]  →  [Aside 수집 루틴, 평일 08:30 KST, 사용자 PC]
  보자따라하자            재생목록 읽기 → 처리여부 대조 → 메타+한국어 자막 수집
  일단모아                → 분류(search / math / study_method / general)
                          → 해당 레포 yt-inbox 브랜치 briefs/<video_id>.md 로 커밋·푸시
                                   ↓
[Claude Code 루틴, 클라우드]  git fetch origin yt-inbox → brief 읽기 → 글 작성 → 기존 절차
```

## 파일 규격 — `briefs/<video_id>.md` (schema: yt-brief/v1)

```markdown
---
schema: yt-brief/v1
video_id: 8Oa1_g0hEdA
url: https://www.youtube.com/watch?v=8Oa1_g0hEdA
title: "6개월 걸려 만든 자동화가 이거 하나로 다 필요 없어졌습니다"
channel: "김경원의 AI"
published: 2026-10-08
duration_sec: 302
duration: "5:02"
playlist: 보자따라하자
route: search            # search | math | study_method | general
route_reason: "playlist=보자따라하자"
transcript_lang: ko
transcript_kind: auto    # auto(자동생성) | manual(업로더 자막)
transcript_tracks: "ko(auto)"
transcript_lines: 141
transcript_chars: 4100
collected_at: 2026-10-15T08:30:00+09:00
collector: aside/yt-brief-collector v1
---

## 영상 설명
(설명란 원문 그대로)

## 자막 (ko, 자동생성)
[00:00] 첫 줄
[00:02] 둘째 줄
...
```

- **사실만 담는다. 분석·요약은 넣지 않는다.** 글쓰기는 클라우드 Claude 루틴의 몫이다.
- 제목·채널·게시일·길이는 유튜브가 준 값 그대로다(모델 생성 아님). 단 `duration_sec` 는 플레이어 값이라 Data API(`get_video_details`)와 ±1초 다를 수 있다(2026-10-15 실측 302 vs 303) — **길이는 API 값이 정본**. Search 루틴은 기존대로
  `get_video_details` 로 한 번 더 확인한다.
- 자막은 **자동생성(ASR)일 수 있다** — 고유명사·숫자 오인식이 섞여 있다. 쓰는 쪽은 또렷하지
  않은 제품명·수치를 단정하지 말 것(각 레포 런북의 규칙 그대로).
- 파일은 UTF-8 평문이다. 구글 문서 변환·base64 를 거치지 않으므로 **전사 손상 검사(2회 대조,
  코퍼스 음절 검사)가 필요 없다.**

## 읽는 법 (클라우드 루틴)

```bash
git fetch origin yt-inbox
git ls-tree --name-only origin/yt-inbox briefs/          # 목록
git show origin/yt-inbox:briefs/<video_id>.md > /tmp/brief/<video_id>.md
```

- **처리 여부는 각 레포의 산출물로 판단한다**(노트·학습자료·`_done` 마커 존재). brief 를 지우거나
  옮기지 않는다 — 수신함은 기록으로 남는다. 루틴은 yt-inbox 브랜치에 **쓰지 않는다.**
- 자막이 없는 영상은 brief 를 만들지 않고 Aside 보고에 「수동대기」로만 남긴다(추측 작성 금지).

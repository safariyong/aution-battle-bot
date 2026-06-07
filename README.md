# 🏠 부동산 AI 경매 배틀 — 실전봇

SK하이닉스 장비지능화팀 해커톤

---

## 시작하기

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 이 폴더에 만들고 API 키를 입력하세요:

```
ANTHROPIC_API_KEY=sk-ant-여기에붙여넣기
```

### 3. 팀 번호 설정

`team_bot.py` 상단에서 팀 번호를 수정하세요:

```python
TEAM_ID = "1"   # ← 우리 팀 번호로 변경 (1~9)
```

### 4. 전략 작성

`team_bot_sample.py` 안의 `[전략]` 부분을 우리 팀 전략으로 바꾸세요:

```python
[전략]  ← 이 부분만 수정!
- 팀컬러가 발동되는 매물은 감정가의 95~110%로 공격적으로 입찰
- ...
```

### 5. 봇 실행

```bash
python team_bot_sample.py --team_id 1
```

---

## Claude Code로 전략 짜기

```bash
# 이 폴더에서 실행
claude
```

Claude Code 안에서:
```
claude.md와 team_bot_sample.py를 읽고
우리 팀컬러는 👑 곧죽어도강남이야.
강남 매물 집중 공략 전략으로 [전략] 부분을 수정해줘.
```

---

## 파일 구성

| 파일 | 설명 |
|------|------|
| `team_bot_sample.py` | 팀봇 템플릿 — `[전략]` 부분만 수정 |
| `claude.md` | 게임 규칙 + API 가이드 — Claude Code에 보여주세요 |
| `.env` | API 키 (직접 생성) |

---

## 주의사항

- 모델은 반드시 **claude-haiku-4-5-20251001** 사용 (Sonnet/Opus 금지)
- 입찰은 **1회만** 가능 — 한번 제출하면 수정 불가
- 봇이 꺼져 있으면 **0.01억 자동입찰** 처리됨

---

*심판 서버: https://sk-auction-battle.up.railway.app*

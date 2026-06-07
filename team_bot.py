#!/usr/bin/env python3
# ============================================================
#  team_bot.py — 부동산 AI 경매 배틀 팀봇 템플릿
#
#  [ 시작하기 ]
#  1. .env 파일에 API 키 입력:  ANTHROPIC_API_KEY=sk-ant-...
#  2. 아래 TEAM_ID 수정
#  3. analyze_building() 안의 프롬프트만 수정
#  4. 실행: python team_bot.py --team_id N --team_name "N팀"
#
#  [ 점수 계산 ]
#  최종점수 = Σ(실제낙찰가 × Phase계수 × 팀컬러계수) + 누적월세
#  → 실제낙찰가는 숨겨져 있음! 감정가 보고 전략 판단
#  → 입찰가는 점수에 영향 없음 (싸게 살수록 현금 절약)
# ============================================================

import anthropic
import requests
import time
import json
import os
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(_env_path)
if not os.environ.get("ANTHROPIC_API_KEY"):
    if os.path.exists(_env_path):
        for line in open(_env_path, encoding="utf-8-sig"):
            if line.startswith("ANTHROPIC_API_KEY="):
                os.environ["ANTHROPIC_API_KEY"] = line.strip().split("=", 1)[1]
                break

# ── 설정 ──────────────────────────────────────────────────
SERVER  = "https://sk-auction-battle.up.railway.app"
TEAM_ID = "1"   # ← 팀 번호 입력 (1~9)

client = anthropic.Anthropic()


# ══════════════════════════════════════════════════════════
#  ★ 아래 함수 안의 [전략] 부분만 수정하세요!
# ══════════════════════════════════════════════════════════
def analyze_building(apt_info: dict, my_cash: float, my_score: float,
                     phase: int, item: int, phase_key: dict,
                     active_dev_bonus: bool, all_teams: dict,
                     my_color: dict) -> float:
    """매물 분석 후 입찰가(억원) 반환"""

    # 팀 순위 요약
    teams_summary = "정보 없음"
    if all_teams:
        lines = []
        for i, (tid, t) in enumerate(sorted(all_teams.items(), key=lambda x: x[1].get('score',0), reverse=True)):
            mark = " ← 나" if str(tid) == str(TEAM_ID) else ""
            lines.append(f"  {i+1}위 {t['name']}: 현금 {t.get('cash',0):.1f}억 / 점수 {t.get('score',0):.1f}억{mark}")
        teams_summary = "\n".join(lines)

    gamjeong = apt_info.get('감정가_억') or apt_info.get('감정가', 10)
    try: gamjeong = float(gamjeong)
    except: gamjeong = 10.0

    # ──────────────────────────────────────────────────────
    #  ↓↓↓ 이 prompt 안의 내용을 우리 팀 전략으로 바꾸세요 ↓↓↓
    # ──────────────────────────────────────────────────────
    prompt = f"""
당신은 부동산 경매 전문가입니다.

[현재 상황]
- Phase: {phase}/5  |  매물: {item}/12
- 내 현금: {my_cash}억  |  내 점수: {my_score}억
- 팀컬러: {my_color.get('emoji','')} {my_color.get('name','')} — {my_color.get('desc','')}
- 황금열쇠: {phase_key.get('name','없음')} — {phase_key.get('desc','')}
- 개발호재 보너스: {'ON (+10%)' if active_dev_bonus else 'OFF'}

[매물 정보]
- 위치: {apt_info.get('csv_위치', apt_info.get('loc',''))}
- 면적: {apt_info.get('csv_건물면적', '')}
- 연식: {apt_info.get('csv_아파트년식', '')}
- 감정가: {gamjeong}억
- 신축여부: {'신축(2015년↑)' if apt_info.get('is_new') else '구축'}
- 강남여부: {'강남3구' if apt_info.get('is_gangnam') else '비강남'}
- 개발호재: {apt_info.get('dev','')}

[전략]  ← 이 부분을 우리 팀 전략으로 바꾸세요!
- 팀컬러가 발동되는 매물은 감정가의 95~110%로 공격적으로 입찰
- 팀컬러 미해당 매물은 감정가의 70~80%로 보수적으로 입찰
- 후반 Phase(4~5)일수록 더 공격적으로 입찰
- 현금이 20억 이하면 절약 모드로 전환

[전체 팀 현황]
{teams_summary}

JSON으로만 답하세요:
{{"bid": 입찰가(숫자), "reason": "한줄이유"}}

제약: bid는 0.01 이상 {my_cash} 이하
"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # 하이쿠 고정 (비용 절감)
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        text = text.replace("```json","").replace("```","").strip()
        data = json.loads(text)
        bid = float(data.get("bid", 0))
        reason = data.get("reason", "")
        print(f"  Claude: {bid}억 — {reason}", flush=True)
        return bid
    except Exception as e:
        print(f"  오류: {e} → 감정가 85% 기본입찰", flush=True)
        return round(gamjeong * 0.85, 2)


# ══════════════════════════════════════════════════════════
#  아래는 수정하지 마세요
# ══════════════════════════════════════════════════════════

def get_status() -> dict:
    r = requests.get(f"{SERVER}/bot/status", params={"team_id": TEAM_ID}, timeout=10)
    return r.json()

def get_my_status() -> dict:
    r = requests.get(f"{SERVER}/bot/my_status/{TEAM_ID}", timeout=10)
    return r.json()

def put_bid(price: float) -> dict:
    r = requests.post(f"{SERVER}/put_bid",
        json={"team_id": TEAM_ID, "price": price}, timeout=10)
    return r.json()

def run():
    print(f"\n[{TEAM_ID}팀] 봇 시작!", flush=True)
    print(f"서버: {SERVER} | 팀ID: {TEAM_ID}\n", flush=True)

    last_item = -1
    last_phase = -1
    my_color = {}
    color_fetched = False

    while True:
        try:
            status = get_status()
        except Exception as e:
            print(f"서버 연결 대기중... ({e})", flush=True)
            time.sleep(3)
            continue

        game_status = status.get("status", "")
        phase = status.get("phase", 0)
        item  = status.get("item", 0)
        teams = status.get("teams", {})

        # 팀컬러 1회 조회
        if not color_fetched and status.get('teams'):
            try:
                me = get_my_status()
                my_color = me.get("color", {})
                print(f"팀컬러: {my_color.get('emoji','')} {my_color.get('name','')} — {my_color.get('desc','')}", flush=True)
                color_fetched = True
            except: pass

        # 게임 종료
        if game_status == "finished":
            print("\n게임 종료!", flush=True)
            ranking = sorted(teams.values(), key=lambda t: t.get("score",0), reverse=True)
            for i, t in enumerate(ranking):
                mark = " ← 나" if str(t.get("id")) == str(TEAM_ID) else ""
                print(f"  {i+1}위 {t['name']}: {t['score']:.1f}억{mark}", flush=True)
            break

        # 입찰
        if game_status == "bidding":
            my_team  = teams.get(str(TEAM_ID), {})
            my_cash  = my_team.get("cash", 0)
            my_score = my_team.get("score", 0)
            apt      = status.get("current_apt", {})
            phase_key = status.get("phase_key") or {}
            dev_bonus = status.get("active_dev_bonus", False)
            bids     = status.get("current_bids", {})

            if str(TEAM_ID) in bids:
                time.sleep(1)
                continue

            if apt and (phase != last_phase or item != last_item):
                last_phase = phase
                last_item  = item
                gamjeong = apt.get('감정가_억') or apt.get('감정가', 10)
                try: gamjeong = float(gamjeong)
                except: gamjeong = 10.0

                print(f"\nP{phase}-{item} | {apt.get('name','?')} | 감정가:{gamjeong}억 | 현금:{my_cash}억", flush=True)
                if phase_key:
                    print(f"황금열쇠: {phase_key.get('emoji','')} {phase_key.get('name','')}", flush=True)

                bid = analyze_building(
                    apt, my_cash, my_score,
                    phase, item, phase_key, dev_bonus,
                    teams, my_color
                )
                bid = max(0.01, min(round(bid, 2), my_cash))
                result = put_bid(bid)
                if result.get("ok"):
                    print(f"  입찰완료: {bid}억 (잔여: {result.get('cash',0):.1f}억)", flush=True)
                else:
                    print(f"  입찰실패: {result.get('msg')}", flush=True)

        time.sleep(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--team_id",   default=TEAM_ID)
    parser.add_argument("--server",    default=SERVER)
    args, _ = parser.parse_known_args()
    TEAM_ID   = args.team_id
    SERVER    = args.server
    run()

"""GitHub Actions 用：境外 runner 直连币安/Polymarket 扫描五大联赛强队赛程，写 schedule.json。
有 BINANCE_API_KEY/SECRET 环境变量就用币安（与挂单口径一致），否则用 Polymarket 公开数据。
"""
import hashlib
import hmac
import json
import math
import os
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests

from teams_zh import zh_team, zh_title
import strength

HORIZON_H = 72
WATCH_PROB = 0.70
TIERS = [  # 临界值取高
    {"min_prob": 0.85, "discount": 0.90, "position_pct": 0.11},
    {"min_prob": 0.80, "discount": 0.85, "position_pct": 0.10},
    {"min_prob": 0.75, "discount": 0.80, "position_pct": 0.09},
]
SLUG_LEAGUE = {"epl": "英超", "lal": "西甲", "bun": "德甲", "sea": "意甲", "fl1": "法甲"}
TEAM_RE = re.compile(r"Will (.+?) win on")


def to_row(league, title, team, prob, start_iso, tick=0.01):
    tier = next((t for t in TIERS if prob >= t["min_prob"]), None)
    home, away = strength.split_teams(title)
    rg = strength.rank_gap(league, home, away) if home and away else None
    return {
        "league": league, "title": title, "title_zh": zh_title(title),
        "team": team, "team_zh": zh_team(team),
        "prob": round(prob, 4), "start": start_iso,
        "rank_gap": rg[2] if rg else None,
        "rank_pair": f"{rg[0]} vs {rg[1]}" if rg else "-",
                "rank_ratio": round(rg[1] / rg[0], 1) if rg else None,
        "discount": tier["discount"] if tier else None,
        "position_pct": tier["position_pct"] if tier else None,
        "limit_price": round(int(prob * tier["discount"] / tick) * tick, 4) if tier else None,
    }


# ---------------- 币安（需 secrets） ----------------
def scan_binance(key, secret):
    base = "https://api.binance.com/sapi/v1/w3w/wallet/prediction"

    def signed_get(path, **params):
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = 5000
        qs = urlencode(params)
        params["signature"] = hmac.new(secret.encode(), qs.encode(), hashlib.sha256).hexdigest()
        r = requests.get(base + path, params=params,
                         headers={"X-MBX-APIKEY": key}, timeout=20)
        return r.json()

    now = datetime.now(timezone.utc)
    horizon = now + timedelta(hours=HORIZON_H)
    topics, offset = [], 0
    while True:
        resp = signed_get("/market/list", l1Category="sports", l2Category="soccer",
                          sortBy="END_DATE", orderBy="ASC", offset=offset, limit=100)
        batch = resp.get("marketTopics", [])
        topics.extend(batch)
        if not resp.get("hasMore") or not batch:
            break
        offset += len(batch)

    rows = []
    for tp in topics:
        if (tp.get("variantData") or {}).get("type") != "SPORTS_MATCH":
            continue
        league = SLUG_LEAGUE.get((tp.get("slug") or "").split("-")[0])
        if not league or not tp.get("startDate"):
            continue
        start = datetime.fromtimestamp(tp["startDate"] / 1000, tz=timezone.utc)
        if start <= now or start > horizon:
            continue
        for m in tp.get("markets", []):
            if m.get("tradingStatus") != "OPEN":
                continue
            if (m.get("title") or "").strip().lower() == "draw":
                continue
            mt = TEAM_RE.search(m.get("question") or "")
            team = mt.group(1) if mt else (m.get("title") or "")
            yes = next((o for o in m.get("outcomes", [])
                        if (o.get("name") or "").lower() == "yes"), None)
            if not yes:
                continue
            prob = float(yes.get("chance") or yes.get("price") or 0)
            if prob > WATCH_PROB:
                tick = 10 ** -int(m.get("decimalPrecision", 2))
                rows.append(to_row(league, tp["title"], team, prob,
                                   start.isoformat(), tick))
    return rows


# ---------------- Polymarket 兜底（公开数据，无需 key） ----------------
def scan_polymarket():
    series = {"10188": "英超", "10193": "西甲", "10194": "德甲",
              "10195": "法甲", "10203": "意甲"}
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(hours=HORIZON_H)
    rows = []
    for sid, league in series.items():
        r = requests.get("https://gamma-api.polymarket.com/events",
                         params={"series_id": sid, "closed": "false",
                                 "active": "true", "limit": 200}, timeout=20)
        for ev in r.json():
            title = ev.get("title", "")
            if " vs. " not in title or " - " in title:
                continue
            for m in ev.get("markets", []):
                if m.get("sportsMarketType") != "moneyline" or m.get("closed"):
                    continue
                if "draw" in (m.get("groupItemTitle") or "").lower():
                    continue
                start_s = m.get("gameStartTime") or m.get("endDate")
                if not start_s:
                    continue
                start = datetime.fromisoformat(start_s.replace("Z", "+00:00")
                                               .replace("+00", "+00:00")
                                               if "+" not in start_s else start_s)
                if start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)
                if start <= now or start > horizon:
                    continue
                try:
                    prices = json.loads(m.get("outcomePrices") or "[]")
                    outcomes = json.loads(m.get("outcomes") or "[]")
                    prob = float(prices[outcomes.index("Yes")])
                except (ValueError, TypeError, IndexError):
                    continue
                team = m.get("groupItemTitle") or ""
                if team and prob > WATCH_PROB:
                    tick = float(m.get("orderPriceMinTickSize") or 0.01)
                    rows.append(to_row(league, title, team, prob,
                                       start.isoformat(), tick))
    return rows


def main():
    key, secret = os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_API_SECRET")
    source = "币安预测市场"
    rows = []
    try:
        if key and secret:
            rows = scan_binance(key, secret)
            if not rows:
                # 币安对 runner 所在地区（美国）可能返回空数据 → 主动回落
                raise RuntimeError("币安返回 0 场（地区限制）")
        else:
            raise RuntimeError("no secrets")
    except Exception as e:
        print("币安扫描失败，回落 Polymarket:", e)
        rows = scan_polymarket()
        source = "Polymarket（公开数据）"

    # 每场只留最强队
    best = {}
    for r in rows:
        if r["title"] not in best or r["prob"] > best[r["title"]]["prob"]:
            best[r["title"]] = r
    rows = sorted(best.values(), key=lambda r: r["start"])

    now_cn = datetime.now(timezone.utc) + timedelta(hours=8)
    out = {"updated": now_cn.strftime("%Y-%m-%d %H:%M:%S") + " (北京时间)",
           "source": f"GitHub Actions 自动更新（{source}）",
           "schedule": rows}
    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"schedule.json: {len(rows)} 场 | {source}")


if __name__ == "__main__":
    main()

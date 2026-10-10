"""尾盘观察清单构建：今日赛程 × 实时比分 × 触发信号 → 看板/线上展示。"""
import strength
from teams_zh import zh_team

# 规范化队名 → 中文（从 teams_zh 反向构建）
from teams_zh import TEAM_ZH

_NORM_ZH = {strength._norm(k): v for k, v in TEAM_ZH.items()}


def zh_of_norm(norm_name: str) -> str:
    aliased = strength.ALIAS.get(norm_name, norm_name)
    if aliased in _NORM_ZH:
        return _NORM_ZH[aliased]
    if norm_name in _NORM_ZH:
        return _NORM_ZH[norm_name]
    return norm_name.title()


def _live_for(title: str, league: str, live: list):
    home, away = strength.split_teams(title)
    if not home:
        return None
    for g in live:
        if g["league"] != league:
            continue
        names = (g["home"]["name"], g["away"]["name"])
        home_ok = any(strength.teams_match(home, n) for n in names)
        away_ok = any(strength.teams_match(away, n) for n in names)
        if home_ok and away_ok:
            return g
    return None


def _signal_for(title: str, signals: dict):
    home, away = strength.split_teams(title)
    if not home:
        return None
    for espn_name, sig in signals.items():
        parts = espn_name.split(" at ")
        if len(parts) != 2:
            continue
        away_e, home_e = parts[0], parts[1]
        home_ok = strength.teams_match(home, home_e) or strength.teams_match(home, away_e)
        away_ok = strength.teams_match(away, home_e) or strength.teams_match(away, away_e)
        if home_ok and away_ok:
            return sig
    return None


def build_watchlist(schedule: list, live: list, signals: dict, cfg: dict) -> list:
    thresholds = cfg.get("inplay_min_rank_gap", {})
    from_min = cfg.get("inplay_from_minute", 80)
    min_lead = cfg.get("inplay_min_lead", 3)
    out = []
    for r in schedule:
        th = thresholds.get(r["league"], 10)
        gap = r.get("rank_gap")
        watching = gap is not None and gap >= th
        g = _live_for(r["title"], r["league"], live) if live else None
        sig = _signal_for(r["title"], signals) if signals else None
        live_txt = None
        if g:
            live_txt = f"{g['home']['score']}:{g['away']['score']} {g['minute']}'"
        out.append({
            "league": r["league"], "title_zh": r.get("title_zh") or r["title"],
            "start": r.get("start", ""), "prob": r.get("prob"),
            "rank_gap": gap, "threshold": th, "watching": watching,
            "live": live_txt,
            "signal": sig["result"] if sig else None,
            "signal_detail": sig.get("detail") if sig else None,
            "rule": f"≥{min_lead}球 & ≥{from_min}' & 差≥{th}位",
        })
    out.sort(key=lambda x: x["start"] or "")
    return out


def build_standings() -> dict:
    """融合积分榜 → {联赛: [{rank, zh, score}]}，用于网页展示。"""
    try:
        d = strength._load()
    except Exception:
        return {}
    out = {}
    for league, table in d.get("table", {}).items():
        rows = sorted(table.items(), key=lambda x: x[1]["rank"])
        out[league] = [{"rank": v["rank"], "team": zh_of_norm(t), "score": v["score"]}
                       for t, v in rows]
    return {"updated": d.get("updated", ""), "leagues": out}

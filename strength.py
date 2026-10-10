"""球队实力排名模块：ESPN 积分榜（本赛季 + 上赛季按场次加权融合），国内直连无需代理。
融合公式：blended_ppg = (本赛季积分 + 上赛季场均分 × K) / (本赛季场次 + K)，K=15。
赛季初上赛季权重高，赛季深入后本赛季权重自然升高——平滑吸收转会/伤病影响。
缓存 strength.json，每天刷新一次。
"""
import json
import logging
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import requests

log = logging.getLogger("strength")

# ESPN 国内直连可用；trust_env=False 防止 requests 读 Windows 注册表里的系统代理（走代理反而被 ESPN 拒）
_SESSION = requests.Session()
_SESSION.trust_env = False
_SESSION.headers.update({"User-Agent": "Mozilla/5.0"})

BASE = Path(__file__).parent
CACHE = BASE / "strength.json"
K = 15          # 上赛季先验的等效场次
PRIOR_W = 0.6   # 上赛季场均分再打 6 折（阵容会变，不能完全等同）

# 联赛映射：scanner 的联赛名 → ESPN 代码
LEAGUE_ESPN = {"英超": "eng.1", "西甲": "esp.1", "德甲": "ger.1",
               "意甲": "ita.1", "法甲": "fra.1"}

_STRIP = re.compile(r"\b(fc|cf|cfc|acf|afc|sc|ac|as|ss|us|sv|tsv|ssc|rc|rcd|ud|ogc|sco|bc|calcio|1909|1913|1901|05|07|04|1\.)\b")


def _norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c))  # 去音调 Mü→Mu
    s = s.lower().replace("&", "and")
    s = _STRIP.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


# 难以自动匹配的手工别名（左边=市场队名 norm 后的关键部分，右边=ESPN 名的 norm）
ALIAS = {
    "bayern munchen": "bayern munich",
    "tsg hoffenheim": "hoffenheim",   # ESPN 全称 → 词表简称
    "hamburg": "hamburger",           # ESPN "Hamburg SV" → 词表 "Hamburger SV"
    "internazionale milano": "inter",
    "inter milan": "inter",          # ESPN 叫法
    "internazionale": "inter",      # ESPN 积分榜简称
    "paris saint-germain": "paris saint-germain",
    "paris": "paris",   # Paris FC — 注意别匹配到 PSG（下方用最长匹配优先规避）
    "bayer leverkusen": "bayer leverkusen",
    "borussia monchengladbach": "borussia monchengladbach",
    "tottenham hotspur": "tottenham",
    "wolverhampton wanderers": "wolves",
    "stade rennais": "rennes",
    "club atletico de madrid": "atletico madrid",
    "real sociedad de futbol": "real sociedad",
    "rayo vallecano de madrid": "rayo vallecano",
    "real betis balompie": "real betis",
    "rc celta de vigo": "celta vigo",
    "rc deportivo a coruna": "deportivo la coruna",
    "stade brestois": "brest",
    "olympique de marseille": "marseille",
    "olympique lyonnais": "lyon",
    "brighton and hove albion": "brighton",
    "tsg 1899 hoffenheim": "hoffenheim",
    "fsv mainz": "mainz",
    "union berlin": "union berlin",
    "sv elversberg": "elversberg",
    "fc koln": "fc koln",
    "parma": "parma",
    "bologna": "bologna",
    "hellas verona": "hellas verona",
}


def _fetch(league_code: str, season: int) -> dict:
    """返回 {规范化队名: (积分, 场次)}"""
    url = f"https://site.api.espn.com/apis/v2/sports/soccer/{league_code}/standings"
    r = _SESSION.get(url, params={"season": season}, timeout=20)
    r.raise_for_status()
    out = {}
    for child in r.json().get("children", []):
        for e in child.get("standings", {}).get("entries", []):
            stats = {s["name"]: s.get("value") for s in e.get("stats", [])}
            pts, gp = stats.get("points"), stats.get("gamesPlayed")
            if pts is not None and gp:
                logos = e["team"].get("logos") or []
                out[_norm(e["team"]["displayName"])] = {
                    "pts": float(pts), "gp": float(gp),
                    "logo": logos[0].get("href", "") if logos else "",
                }
    return out


def refresh() -> dict:
    """拉全部五个联赛，本赛季+上赛季融合，按融合分排名。返回并写缓存。"""
    now = datetime.now()
    # ESPN season 参数 = 赛季开始年（如 2026 = 2026-27 赛季）；10 月属新赛季
    cur_season = now.year if now.month >= 7 else now.year - 1
    table = {}
    for league, code in LEAGUE_ESPN.items():
        try:
            cur = _fetch(code, cur_season)
            prev = _fetch(code, cur_season - 1)
        except Exception as e:
            log.warning("[%s] 积分榜拉取失败: %s", league, e)
            continue
        blended = {}
        logos = {}
        for team in set(cur) | set(prev):
            c = cur.get(team)
            p = prev.get(team)
            cp, cg = (c["pts"], c["gp"]) if c else (None, 0)
            pp, pg = (p["pts"], p["gp"]) if p else (None, 0)
            logo = (c or p or {}).get("logo", "")
            if logo:
                logos[team] = logo
            prev_ppg = (pp / pg) * PRIOR_W if pg else 1.0 * PRIOR_W  # 升班马按场均1分算
            if cg:
                blended[team] = (cp + prev_ppg * K) / (cg + K)
            else:
                blended[team] = prev_ppg
        ranked = sorted(blended, key=lambda t: -blended[t])
        table[league] = {t: {"rank": i + 1, "score": round(blended[t], 3),
                             "logo": logos.get(t, "")}
                         for i, t in enumerate(ranked)}
    data = {"updated": now.strftime("%Y-%m-%d %H:%M"), "table": table}
    CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("积分榜已刷新: %s", {k: len(v) for k, v in table.items()})
    return data


def _load() -> dict:
    if CACHE.exists():
        try:
            d = json.loads(CACHE.read_text(encoding="utf-8"))
            if d.get("updated", "")[:10] == datetime.now().strftime("%Y-%m-%d"):
                return d
        except (ValueError, OSError):
            pass
    return refresh()


def _match_team(league_table: dict, name: str):
    """市场队名 → 积分榜里的条目。精确→别名→包含→词重合，最长者优先。"""
    n = _norm(name)
    if n in league_table:
        return league_table[n]
    aliased = ALIAS.get(n, n)
    if aliased in league_table:
        return league_table[aliased]
    # 包含匹配（双向），最长键优先，避免 paris 误中 paris saint-germain
    for key in sorted(league_table, key=len, reverse=True):
        if key and (key in n or n in key):
            return league_table[key]
    # 词重合 ≥2
    ntok = set(n.split())
    best, best_n = None, 0
    for key in league_table:
        shared = len(ntok & set(key.split()))
        if shared > best_n:
            best, best_n = league_table[key], shared
    return best if best_n >= 2 else None


def rank_of(league: str, team: str):
    """单队查询，返回 {rank, score, logo} 或 None。"""
    d = _load()
    table = d.get("table", {}).get(league)
    if not table:
        return None
    return _match_team(table, team)


def rank_gap(league: str, team_a: str, team_b: str):
    """返回 (强队排名, 弱队排名, 排名差)；任一匹配不上返回 None。"""
    d = _load()
    table = d.get("table", {}).get(league)
    if not table:
        return None
    a = _match_team(table, team_a)
    b = _match_team(table, team_b)
    if not a or not b:
        log.warning("排名匹配失败: %s / %s (%s)", team_a, team_b, league)
        return None
    gap = b["rank"] - a["rank"]  # a 应是强队（排名数字小）
    return (a["rank"], b["rank"], gap) if gap > 0 else (b["rank"], a["rank"], -gap)


def split_teams(title: str):
    """'A vs. B' / 'A vs B' → (A, B)"""
    t = re.split(r"\s+vs\.?\s+", title or "")
    return (t[0], t[1]) if len(t) == 2 else (None, None)


def teams_match(name_a: str, name_b: str) -> bool:
    """跨数据源的队名匹配（ESPN 'Bayern Munich' vs 币安 'FC Bayern München'）。
    规范化 + 别名 + 双向包含 + 词重合（≥2 词或 ≥5 字母特征词）。"""
    a = ALIAS.get(_norm(name_a), _norm(name_a))
    b = ALIAS.get(_norm(name_b), _norm(name_b))
    if not a or not b:
        return False
    if a == b:
        return True
    if a in b or b in a:
        # 排除纯首词前缀误伤：Paris FC(paris) 不能匹配 Paris Saint-Germain
        shorter, longer = (a, b) if len(a) < len(b) else (b, a)
        if shorter == longer.split()[0]:
            return False
        return True
    shared = set(a.split()) & set(b.split())
    if len(shared) >= 2:
        return True
    return bool(shared) and max(len(w) for w in shared) >= 5
    return (t[0], t[1]) if len(t) == 2 else (None, None)

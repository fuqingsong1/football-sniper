"""足球队名 英→中 翻译表（五大联赛 + 欧战常见球队）。
用于看板和线上网页展示。未收录的队名保留原文。
"""

TEAM_ZH = {
    # 英超
    "Arsenal FC": "阿森纳", "Arsenal": "阿森纳",
    "Manchester City FC": "曼城", "Manchester City": "曼城",
    "Manchester United FC": "曼联", "Manchester United": "曼联",
    "Liverpool FC": "利物浦", "Liverpool": "利物浦",
    "Chelsea FC": "切尔西", "Chelsea": "切尔西",
    "Tottenham Hotspur FC": "热刺", "Tottenham Hotspur": "热刺", "Tottenham": "热刺",
    "Newcastle United FC": "纽卡斯尔", "Newcastle United": "纽卡斯尔",
    "Aston Villa FC": "阿斯顿维拉", "Aston Villa": "阿斯顿维拉",
    "Brighton & Hove Albion FC": "布莱顿", "Brighton & Hove Albion": "布莱顿",
    "West Ham United FC": "西汉姆联", "West Ham United": "西汉姆联",
    "Crystal Palace FC": "水晶宫", "Crystal Palace": "水晶宫",
    "Everton FC": "埃弗顿", "Everton": "埃弗顿",
    "Fulham FC": "富勒姆", "Fulham": "富勒姆",
    "Brentford FC": "布伦特福德", "Brentford": "布伦特福德",
    "Nottingham Forest FC": "诺丁汉森林", "Nottingham Forest": "诺丁汉森林",
    "AFC Bournemouth": "伯恩茅斯", "Bournemouth": "伯恩茅斯",
    "Wolverhampton Wanderers FC": "狼队", "Wolves": "狼队",
    "Leeds United FC": "利兹联", "Leeds United": "利兹联",
    "Sunderland AFC": "桑德兰", "Sunderland": "桑德兰",
    "Ipswich Town FC": "伊普斯维奇", "Ipswich Town": "伊普斯维奇",
    "Leicester City FC": "莱斯特城", "Hull City AFC": "赫尔城",
    "Burnley FC": "伯恩利", "Burnley": "伯恩利",
    # 西甲
    "Real Madrid CF": "皇家马德里", "Real Madrid": "皇家马德里",
    "FC Barcelona": "巴塞罗那", "Barcelona": "巴塞罗那",
    "Club Atlético de Madrid": "马德里竞技", "Atlético Madrid": "马德里竞技", "Atletico Madrid": "马德里竞技",
    "Athletic Club": "毕尔巴鄂竞技", "Athletic Bilbao": "毕尔巴鄂竞技",
    "Real Sociedad de Fútbol": "皇家社会", "Real Sociedad": "皇家社会",
    "Villarreal CF": "比利亚雷亚尔", "Villarreal": "比利亚雷亚尔",
    "Real Betis Balompié": "皇家贝蒂斯", "Real Betis": "皇家贝蒂斯",
    "Sevilla FC": "塞维利亚", "Sevilla": "塞维利亚",
    "Valencia CF": "瓦伦西亚", "Valencia": "瓦伦西亚",
    "Getafe CF": "赫塔菲", "Getafe": "赫塔菲",
    "Girona FC": "赫罗纳", "Girona": "赫罗纳",
    "RC Celta de Vigo": "塞尔塔", "Celta Vigo": "塞尔塔",
    "CA Osasuna": "奥萨苏纳", "Osasuna": "奥萨苏纳",
    "Rayo Vallecano de Madrid": "巴列卡诺", "Rayo Vallecano": "巴列卡诺",
    "Deportivo Alavés": "阿拉维斯", "Alaves": "阿拉维斯",
    "RCD Espanyol": "西班牙人", "Espanyol": "西班牙人",
    "Elche CF": "埃尔切", "RCD Mallorca": "马略卡", "Levante UD": "莱万特",
    "RC Deportivo A Coruña": "拉科鲁尼亚", "Real Racing Club": "桑坦德竞技",
    "Real Oviedo": "奥维耶多", "UD Las Palmas": "拉斯帕尔马斯",
    # 德甲
    "FC Bayern München": "拜仁慕尼黑", "Bayern Munich": "拜仁慕尼黑", "Bayern München": "拜仁慕尼黑",
    "Borussia Dortmund": "多特蒙德",
    "Bayer 04 Leverkusen": "勒沃库森", "Bayer Leverkusen": "勒沃库森",
    "RB Leipzig": "莱比锡红牛",
    "Eintracht Frankfurt": "法兰克福",
    "VfB Stuttgart": "斯图加特",
    "VfL Wolfsburg": "沃尔夫斯堡",
    "Borussia Mönchengladbach": "门兴",
    "SC Freiburg": "弗赖堡",
    "TSG 1899 Hoffenheim": "霍芬海姆", "Hoffenheim": "霍芬海姆",
    "1. FSV Mainz 05": "美因茨", "Mainz 05": "美因茨",
    "1. FC Union Berlin": "柏林联合", "Union Berlin": "柏林联合",
    "FC Augsburg": "奥格斯堡", "Augsburg": "奥格斯堡",
    "1. FC Köln": "科隆", "FC Köln": "科隆",
    "SV Werder Bremen": "云达不莱梅", "Werder Bremen": "云达不莱梅",
    "VfL Bochum": "波鸿", "FC St. Pauli": "圣保利",
    "1. FC Heidenheim": "海登海姆", "Hamburger SV": "汉堡",
    "FC Schalke 04": "沙尔克04", "SC Paderborn 07": "帕德博恩",
    "SV 07 Elversberg": "埃尔弗斯贝格",
    # 意甲
    "FC Internazionale Milano": "国际米兰", "Inter Milan": "国际米兰", "Inter": "国际米兰",
    "AC Milan": "AC米兰", "Milan": "AC米兰",
    "Juventus FC": "尤文图斯", "Juventus": "尤文图斯",
    "SSC Napoli": "那不勒斯", "Napoli": "那不勒斯",
    "AS Roma": "罗马", "Roma": "罗马",
    "SS Lazio": "拉齐奥", "Lazio": "拉齐奥",
    "Atalanta BC": "亚特兰大", "Atalanta": "亚特兰大",
    "ACF Fiorentina": "佛罗伦萨", "Fiorentina": "佛罗伦萨",
    "Bologna FC 1909": "博洛尼亚", "Bologna": "博洛尼亚",
    "Torino FC": "都灵", "Torino": "都灵",
    "Como 1907": "科莫", "Como": "科莫",
    "Parma Calcio 1913": "帕尔马", "Parma": "帕尔马",
    "Genoa CFC": "热那亚", "Genoa": "热那亚",
    "US Lecce": "莱切", "Lecce": "莱切",
    "Venezia FC": "威尼斯", "Venezia": "威尼斯",
    "Udinese Calcio": "乌迪内斯", "Cagliari Calcio": "卡利亚里",
    "Hellas Verona FC": "维罗纳", "Empoli FC": "恩波利",
    "AC Monza": "蒙扎", "Monza": "蒙扎",
    "US Sassuolo Calcio": "萨索洛", "Sassuolo": "萨索洛",
    "Frosinone Calcio": "弗罗西诺内", "US Salernitana": "萨勒尼塔纳",
    # 法甲
    "Paris Saint-Germain FC": "巴黎圣日耳曼", "Paris Saint-Germain": "巴黎圣日耳曼", "PSG": "巴黎圣日耳曼",
    "Olympique de Marseille": "马赛", "Marseille": "马赛",
    "Olympique Lyonnais": "里昂", "Lyon": "里昂",
    "AS Monaco FC": "摩纳哥", "AS Monaco": "摩纳哥", "Monaco": "摩纳哥",
    "LOSC Lille": "里尔", "Lille OSC": "里尔", "Lille": "里尔",
    "OGC Nice": "尼斯", "Nice": "尼斯",
    "Stade Rennais FC 1901": "雷恩", "Stade Rennais": "雷恩", "Rennes": "雷恩",
    "RC Strasbourg Alsace": "斯特拉斯堡", "Strasbourg": "斯特拉斯堡",
    "RC Lens": "朗斯", "Lens": "朗斯",
    "FC Nantes": "南特", "Nantes": "南特",
    "Stade Brestois 29": "布雷斯特", "Brest": "布雷斯特",
    "Toulouse FC": "图卢兹", "Toulouse": "图卢兹",
    "AJ Auxerre": "欧塞尔", "Auxerre": "欧塞尔",
    "Le Havre AC": "勒阿弗尔", "Le Havre": "勒阿弗尔",
    "Angers SCO": "昂热", "Angers": "昂热",
    "FC Lorient": "洛里昂", "Paris FC": "巴黎FC",
    "ES Troyes AC": "特鲁瓦", "Le Mans FC": "勒芒",
    "Montpellier HSC": "蒙彼利埃", "AS Saint-Étienne": "圣埃蒂安",
    # 欧战常见
    "Sabah FK": "萨巴赫", "SK Slavia Praha": "布拉格斯拉维亚",
    "Feyenoord": "费耶诺德", "AFC Ajax": "阿贾克斯", "Ajax": "阿贾克斯",
    "SL Benfica": "本菲卡", "FC Porto": "波尔图", "Sporting CP": "葡萄牙体育",
    "Celtic FC": "凯尔特人", "Rangers FC": "流浪者",
    "Galatasaray": "加拉塔萨雷", "Fenerbahçe": "费内巴切",
    "Club Brugge": "布鲁日", "Celtic": "凯尔特人",
}

_TEAM_KEYS = sorted(TEAM_ZH.keys(), key=len, reverse=True)


def zh_team(name: str) -> str:
    """队名翻译成中文，未收录返回原文。"""
    return TEAM_ZH.get((name or "").strip(), name)


def zh_title(title: str) -> str:
    """把 'Arsenal FC vs. Leeds United FC' 里的队名替换成中文。"""
    if not title:
        return title
    out = title
    for k in _TEAM_KEYS:
        if k in out:
            out = out.replace(k, TEAM_ZH[k])
    return out.replace(" vs. ", " vs ")

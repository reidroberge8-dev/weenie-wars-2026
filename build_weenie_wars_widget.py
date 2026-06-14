"""
Weenie Wars 2026 — Widget Build Script
Run:  python3 build_weenie_wars_widget.py
Out:  WeeniesWars_2026.html  (same folder)

DATA SOURCE
  Google Sheet: https://docs.google.com/spreadsheets/d/1-NezoEWSZpeUIZem89ZMltE-kGX_P11LqKVoAwSG0gU/edit?gid=1814658863
  Export CSV:   https://docs.google.com/spreadsheets/d/1-NezoEWSZpeUIZem89ZMltE-kGX_P11LqKVoAwSG0gU/export?format=csv&gid=1814658863
  Columns:      Timestamp, Name, Weenies Consumed
  Note:         "John" in sheet = "Jon" in widget

UPDATE GUIDE
Each month:
  1. Fetch the CSV export URL above to get raw entries
  2. Sum per player per month (month = May if month==5, June if month==6, etc.)
  3. L7 = entries within last 7 days from today
  4. Update player scores in PLAYERS list (may, june, july, aug, sep fields)
  2. Update l7 = weenies in last 7 days for each player
  3. Recalculate chomp (see CHOMP+ formula below)
  4. Update odds + move direction ("▲" lengthened / "▼" shortened)
  5. Update months list: set status = "complete" / "inprogress" / "upcoming"
  6. Update banner stats (leader name, l7 leader, months complete)
  7. Update narrative text
  8. Update footer date

CHOMP+ Formula
  league_avg = sum(all totals) / num_players
  chomp = round((player_total / league_avg) * 100)   # 0 if total == 0
  League avg = 100 by definition.

P2J Formula
  p2j = round(player_total / JOEY_COUNT * 100, 1)    # % to Joey's benchmark
  Computed dynamically — no need to store in PLAYERS.

Betting Odds
  American format. Calibrate so total implied probability ≈ 110-115% (10-15% vig).
  Implied prob from odds:
    negative: (-odds) / (-odds + 100)
    positive: 100 / (odds + 100)
"""

import os

from datetime import datetime as _dt
# ─── DATA ────────────────────────────────────────────────────────────────────

PLAYERS = [
    # name       place  total  may  june  july  aug  sep   l7  chomp    odds    move   mc
    {"name":"Alex",    "place":1, "total":11,"may":5,"june":6,"july":0,"aug":0,"sep":0,"l7":5, "chomp":283,"odds":"+550","move":"—","mc":"#7a8aaa"},
    {"name":"Tom",     "place":2, "total":14,"may":1,"june":13,"july":0,"aug":0,"sep":0,"l7":8, "chomp":361,"odds":"+400","move":"—","mc":"#7a8aaa"},
    {"name":"Jake",    "place":2, "total":4,"may":3,"june":1,"july":0,"aug":0,"sep":0,"l7":1, "chomp":103,"odds":"+1550","move":"—","mc":"#7a8aaa"},
    {"name":"Nick",    "place":2, "total":6,"may":0,"june":6,"july":0,"aug":0,"sep":0,"l7":1, "chomp":155,"odds":"+1050","move":"—","mc":"#7a8aaa"},
    {"name":"Jess",    "place":5, "total":4,"may":2,"june":2,"july":0,"aug":0,"sep":0,"l7":1, "chomp":103,"odds":"+1550","move":"—","mc":"#7a8aaa"},
    {"name":"Scott",   "place":5, "total":5,"may":2,"june":3,"july":0,"aug":0,"sep":0,"l7":3, "chomp":129,"odds":"+1250","move":"—","mc":"#7a8aaa"},
    {"name":"Leah",    "place":5, "total":3,"may":2,"june":1,"july":0,"aug":0,"sep":0,"l7":1, "chomp":77,"odds":"+2050","move":"—","mc":"#7a8aaa"},
    {"name":"Jon",     "place":8, "total":12,"may":1,"june":11,"july":0,"aug":0,"sep":0,"l7":8, "chomp":309,"odds":"+500","move":"—","mc":"#7a8aaa"},
    {"name":"Alyssa",  "place":9, "total":0,"may":0,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":0,"odds":"+14800","move":"—","mc":"#7a8aaa"},
    {"name":"Noel",    "place":9, "total":2,"may":0,"june":2,"july":0,"aug":0,"sep":0,"l7":1, "chomp":52,"odds":"+2900","move":"—","mc":"#7a8aaa"},
    {"name":"Kristen", "place":9, "total":1,"may":0,"june":1,"july":0,"aug":0,"sep":0,"l7":0, "chomp":26,"odds":"+4850","move":"—","mc":"#7a8aaa"},
    {"name":"Reid",    "place":9, "total":2,"may":0,"june":2,"july":0,"aug":0,"sep":0,"l7":0, "chomp":52,"odds":"+2900","move":"—","mc":"#7a8aaa"},
    {"name":"Jen",     "place":9, "total":0,"may":0,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":0,"odds":"+14800","move":"—","mc":"#7a8aaa"},
    {"name":"Devin",   "place":9, "total":2,"may":0,"june":2,"july":0,"aug":0,"sep":0,"l7":2, "chomp":52,"odds":"+2900","move":"—","mc":"#7a8aaa"},
    {"name":"Steph",   "place":9, "total":0,"may":0,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":0,"odds":"+14800","move":"—","mc":"#7a8aaa"},
    {"name":"Harrison", "place":9, "total":0,"may":0,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":0,"odds":"+14800","move":"—","mc":"#7a8aaa"},
    {"name":"Owen",    "place":9, "total":0,"may":0,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":0,"odds":"+14800","move":"—","mc":"#7a8aaa"},
]

MONTHS = [
    # name         key       status: "complete" | "inprogress" | "upcoming"
    {"name":"May",       "key":"may",  "status":"complete"},
    {"name":"June",      "key":"june", "status":"inprogress"},
    {"name":"July",      "key":"july", "status":"upcoming"},
    {"name":"August",    "key":"aug",  "status":"upcoming"},
    {"name":"September", "key":"sep",  "status":"upcoming"},
]

# ─── BANNER ──────────────────────────────────────────────────────────────────
# Update these manually each refresh

BANNER = {
    "leader_name":   "Tom",
    "leader_total":  14,
    "l7_leader":     "Tom",
    "l7_score":      8,
    "l7_note":       "none today",
    "months_done":   1,
    "months_total":  5,
    "players":       17,
}

# ─── NARRATIVE ───────────────────────────────────────────────────────────────
# Update as the season progresses


try:
    from zoneinfo import ZoneInfo as _ZI
    _ET_TZ = _ZI("America/New_York")
except Exception:
    from datetime import timezone as _tz, timedelta as _td
    _ET_TZ = _tz(_td(hours=-4))  # EDT fallback
_build_dt = _dt.now(tz=_ET_TZ)
UPDATED   = _build_dt.strftime("%I:%M %p ET  %m/%d/%Y").lstrip("0")

# Auto-set MONTHS status from build date
for _m in MONTHS:
    _mk = {"may":5,"june":6,"july":7,"aug":8,"sep":9}[_m["key"]]
    _m["status"] = "complete" if _build_dt.month > _mk else ("inprogress" if _build_dt.month == _mk else "upcoming")

# ── Temporary flags ──────────────────────────────────────────────────────────
# Set to False to remove the asterisk once investigation is resolved
NICK_INVESTIGATION = True
NICK_LOG = [{"date": "Jun 14","text": "Surveillance footage shows Nick entering a Costco at 11:58pm, purchasing ninety-six hot dogs, and then immediately returning them. The return receipt exists. The purchase receipt exists. There is no window in which the hot dogs could have been consumed. Nick says he changed his mind. Investigators say that is not an explanation."},{"date": "Jun 13","text": "A grocery store security camera caught Nick purchasing a single hot dog bun with no hot dog at 11:52pm on a Tuesday. Investigators spent six weeks trying to understand this and ultimately filed it under the most suspicious innocent act we have ever witnessed. The bun was entered into evidence."},{"date": "Jun 12","text": "Surveillance footage recovered from a 7-Eleven shows Nick entering at 2:47am, wandering the hot dog roller section for eleven minutes, purchasing nothing, and leaving while staring directly at the ceiling. Behavioral analysts have been studying the tape for three weeks and remain baffled."}]  # auto-filled by CI: newest first
HARRISON_INVESTIGATION = True
HARRISON_LOG = [{"date": "Jun 13", "text": "The FBI recovered a Post-it note from Harrison's recycling bin reading 'remember: hot dogs only, no burgers, they are watching.' Handwriting confirmed it was Harrison's. A second Post-it nearby read 'also destroy this note.' He had not destroyed either note. Both are now Exhibit A and Exhibit B."}, {"date": "Jun 12", "text": "Harrison's insurance adjuster testified that upon receiving the eleventh Food Baby photo, he called his supervisor assuming he was being pranked. His supervisor also assumed it was a prank. Both are now in therapy. The insurance company has requested the photos be destroyed. The FBI said absolutely not."}, {"date": "Jun 11", "text": "Uncle Sam the Glizzy Man appeared at his deposition in a t-shirt reading 'Glizzy Innocent' in large block letters, which his attorney had specifically told him not to wear. The shirt was confiscated as evidence. Harrison asked for it back three separate times. The answer was no each time."}]  # auto-filled by CI: newest first
HEADLINES = [{'icon': '📰', 'label': 'BREAKING', 'text': "The gap between Tom and Jon stands at 2 weenies. The Commission's analysts have been watching this number. It has been described as stubborn, meaningful, and uncomfortable to read aloud at press conferences.", 'date': 'Jun 14'}, {'icon': '🔥', 'label': 'HOT STREAK', 'text': "Momentum report: Tom has the hot hand at 8 over the last week. At this pace, the overall standings will shift by end of month. Tom's camp has declined to project by how much. The Commission estimates: considerably.", 'date': 'Jun 14'}, {'icon': '📊', 'label': 'STANDINGS', 'text': '5 players have not eaten a single official weenie. Their names are on file. Their excuses are also on file. The Commission reviewed the excuses and categorized them as creative, implausible, and in one case simply the word no.', 'date': 'Jun 14'}, {'icon': '🕵️', 'label': 'INVESTIGATION', 'text': 'Harrison submitted exculpatory evidence: a gas station receipt for a cylindrical food item during the competition window. Analysts confirmed the receipt is real and the station sells both hot dogs and sausages under the same label. Harrison said he ordered the hot dog. The analyst said he cannot confirm that from a receipt.', 'date': 'Jun 14'}]  # auto-filled by CI: 4 headlines per day
LAST_WEENIE_TS = 1781451717  # auto-filled by CI — Unix seconds of most recent weenie entry (ET→UTC)
JOEY_COUNT    = 70.5   # Joey Chestnut's most recent result (2025) — the benchmark
BIG_DAYS      = [('Thursday June11th', 15), ('Saturday June6th', 14), ('Monday May25th 🇺🇸', 12), ('Saturday June13th', 10), ('Sunday May31st', 3)]     # auto-filled by CI: [("Jun 3", 8), ...]
BIG_DAYS_BREAKDOWN = {}  # auto-filled by live-patch: {date: {player: count}}
WEENIE_LOG = []  # auto-filled by live-patch: [{player, count, display_ts, sort_ts}] newest first
RECORDS_SINGLE_DAY  = []  # auto-filled: [{player, count, date_display}] top 10 individual single-day
RECORDS_SINGLE_WEEK = []  # auto-filled: [{player, count, week_display}] top 10 individual single-week
BILLIONAIRE_DATA = [{'rank': 1, 'name': 'Elon Musk', 'worth_b': 1120.4, 'delta_b': 0.0}, {'rank': 2, 'name': 'Larry Page', 'worth_b': 294.1, 'delta_b': 0.0}, {'rank': 3, 'name': 'Sergey Brin', 'worth_b': 271.3, 'delta_b': 0.0}, {'rank': 4, 'name': 'Jeff Bezos', 'worth_b': 248.9, 'delta_b': 0.0}, {'rank': 5, 'name': 'Larry Ellison', 'worth_b': 231.5, 'delta_b': 0.0}]  # auto-filled by CI
NATHANS_URL   = "https://majorleagueeating.com/contests/1038"
NATHANS_DATE  = "July 4, 2026"

# Days until Nathan's — computed at build time
from datetime import datetime as _dt
_contest  = _dt(2026, 7, 4, tzinfo=_ET_TZ)
_today    = _build_dt
NATHANS_DAYS = max(0, (_contest - _today).days)

# Days remaining in Weenie Wars season — ends Labor Day (first Mon in Sep)
_labor_day   = _dt(2026, 9, 7, tzinfo=_ET_TZ)
SEASON_DAYS  = max(0, (_labor_day - _today).days)
SEASON_END   = "Sep 7, 2026"

# ─── BUILD ───────────────────────────────────────────────────────────────────

def _assign_places(players):
    sp = sorted(players, key=lambda p: p["total"], reverse=True)
    place = 1
    for i, p in enumerate(sp):
        if i > 0 and p["total"] < sp[i-1]["total"]:
            place = i + 1
        p["place"] = place
    players[:] = sp  # reorder in-place so table renders sorted by default

# ── Live-sheet self-patch (runs on every build) ─────────────────────────────
# Silently fetches the live Google Sheet and overwrites in-memory PLAYERS
# values before any HTML computation — ensures local builds are always fresh.
try:
    import urllib.request as _up, csv as _csv, io as _io
    from datetime import datetime as _dtnow, timedelta as _tdnow, timezone as _tznow
    _SHEET = ("https://docs.google.com/spreadsheets/d/"
              "1-NezoEWSZpeUIZem89ZMltE-kGX_P11LqKVoAwSG0gU/"
              "export?format=csv&gid=1814658863")
    _raw   = _up.urlopen(_SHEET + f"&_={int(_dtnow.now().timestamp())}", timeout=10).read().decode("utf-8")
    _rows  = list(_csv.DictReader(_io.StringIO(_raw)))
    _ET    = _tznow(_tdnow(hours=-4))
    _now   = _dtnow.now(_ET)
    _today = _now.date()
    _l7cut = _today - _tdnow(days=7)
    _tots, _mon, _l7, _tdayCts = {}, {m: {} for m in range(5,10)}, {}, {}
    for _r in _rows:
        _nm = _r["Name"].strip().replace("John", "Jon")
        try: _ct = int(float(_r["Weenies Consumed"]))
        except: continue
        try:
            _ts  = _dtnow.strptime(_r["Timestamp"].strip(), "%m/%d/%Y %H:%M:%S").replace(tzinfo=_ET)
            _edt = _ts.date()
        except: continue
        _tots[_nm] = _tots.get(_nm, 0) + _ct
        if _edt == _today:   _tdayCts[_nm] = _tdayCts.get(_nm, 0) + _ct
        if _edt >= _l7cut:   _l7[_nm]      = _l7.get(_nm, 0) + _ct
        if _ts.month in _mon: _mon[_ts.month].setdefault(_nm, 0); _mon[_ts.month][_nm] += _ct
    _nw  = sum(1 for v in _tots.values() if v > 0)
    _avg = sum(_tots.values()) / _nw if _nw else 1
    for _p in PLAYERS:
        _n = _p["name"]
        _p["total"] = _tots.get(_n, 0)
        _p["may"]   = _mon[5].get(_n, 0)
        _p["june"]  = _mon[6].get(_n, 0)
        _p["july"]  = _mon[7].get(_n, 0)
        _p["aug"]   = _mon[8].get(_n, 0)
        _p["sep"]   = _mon[9].get(_n, 0)
        _p["l7"]    = _l7.get(_n, 0)
        _p["chomp"] = round(_p["total"] / _avg * 100) if _p["total"] > 0 else 0
    # Update banner live data
    _ldr   = max(PLAYERS, key=lambda p: p["total"])
    _l7ldr = max(PLAYERS, key=lambda p: p["l7"]) if any(p["l7"] for p in PLAYERS) else _ldr
    BANNER["leader_name"]  = _ldr["name"]
    BANNER["leader_total"] = _ldr["total"]
    BANNER["l7_leader"]    = _l7ldr["name"]
    BANNER["l7_score"]     = _l7ldr["l7"]
    _l7td  = _tdayCts.get(_l7ldr["name"], 0)
    BANNER["l7_note"]      = f"{_l7td} today" if _l7td > 0 else "none today"
    BANNER["players"]      = len([p for p in PLAYERS if p["total"] > 0 or True])
    # Update BIG_DAYS from live data
    _day_tots = {}
    for _r in _rows:
        _nm = _r["Name"].strip().replace("John", "Jon")
        try: _ct = int(float(_r["Weenies Consumed"]))
        except: continue
        try:
            _ts  = _dtnow.strptime(_r["Timestamp"].strip(), "%m/%d/%Y %H:%M:%S").replace(tzinfo=_ET)
            _sfx = 'th' if 11 <= _ts.day <= 13 else {1:'st',2:'nd',3:'rd'}.get(_ts.day % 10, 'th')
            _dk  = _ts.strftime(f"%A %B {_ts.day}{_sfx}")
            if (_ts.month, _ts.day) in ((5, 25), (7, 4), (9, 7)): _dk += ' 🇺🇸'
        except: continue
        _day_tots[_dk] = _day_tots.get(_dk, 0) + _ct
    BIG_DAYS[:] = sorted(_day_tots.items(), key=lambda x: x[1], reverse=True)[:5]
    # Build per-day per-player breakdown for expandable rows
    _bkdn = {}
    for _r in _rows:
        _nm2 = _r['Name'].strip().replace('John', 'Jon')
        try: _ct2 = int(float(_r['Weenies Consumed']))
        except: continue
        try:
            _ts2 = _dtnow.strptime(_r['Timestamp'].strip(), '%m/%d/%Y %H:%M:%S').replace(tzinfo=_ET)
            _sfx2 = 'th' if 11 <= _ts2.day <= 13 else {1:'st',2:'nd',3:'rd'}.get(_ts2.day % 10, 'th')
            _dk2  = _ts2.strftime(f'%A %B {_ts2.day}{_sfx2}')
            if (_ts2.month, _ts2.day) in ((5, 25), (7, 4), (9, 7)): _dk2 += ' 🇺🇸'
        except: continue
        _bkdn.setdefault(_dk2, {})
        _bkdn[_dk2][_nm2] = _bkdn[_dk2].get(_nm2, 0) + _ct2
    BIG_DAYS_BREAKDOWN.clear()
    BIG_DAYS_BREAKDOWN.update({dk: _bkdn[dk] for dk, _ in BIG_DAYS if dk in _bkdn})
    # Build full weenie log (all entries, newest first)
    _log_entries = []
    for _r in _rows:
        _nm3 = _r['Name'].strip().replace('John', 'Jon')
        try: _ct3 = int(float(_r['Weenies Consumed']))
        except: continue
        try:
            _ts3 = _dtnow.strptime(_r['Timestamp'].strip(), '%m/%d/%Y %H:%M:%S').replace(tzinfo=_ET)
            _sfx3 = 'th' if 11 <= _ts3.day <= 13 else {1:'st',2:'nd',3:'rd'}.get(_ts3.day % 10, 'th')
            _disp3 = _ts3.strftime(f'%b {_ts3.day}{_sfx3}, %I:%M %p').lstrip('0')
        except: continue
        _log_entries.append({'player': _nm3, 'count': _ct3, 'display_ts': _disp3, 'sort_ts': _ts3.timestamp()})
    WEENIE_LOG.clear()
    WEENIE_LOG.extend(sorted(_log_entries, key=lambda x: -x['sort_ts']))
    # Build individual single-day and single-week records
    _indiv_day, _indiv_week = {}, {}
    for _r in _rows:
        _nm4 = _r['Name'].strip().replace('John', 'Jon')
        try: _ct4 = int(float(_r['Weenies Consumed']))
        except: continue
        try:
            _ts4 = _dtnow.strptime(_r['Timestamp'].strip(), '%m/%d/%Y %H:%M:%S').replace(tzinfo=_ET)
            _d4  = _ts4.date()
            _wk4 = _d4 - _tdnow(days=(_d4.weekday() + 1) % 7)
        except: continue
        _indiv_day[(_nm4, _d4)]   = _indiv_day.get((_nm4, _d4), 0)   + _ct4
        _indiv_week[(_nm4, _wk4)] = _indiv_week.get((_nm4, _wk4), 0) + _ct4
    RECORDS_SINGLE_DAY.clear()
    for (_pn4, _d4), _c4 in sorted(_indiv_day.items(), key=lambda x: -x[1])[:10]:
        _sfxr = 'th' if 11 <= _d4.day <= 13 else {1:'st',2:'nd',3:'rd'}.get(_d4.day % 10, 'th')
        RECORDS_SINGLE_DAY.append({'player': _pn4, 'count': _c4, 'date_display': _d4.strftime(f'%b {_d4.day}{_sfxr}')})
    RECORDS_SINGLE_WEEK.clear()
    for (_pn4, _wk4), _c4 in sorted(_indiv_week.items(), key=lambda x: -x[1])[:10]:
        _we4  = _wk4 + _tdnow(days=6)
        _sfxs = 'th' if 11 <= _wk4.day <= 13 else {1:'st',2:'nd',3:'rd'}.get(_wk4.day % 10, 'th')
        _sfxe = 'th' if 11 <= _we4.day  <= 13 else {1:'st',2:'nd',3:'rd'}.get(_we4.day  % 10, 'th')
        _wd = _wk4.strftime(f'%b {_wk4.day}{_sfxs}') + ' – ' + _we4.strftime(f'%b {_we4.day}{_sfxe}')
        RECORDS_SINGLE_WEEK.append({'player': _pn4, 'count': _c4, 'week_display': _wd})
    # Update LAST_WEENIE_TS
    _all_ts = []
    for _r in _rows:
        try:
            _ts = _dtnow.strptime(_r["Timestamp"].strip(), "%m/%d/%Y %H:%M:%S").replace(tzinfo=_ET)
            _all_ts.append(int(_ts.timestamp()))
        except: pass
    if _all_ts: LAST_WEENIE_TS = max(_all_ts)
except Exception as _live_err:
    pass  # silently fall back to hardcoded values if fetch fails

_assign_places(PLAYERS)

# Medal icons for top 3 unique ranks
# Medals fixed to places 1/2/3 — ties correctly skip a medal (e.g. two 1sts → no 2nd)
place_icons  = {1:"🥇", 2:"🥈", 3:"🥉"}
place_colors = {1:"#B8860B", 2:"#666", 3:"#8B4513"}

def streak_icon(p):
    # Use the most recently active month key to determine hot/cold
    recent_keys = ["sep","aug","july","june","may"]
    for k in recent_keys:
        vals = [x[k] for x in PLAYERS if x[k] > 0]
        if vals:  # this is the most recent month with any score
            return "🔥" if p[k] > 0 else ("🧊" if p["total"] == 0 else "📉")
    return "🧊"

def chomp_color(c):
    if c >= 400: return "#B22234"
    if c >= 200: return "#002868"
    if c > 0:    return "#445580"
    return "#c0c8d8"

def odds_color(o):
    val = int(o.replace("+","").replace("-",""))
    if o.startswith("-") or val <= 400: return "#002868"
    if val <= 1500:                     return "#445580"
    return "#8a9abc"

def p2j_fmt(total):
    """% to Joey Chestnut's most recent result. Returns (display_str, color)."""
    if total == 0:
        return '<span style="color:#c0c8d8">—</span>', "#c0c8d8"
    pct = round(total / JOEY_COUNT * 100, 1)
    # Color: <5% faint, 5-10% navy, >10% red (extremely impressive)
    if pct >= 10:   color = "#B22234"
    elif pct >= 5:  color = "#002868"
    else:           color = "#445580"
    return f'<strong style="color:{color}">{pct}%</strong>', color

def top_scorer(month_key):
    if not month_key: return None, 0
    best = max(PLAYERS, key=lambda p: p[month_key])
    return (best["name"], best[month_key]) if best[month_key] > 0 else (None, 0)

def fv(v): return str(v) if v else "—"


# ── Headlines HTML builder ────────────────────────────────────────────────────
def _build_headlines_html(headlines):
    if not headlines:
        return '<p style="color:#aab;text-align:center;padding:20px 0">No headlines today — check back at 8am ET.</p>'
    parts = []
    label_colors = {"BREAKING":"#B22234","HOT STREAK":"#cc6600","STANDINGS":"#002868","INVESTIGATION":"#5a0d8a"}
    for i, h in enumerate(headlines):
        sep = 'border-bottom:1px solid #e8edf5;margin-bottom:14px;padding-bottom:14px;' if i < len(headlines)-1 else ''
        lcol = label_colors.get(h.get("label",""), "#B22234")
        parts.append(
            f'<div style="{sep}">' +
            f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:5px">' +
            f'<span style="font-size:1.05em">{h["icon"]}</span>' +
            f'<span style="font-size:0.63em;font-weight:800;letter-spacing:1.2px;color:{lcol};text-transform:uppercase">{h["label"]}</span>' +
            f'<span style="font-size:0.63em;color:#aab4cc;margin-left:auto">{h["date"]}</span>' +
            '</div>' +
            f'<p style="margin:0;color:#334;font-size:0.88em;line-height:1.6">{h["text"]}</p>' +
            '</div>'
        )
    return "".join(parts)

HEADLINES_HTML = _build_headlines_html(HEADLINES)

# ── Leaderboard rows
rows_html = ""
for i, p in enumerate(PLAYERS):
    icon   = place_icons.get(p["place"], "")
    pc     = place_colors.get(p["place"], "#8a9abc")
    streak = streak_icon(p)
    bg     = "#ffffff" if i % 2 == 0 else "#f4f7fc"
    ns     = "color:#002868;font-weight:600;"
    tcol   = "#B22234" if p["total"] > 0 else "#b0bcd4"
    l7c    = "#002868" if p["l7"] > 0 else "#c0c8d8"
    cc     = chomp_color(p["chomp"])
    oc     = odds_color(p["odds"])
    chomp_str = f'<strong>{p["chomp"]}</strong>' if p["chomp"] > 0 else '<span style="color:#c0c8d8">—</span>'
    odds_str  = f'<span style="color:{oc};font-weight:bold">{p["odds"]}</span> <span style="color:{p["mc"]};font-size:0.75em">{p["move"]}</span>'
    p2j_str, _ = p2j_fmt(p["total"])
    td = "padding:7px 9px"
    nick_badge = ('<sup style="color:#B22234;font-size:0.8em">*</sup>'
                  '<span style="font-size:0.72em;color:#B22234;font-weight:normal;"> (under review)</span>'
                  if p["name"] == "Nick" and NICK_INVESTIGATION else '')
    harrison_badge = ('<sup style="color:#B22234;font-size:0.8em">†</sup>'
                      '<span style="font-size:0.72em;color:#B22234;font-weight:normal;"> (Fraudfurter case)</span>'
                      if p["name"] == "Harrison" and HARRISON_INVESTIGATION else '')
    rows_html += f"""
    <tr style="background:{bg};" data-player="{p['name']}" data-chomp="{p['chomp']}" data-place="{p['place']}">
      <td style="{td};text-align:center;font-size:1em">{streak}</td>
      <td style="{td};color:{pc};font-weight:bold;text-align:center;white-space:nowrap">{icon} {p['place']}</td>
      <td style="{td};{ns}">{p['name']}{nick_badge}{harrison_badge}</td>
      <td style="{td};text-align:center;font-weight:bold;color:{tcol}">{fv(p['total'])}</td>
      <td style="{td};text-align:center;font-size:0.93em">{p2j_str}</td>
      <td style="{td};text-align:center;color:#445580">{fv(p['may'])}</td>
      <td style="{td};text-align:center;color:#445580">{fv(p['june'])}</td>
      <td style="{td};text-align:center;color:#445580">{fv(p['july'])}</td>
      <td style="{td};text-align:center;color:#445580">{fv(p['aug'])}</td>
      <td style="{td};text-align:center;color:#445580">{fv(p['sep'])}</td>
      <td style="{td};text-align:center;font-weight:bold;color:{l7c}">{fv(p['l7'])}</td>
      <td style="{td};text-align:center;color:{cc};font-size:0.95em">{chomp_str}</td>
      <td style="{td};text-align:center;white-space:nowrap;font-size:0.95em">{odds_str}</td>
    </tr>"""

# ── Month tiles
month_tiles = ""
for m in MONTHS:
    winner, w_count = top_scorer(m["key"])
    has_data = winner is not None
    status   = m["status"]
    if status == "complete":
        tile_bg = "linear-gradient(135deg,#B22234,#cc2a3c)"; tile_border = "#8a1020"; tc = "#fff"
        badge = '<span style="background:rgba(0,0,0,0.2);color:#fff;font-size:0.62em;padding:1px 7px;border-radius:10px;font-weight:bold;letter-spacing:1px">✓ COMPLETE</span>'
        winner_block = f"""<div style="margin-top:7px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.25)">
          <div style="font-size:0.6em;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.65);margin-bottom:2px">Most Weenies</div>
          <div style="font-size:0.9em;font-weight:bold;color:#fff">🌭 {winner}</div>
          <div style="font-size:1.35em;font-weight:900;color:#FFD700;line-height:1.1">{w_count}</div>
        </div>""" if has_data else ""
    elif status == "inprogress":
        tile_bg = "linear-gradient(135deg,#edf1f9,#dde4f2)"; tile_border = "#3a6abf"; tc = "#002868"
        badge = '<span style="background:#002868;color:#fff;font-size:0.62em;padding:1px 7px;border-radius:10px;font-weight:bold;letter-spacing:1px">⚡ IN PROGRESS</span>'
        winner_block = f"""<div style="margin-top:7px;padding-top:6px;border-top:1px solid #c8d4ea">
          <div style="font-size:0.6em;text-transform:uppercase;letter-spacing:1px;color:#8a9abc;margin-bottom:2px">Leading</div>
          <div style="font-size:0.9em;font-weight:bold;color:#002868">🌭 {winner}</div>
          <div style="font-size:1.35em;font-weight:900;color:#B22234;line-height:1.1">{w_count}</div>
        </div>""" if has_data else '<div style="font-size:1.1em;color:#b0bcd4;margin-top:8px">No scores yet</div>'
    else:
        tile_bg = "linear-gradient(135deg,#edf1f9,#dde4f2)"; tile_border = "#b8c8e8"; tc = "#002868"
        badge = '<span style="background:#c8d4ea;color:#445580;font-size:0.62em;padding:1px 7px;border-radius:10px;letter-spacing:1px">UPCOMING</span>'
        winner_block = """<div style="margin-top:7px;padding-top:6px;border-top:1px solid #c8d4ea">
          <div style="font-size:0.6em;text-transform:uppercase;letter-spacing:1px;color:#b0bcd4;margin-bottom:2px">Most Weenies</div>
          <div style="font-size:0.9em;font-weight:bold;color:#c0c8d8">🌭 TBD</div>
          <div style="font-size:1.35em;font-weight:900;color:#c0c8d8;line-height:1.1">—</div>
        </div>"""
    month_tiles += f"""<div data-month="{m['key']}" style="background:{tile_bg};border:1px solid {tile_border};border-radius:9px;padding:10px 13px;min-width:100px;text-align:center;flex-shrink:0;align-self:flex-start;cursor:pointer;transition:outline 0.1s">
      <div style="color:{tc};font-weight:bold;font-size:0.85em;margin-bottom:5px;letter-spacing:1px">{m['name']}</div>
      {badge}{winner_block}</div>"""

months_remaining = sum(1 for m in MONTHS if m["status"] != "complete")
_total_weenies = sum(p["total"] for p in PLAYERS)
_total_lbs     = round(_total_weenies * 2 / 16, 2)  # ~2 oz per hot dog → lbs
_total_ft      = round(_total_weenies * 6 / 12, 2)  # 6 inch standard weenie → ft

# ── Biggest Weenie Days card ─────────────────────────────────────────────────
if BIG_DAYS:
    _big_rows = ""
    for _i, (_date, _cnt) in enumerate(BIG_DAYS):
        _lbs  = round(_cnt * 2 / 16, 2)
        _ft   = round(_cnt * 6 / 12, 2)
        _rbg  = "background:#f7f9fc;" if _i % 2 == 0 else "background:#fff;"
        # Build breakdown pills
        _bk = BIG_DAYS_BREAKDOWN.get(_date, {})
        _pills = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:3px;background:#fff;border:1px solid #c8d4e8;border-radius:4px;padding:2px 7px;font-size:0.82em;color:#334;white-space:nowrap"><strong style="color:#002868">{_pn}</strong>&nbsp;{_pc}&nbsp;🌭</span>'
            for _pn, _pc in sorted(_bk.items(), key=lambda x: -x[1]) if _pc > 0
        )
        _big_rows += (
            f'<tr style="{_rbg}cursor:pointer" onclick="toggleBigDay({_i})">'
            f'<td style="padding:6px 4px;color:#334">'
            f'<span id="bwd-arrow-{_i}" style="font-size:0.7em;margin-right:5px;color:#7a8aaa">▶</span>{_date}</td>'
            f'<td style="text-align:right;padding:6px 4px;font-weight:700;color:#002868">{_cnt}</td>'
            f'<td style="text-align:right;padding:6px 4px;color:#666">{_lbs} lbs</td>'
            f'<td style="text-align:right;padding:6px 4px;color:#666">{_ft} ft</td>'
            f'</tr>'
            f'<tr id="bwd-{_i}" style="display:none">'
            f'<td colspan="4" style="padding:6px 10px 10px 10px;background:#eef1f8;'
            f'border-bottom:1px solid #d0daee">'
            f'<div style="display:flex;flex-wrap:wrap;gap:5px">{_pills}</div>'
            f'</td></tr>'
        )
    BIG_DAYS_HTML = (
        '<div class="nt">🏆 <span style="font-size:1.25em;font-weight:900;color:#002868">Biggest Weenie</span> Days</div>'
        '<table style="width:100%;border-collapse:collapse;font-size:0.88em;">'
        '<thead><tr>'
        '<th style="text-align:left;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">Date</th>'
        '<th style="text-align:right;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">Weenies</th>'
        '<th style="text-align:right;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">Lbs</th>'
        '<th style="text-align:right;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">Ft</th>'
        '</tr></thead>'
        f'<tbody>{_big_rows}</tbody>'
        '</table>'
        '<div style="font-size:0.7em;color:#aab;margin-top:8px;font-style:italic">'
        '* Feet calculated assuming 6&quot; average weenie length, which is in fact very above average.</div>'
    )
else:
    BIG_DAYS_HTML = ""

# ── Full Weenie Log HTML ─────────────────────────────────────────────────────
if WEENIE_LOG:
    _log_rows = ""
    for _li, _entry in enumerate(WEENIE_LOG):
        _lrbg = "background:#f7f9fc;" if _li % 2 == 0 else "background:#fff;"
        _log_rows += (
            f'<tr style="{_lrbg}">'
            f'<td style="padding:5px 6px;color:#7a8aaa;font-size:0.82em;white-space:nowrap">{_entry["display_ts"]}</td>'
            f'<td style="padding:5px 6px;color:#334;font-weight:600">{_entry["player"]}</td>'
            f'<td style="text-align:right;padding:5px 6px;font-weight:700;color:#002868">{_entry["count"]} 🌭</td>'
            f'</tr>'
        )
    WEENIE_LOG_HTML = (
        '<table style="width:100%;border-collapse:collapse;font-size:0.88em;">'
        '<thead><tr>'
        '<th style="text-align:left;color:#7a8aaa;font-weight:600;padding:4px 6px;border-bottom:1px solid #e0e6f0">When</th>'
        '<th style="text-align:left;color:#7a8aaa;font-weight:600;padding:4px 6px;border-bottom:1px solid #e0e6f0">Player</th>'
        '<th style="text-align:right;color:#7a8aaa;font-weight:600;padding:4px 6px;border-bottom:1px solid #e0e6f0">Logged</th>'
        '</tr></thead>'
        f'<tbody>{_log_rows}</tbody>'
        '</table>'
    )
else:
    WEENIE_LOG_HTML = '<div style="color:#aab;text-align:center;padding:20px">No weenies logged yet.</div>'

# ── Billionaire Weenie Fund card ─────────────────────────────────────────────
_WEENIE_PRICE = 5.0  # Nathan's Famous ballpark price

def _fmt_worth(b):
    if b >= 1000: return f"${b/1000:.2f}T"
    return f"${b:.0f}B"

def _fmt_w(w):
    if w >= 1e9:  return f"{w/1e9:.1f}B"
    if w >= 1e6:  return f"{w/1e6:.1f}M"
    if w >= 1e3:  return f"{w/1e3:.1f}K"
    return str(int(w))

if BILLIONAIRE_DATA:
    _bill_rows = ""
    for _bi, _bd in enumerate(BILLIONAIRE_DATA):
        _rbg   = "background:#f7f9fc;" if _bi % 2 == 0 else ""
        _worth = _fmt_worth(_bd["worth_b"])
        _ween  = _fmt_w(_bd["worth_b"] * 1e9 / _WEENIE_PRICE)
        _bill_rows += (
            f'<tr style="{_rbg}">'
            f'<td style="padding:6px 4px;color:#7a8aaa;font-size:0.85em">{_bd["rank"]}</td>'
            f'<td style="padding:6px 4px;color:#334;font-weight:600">{_bd["name"]}</td>'
            f'<td style="text-align:right;padding:6px 4px;color:#334">{_worth}</td>'
            f'<td style="text-align:right;padding:6px 4px;font-weight:700;color:#002868">{_ween} 🌭</td>'
            f'</tr>'
        )
    BILLIONAIRE_CARD_HTML = (
        '<div class="nt">💰 Big Shot Weenies</div>'
        '<div style="font-size:0.72em;color:#7a8aaa;margin-bottom:8px">Forbes Real-Time Billionaires · priced at $5&thinsp;/&thinsp;🌭</div>'
        '<table style="width:100%;border-collapse:collapse;font-size:0.88em;">'
        '<thead><tr>'
        '<th style="text-align:left;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">#</th>'
        '<th style="text-align:left;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">Name</th>'
        '<th style="text-align:right;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">Net Worth</th>'
        '<th style="text-align:right;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">🌭 Weenies</th>'
        '</tr></thead>'
        f'<tbody>{_bill_rows}</tbody>'
        '</table>'
    )
else:
    BILLIONAIRE_CARD_HTML = ""

# ── Records card (top 10 individual day + week) ────────────────────────────────
def _rec_table(entries, date_key, hdr_label):
    medals = {0:"🥇",1:"🥈",2:"🥉"}
    rows = ""
    for _ri, _e in enumerate(entries):
        _rbg = "background:#f7f9fc;" if _ri % 2 == 0 else "background:#fff;"
        _med = medals.get(_ri, f'<span style="color:#aab;font-size:0.8em">{_ri+1}</span>')
        rows += (
            f'<tr style="{_rbg}">'
            f'<td style="padding:5px 4px;text-align:center;font-size:0.95em">{_med}</td>'
            f'<td style="padding:5px 4px;color:#334;font-weight:600">{_e["player"]}</td>'
            f'<td style="padding:5px 4px;color:#7a8aaa;font-size:0.82em;white-space:nowrap">{_e[date_key]}</td>'
            f'<td style="text-align:right;padding:5px 4px;font-weight:700;color:#002868">{_e["count"]} 🌭</td>'
            f'</tr>'
        )
    return (
        f'<div class="nt" style="margin-top:6px">🏅 {hdr_label}</div>'
        '<table style="width:100%;border-collapse:collapse;font-size:0.88em;">'
        '<thead><tr>'
        '<th style="text-align:center;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0;width:28px">#</th>'
        '<th style="text-align:left;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">Player</th>'
        f'<th style="text-align:left;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">{hdr_label.split()[2] if len(hdr_label.split()) > 2 else "Period"}</th>'
        '<th style="text-align:right;color:#7a8aaa;font-weight:600;padding:4px 4px;border-bottom:1px solid #e0e6f0">Weenies</th>'
        '</tr></thead>'
        f'<tbody>{rows}</tbody>'
        '</table>'
    ) if entries else ""

RECORDS_HTML = (
    _rec_table(RECORDS_SINGLE_DAY,  "date_display", "Best Single Day") +
    '<div style="height:14px"></div>' +
    _rec_table(RECORDS_SINGLE_WEEK, "week_display", "Best Single Week")
) or '<div style="color:#aab;text-align:center;padding:20px">No records yet.</div>'


# ── Compute narrative ────────────────────────────────────────────────────────

# ── Nick / Harrison log HTML (3 entries, newest first) ──────────────────────
def _build_log_html(log):
    parts = []
    for i, entry in enumerate(log[:3]):
        sep = 'border-bottom:1px solid #e8edf5;margin-bottom:12px;padding-bottom:12px;' if i < min(2, len(log) - 1) else ''
        parts.append(
            f'<div style="{sep}">'
            f'<div style="font-size:0.68em;color:#8a9abc;font-weight:700;letter-spacing:0.8px;margin-bottom:5px;text-transform:uppercase">{entry["date"]}</div>'
            f'<p style="margin:0;color:#334;font-size:0.92em;line-height:1.6">{entry["text"]}</p>'
            f'</div>'
        )
    return "".join(parts)

NICK_LOG_HTML     = _build_log_html(NICK_LOG)
HARRISON_LOG_HTML = _build_log_html(HARRISON_LOG)

# Narrative switcher JS — defined outside f-string to avoid brace-escaping
NARRATIVE_SWITCHER_JS = """<script>
function switchNarrative(id) {
  ['nick','harrison','headlines'].forEach(function(n) {
    document.getElementById('narr-'+n).style.display = (n===id) ? '' : 'none';
    document.getElementById('nb-'+n).classList.toggle('active', n===id);
  });
}
function switchBBW(id) {
  ['days','shots','records'].forEach(function(n) {
    document.getElementById('bbw-'+n).style.display = (n===id) ? '' : 'none';
    document.getElementById('bbw-'+n+'-btn').classList.toggle('active', n===id);
  });
}
function toggleBigDay(i) {
  var row   = document.getElementById('bwd-'+i);
  var arrow = document.getElementById('bwd-arrow-'+i);
  var open  = row.style.display !== 'none';
  row.style.display  = open ? 'none' : '';
  arrow.textContent  = open ? '\u25b6' : '\u25bc';
}
function toggleWeenielog() {
  var panel = document.getElementById("weenie-log-panel");
  var btn   = document.getElementById("wl-btn");
  var open  = panel.style.display !== "none";
  panel.style.display = open ? "none" : "";
  btn.textContent = open ? "\U0001f4cb Full Weenie Log" : "\u2715 Hide Log";
}
</script>"""

# Mobile month filter JS — defined outside f-string to avoid brace-escaping issues
MOBILE_FILTER_JS = """<script>
(function() {
  var bar = document.getElementById('monthFilter');
  if (!bar) return;
  var pills   = Array.from(bar.querySelectorAll('.mf-pill'));
  var headers = Array.from(document.querySelectorAll('#leaderboard-table thead th'));
  var tb      = document.querySelector('#leaderboard-table tbody');
  var MONTH_COLS = {may:5, june:6, july:7, aug:8, sep:9};
  var TOTAL_COL = 3, P2J_COL = 4, L7_COL = 10, CHOMP_COL = 11, ODDS_COL = 12;
  var PLACE_COL = 1;
  var PLACE_ICONS  = {1:"🥇", 2:"🥈", 3:"🥉"};
  var PLACE_COLORS = {1:"#B8860B", 2:"#666", 3:"#8B4513"};

  function setPlaceCell(cell, place) {
    var icon  = PLACE_ICONS[place]  || "";
    var color = PLACE_COLORS[place] || "#8a9abc";
    cell.style.color = color;
    cell.innerHTML = (icon ? icon + " " : "") + place;
  }

  function updatePlaceForMonth(col) {
    var sortedRows = Array.from(tb.querySelectorAll('tr'));
    var place = 1;
    sortedRows.forEach(function(row, i) {
      if (!row.cells[col] || !row.cells[PLACE_COL]) return;
      if (i > 0) {
        var prevVal = parseInt((sortedRows[i-1].cells[col].textContent || '0').replace(/[^0-9]/g,'') || '0');
        var curVal  = parseInt((row.cells[col].textContent || '0').replace(/[^0-9]/g,'') || '0');
        if (curVal < prevVal) place = i + 1;
      }
      setPlaceCell(row.cells[PLACE_COL], place);
    });
  }

  function restoreSeasonPlace() {
    Array.from(tb.querySelectorAll('tr')).forEach(function(row) {
      if (!row.cells[PLACE_COL]) return;
      var place = parseInt(row.dataset.place || '0');
      setPlaceCell(row.cells[PLACE_COL], place);
    });
  }

  function setColVisible(ci, visible) {
    var disp = visible ? 'table-cell' : 'none';
    headers[ci].style.display = disp;
    Array.from(tb.querySelectorAll('tr')).forEach(function(row) {
      if (row.cells[ci]) row.cells[ci].style.display = disp;
    });
  }

  function sortBy(col) {
    var rows = Array.from(tb.querySelectorAll('tr'));
    rows.sort(function(a, b) {
      var av = parseInt((a.cells[col] ? a.cells[col].textContent : '0').replace(/[^0-9]/g, '') || '0');
      var bv = parseInt((b.cells[col] ? b.cells[col].textContent : '0').replace(/[^0-9]/g, '') || '0');
      return bv - av;
    });
    rows.forEach(function(r) { tb.appendChild(r); });
  }

  function chompColor(c) {
    if (c >= 400) return '#B22234';
    if (c >= 200) return '#002868';
    if (c > 0)    return '#445580';
    return '#c0c8d8';
  }

  function setChompCell(row, chomp) {
    var cell = row.cells[CHOMP_COL];
    if (!cell) return;
    cell.style.color = chompColor(chomp);
    cell.innerHTML = chomp > 0
      ? '<strong>' + chomp + '</strong>'
      : '<span style="color:#c0c8d8">—</span>';
  }

  function updateChompForMonth(month) {
    var names = Object.keys(WW_PLAYERS);
    var total = 0;
    names.forEach(function(n) { total += (WW_PLAYERS[n][month] || 0); });
    var avg = WW_N > 0 ? total / WW_N : 0;
    Array.from(tb.querySelectorAll('tr')).forEach(function(row) {
      var name = row.dataset.player;
      if (!name || !WW_PLAYERS[name]) return;
      var t = WW_PLAYERS[name][month] || 0;
      var chomp = avg > 0 ? Math.round(t / avg * 100) : 0;
      setChompCell(row, chomp);
    });
  }

  function restoreSeasonChomp() {
    Array.from(tb.querySelectorAll('tr')).forEach(function(row) {
      setChompCell(row, parseInt(row.dataset.chomp || '0'));
    });
  }

  pills.forEach(function(pill) {
    pill.addEventListener('click', function() {
      pills.forEach(function(p) { p.classList.remove('active'); });
      pill.classList.add('active');
      var month = pill.dataset.month;
      if (month === 'all') {
        setColVisible(TOTAL_COL, true);
        setColVisible(P2J_COL,   true);
        setColVisible(L7_COL,    true);
        setColVisible(CHOMP_COL, true);
        setColVisible(ODDS_COL,  true);
        Object.keys(MONTH_COLS).forEach(function(m) { setColVisible(MONTH_COLS[m], false); });
        restoreSeasonChomp();
        restoreSeasonPlace();
        sortBy(TOTAL_COL);
      } else {
        var col = MONTH_COLS[month];
        setColVisible(TOTAL_COL, false);
        setColVisible(P2J_COL,   false);
        setColVisible(L7_COL,    false);
        setColVisible(CHOMP_COL, true);
        setColVisible(ODDS_COL,  false);
        Object.keys(MONTH_COLS).forEach(function(m) { setColVisible(MONTH_COLS[m], m === month); });
        updateChompForMonth(month);
        sortBy(col);
        updatePlaceForMonth(col);
      }
    });
  });

  pills[0].click();
})();
</script>"""

# Stat note examples — computed from live PLAYERS data
_chomp_leaders = sorted([p for p in PLAYERS if p["chomp"] > 0], key=lambda p: p["chomp"], reverse=True)
_chomp_ex = _chomp_leaders[0] if _chomp_leaders else None
STAT_CHOMP_EX = (
    f'{_chomp_ex["name"]} at {_chomp_ex["chomp"]} = {round(_chomp_ex["chomp"]/100,1)}× field avg'
    if _chomp_ex else "league avg = 100 by definition"
)
_p2j_leaders = sorted([p for p in PLAYERS if p["total"] > 0], key=lambda p: p["total"], reverse=True)
_p2j_ex = _p2j_leaders[0] if _p2j_leaders else None
STAT_P2J_EX = (
    f'{_p2j_ex["name"]} at {round(_p2j_ex["total"]/JOEY_COUNT*100,1)}% = {_p2j_ex["total"]} / {JOEY_COUNT}'
    if _p2j_ex else f"leader / {JOEY_COUNT} dogs"
)

# Per-player monthly data for dynamic CHOMP+ in JS
_pd = ", ".join(
    f'"{p["name"]}":{{"may":{p["may"]},"june":{p["june"]},"july":{p["july"]},"aug":{p["aug"]},"sep":{p["sep"]},"chomp":{p["chomp"]}}}'
    for p in PLAYERS
)
PLAYER_DATA_SCRIPT = f'<script>var WW_PLAYERS={{{_pd}}};var WW_N={len(PLAYERS)};</script>'

# ── Season progress chart (cumulative weenies per player by week)
import urllib.request as _ureq, csv as _csv, io as _io
from datetime import timedelta as _td

_SEASON_START = _dt(2026, 5, 25, tzinfo=_ET_TZ)   # Memorial Day
_SEASON_END   = _dt(2026, 9, 7,  tzinfo=_ET_TZ)    # Labor Day
_N_WEEKS      = ((_SEASON_END - _SEASON_START).days // 7) + 1  # 16 weeks
_pal = ["#B22234","#002868","#1a7a4a","#e07b00","#cc44aa","#6a0dad",
        "#0077aa","#e05500","#336633","#005577","#8B4513","#445580",
        "#cc6600","#887733","#008855","#6633cc"]

# Week start labels: "5/25", "6/1", …
_wk_labels = ["{}/{}".format((_SEASON_START + _td(weeks=_wi)).month,
                              (_SEASON_START + _td(weeks=_wi)).day)
              for _wi in range(_N_WEEKS)]

# Fetch raw sheet and bin entries by week
_today_dt    = _build_dt
_current_wk  = (_today_dt - _SEASON_START).days // 7  # 0-based
_per_week    = {}  # name -> list[int] length _N_WEEKS
_CSV_URL = ("https://docs.google.com/spreadsheets/d/"
            "1-NezoEWSZpeUIZem89ZMltE-kGX_P11LqKVoAwSG0gU/"
            "export?format=csv&gid=1814658863")
try:
    with _ureq.urlopen(_CSV_URL, timeout=10) as _resp:
        _raw = _resp.read().decode("utf-8")
    for _row in _csv.reader(_io.StringIO(_raw)):
        if len(_row) < 3 or _row[0].strip() == "Timestamp":
            continue
        try:
            _ts = _dt.strptime(_row[0].strip(), "%m/%d/%Y %H:%M:%S").replace(tzinfo=_ET_TZ)
        except ValueError:
            continue
        _nm = _row[1].strip()
        if _nm == "John":
            _nm = "Jon"
        try:
            _cnt = int(float(_row[2].strip()))
        except ValueError:
            continue
        _wi = (_ts - _SEASON_START).days // 7
        if _wi < 0 or _wi >= _N_WEEKS:
            continue
        if _nm not in _per_week:
            _per_week[_nm] = [0] * _N_WEEKS
        _per_week[_nm][_wi] += _cnt
except Exception as _csv_err:
    print(f"Warning: CSV fetch failed ({_csv_err}) — chart may be empty")

# Build cumulative datasets, null for weeks beyond today
_sp  = sorted(PLAYERS, key=lambda x: x["total"], reverse=True)
_cds = []
for _ci, _cp in enumerate(_sp):
    _col   = _pal[_ci % len(_pal)]
    _wkly  = _per_week.get(_cp["name"], [0] * _N_WEEKS)
    _run   = 0
    _dv    = []
    for _wi2 in range(_N_WEEKS):
        _run += _wkly[_wi2]
        _dv.append(str(_run) if _wi2 <= _current_wk else "null")
    _cds.append('{{"label":"{}","data":[{}],"borderColor":"{}","backgroundColor":"{}22","tension":0.3,"pointRadius":3,"pointHoverRadius":5,"borderWidth":2}}'.format(
        _cp["name"], ",".join(_dv), _col, _col))

_cds_js    = "[" + ",".join(_cds) + "]"
_labels_js = "[" + ",".join('"' + l + '"' for l in _wk_labels) + "]"
CHART_SECTION = (
    '\U0001f32d Season Progress \u2014 Cumulative Weenies'.join([
        '<div class="section-title" style="margin-top:18px">',
        '</div>'
    ])
    + '<div style="background:#fff;border:1px solid #c8d4ea;border-radius:9px;padding:16px 14px;'
      'box-shadow:0 1px 6px rgba(0,40,104,0.07);margin-bottom:14px">'
      '<canvas id="wwChart" style="max-height:340px"></canvas></div>'
    + '<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>'
    + '<script>(function(){var ctx=document.getElementById("wwChart").getContext("2d");'
      'new Chart(ctx,{type:"line",data:{labels:' + _labels_js + ',datasets:' + _cds_js + '},'
      'options:{responsive:true,maintainAspectRatio:true,spanGaps:false,'
      'interaction:{mode:"index",intersect:false},'
      'plugins:{legend:{position:"bottom",labels:{boxWidth:10,padding:8,font:{size:10},color:"#445580"}},'
      'tooltip:{callbacks:{'
      'title:function(i){return "Wk of "+i[0].label+" (Cumulative)";},'
      'label:function(i){return i.dataset.label+": "+(i.raw!==null?i.raw:"—")+" \U0001f32d";}'
      '}}},'
      'scales:{'
      'x:{grid:{color:"#edf1f9"},ticks:{color:"#7a8aaa",font:{size:10},maxRotation:45,minRotation:0,autoSkip:true,maxTicksLimit:10}},'
      'y:{beginAtZero:true,ticks:{stepSize:1,color:"#7a8aaa",font:{size:11}},grid:{color:"#edf1f9"}}'
      '}'
      '}});})();</script>'
)

HOME_SCREEN_JS = """<style>
@keyframes ww-slide-up { from { transform:translateY(60px); opacity:0; } to { transform:translateY(0); opacity:1; } }
@keyframes ww-bounce   { 0%,100% { transform:translateY(0); } 50% { transform:translateY(8px); } }
</style>
<script>
(function() {
  var btn = document.getElementById('installBtn');
  var ua  = navigator.userAgent;
  var isIOS       = /iPhone|iPad/.test(ua);
  var isSafari    = /Safari/.test(ua) && !/CriOS|FxiOS|EdgiOS|OPiOS/.test(ua);
  var isStandalone = window.navigator.standalone === true;
  var _prompt = null;

  // Android/Chrome: capture install prompt — allows skipping share sheet entirely
  window.addEventListener('beforeinstallprompt', function(e) {
    e.preventDefault();
    _prompt = e;
    if (btn) btn.style.display = 'inline-block';
  });

  // iOS Safari (not already installed)
  if (isIOS && isSafari && !isStandalone && btn) {
    btn.style.display = 'inline-block';
  }

  // Inject modal HTML once on first use
  var _modalEl = null;
  function buildModal() {
    if (_modalEl) return;
    _modalEl = document.createElement('div');
    _modalEl.id = 'ww-install-modal';
    _modalEl.innerHTML =
      '<div id="ww-install-overlay" onclick="if(event.target===this)closeInstallModal()" '
      + 'style="position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:9998;'
      + 'display:none;align-items:flex-end;justify-content:center;padding-bottom:0">'
      + '<div style="background:#fff;border-radius:20px 20px 0 0;padding:22px 20px 40px;'
      + 'max-width:440px;width:100%;position:relative;animation:ww-slide-up 0.25s ease-out">'
      // close button
      + '<button onclick="closeInstallModal()" style="position:absolute;top:12px;right:16px;'
      + 'border:none;background:none;font-size:1.5em;color:#999;cursor:pointer;line-height:1;'
      + 'padding:4px 8px;border-radius:50%">&#10005;</button>'
      // header
      + '<div style="text-align:center;margin-bottom:18px;padding-top:4px">'
      + '<div style="font-size:1.35em;font-weight:900;color:#002868;margin-bottom:5px">📲 Add to Home Screen</div>'
      + '<div style="font-size:0.83em;color:#7a8aaa;line-height:1.4">Open Weenie Wars like a native app —<br>instant load, no browser chrome</div>'
      + '</div>'
      // steps
      + '<div style="display:flex;flex-direction:column;gap:10px;margin-bottom:22px">'
      // step 1
      + '<div style="display:flex;align-items:center;gap:13px;background:#f0f4fb;'
      + 'border-radius:12px;padding:12px 14px">'
      + '<span style="font-size:1.5em;min-width:30px;text-align:center">1️⃣</span>'
      + '<span style="font-size:0.88em;color:#334;line-height:1.4">Tap the '
      + '<strong style="color:#002868">Share</strong> button '
      + '<span style="display:inline-block;border:1.5px solid #445580;border-radius:4px;'
      + 'padding:0 4px;font-size:1.1em;line-height:1.3;vertical-align:middle">&#11014;</span>'
      + ' at the <strong>bottom</strong> of Safari</span>'
      + '</div>'
      // step 2
      + '<div style="display:flex;align-items:center;gap:13px;background:#f0f4fb;'
      + 'border-radius:12px;padding:12px 14px">'
      + '<span style="font-size:1.5em;min-width:30px;text-align:center">2️⃣</span>'
      + '<span style="font-size:0.88em;color:#334;line-height:1.4">Scroll down and tap '
      + '<strong style="color:#002868">"Add to Home Screen"</strong></span>'
      + '</div>'
      // step 3
      + '<div style="display:flex;align-items:center;gap:13px;background:#f0f4fb;'
      + 'border-radius:12px;padding:12px 14px">'
      + '<span style="font-size:1.5em;min-width:30px;text-align:center">3️⃣</span>'
      + '<span style="font-size:0.88em;color:#334;line-height:1.4">Tap '
      + '<strong style="color:#002868">"Add"</strong> in the top-right corner</span>'
      + '</div>'
      + '</div>'
      // bounce arrow
      + '<div style="text-align:center">'
      + '<span style="font-size:2em;display:inline-block;animation:ww-bounce 1.1s ease-in-out infinite">⬇️</span>'
      + '<div style="font-size:0.72em;color:#aab4cc;margin-top:4px;letter-spacing:0.3px">'
      + 'Share button is in the Safari toolbar below</div>'
      + '</div>'
      + '</div>'
      + '</div>';
    document.body.appendChild(_modalEl);
  }

  window.showInstallModal = function() {
    if (_prompt) {
      // Android: fire native prompt — user skips the share sheet entirely
      _prompt.prompt();
      _prompt.userChoice.then(function(r) {
        if (r.outcome === 'accepted' && btn) btn.style.display = 'none';
        _prompt = null;
      });
      return;
    }
    buildModal();
    var ov = document.getElementById('ww-install-overlay');
    if (ov) { ov.style.display = 'flex'; }
  };

  window.closeInstallModal = function() {
    var ov = document.getElementById('ww-install-overlay');
    if (ov) ov.style.display = 'none';
  };
})();
</script>"""

STANDALONE_RELOAD_JS = """<script>
(function() {
  // iOS standalone mode: reload when app returns from background after 5+ min
  if (!window.navigator.standalone) return;
  var _hiddenAt = null;
  document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
      _hiddenAt = Date.now();
    } else if (_hiddenAt !== null && Date.now() - _hiddenAt > 5 * 60 * 1000) {
      window.location.reload(true);
    }
  });
  // Also force reload on bfcache restore (back/forward navigation)
  window.addEventListener('pageshow', function(e) {
    if (e.persisted) window.location.reload(true);
  });
})();
</script>"""

# ── Hours-since-last-weenie JS (regular string — no f-string escaping needed) ──
HOURS_SINCE_JS = """<script>
(function() {
  var SHEET_CSV = 'https://docs.google.com/spreadsheets/d/1-NezoEWSZpeUIZem89ZMltE-kGX_P11LqKVoAwSG0gU/export?format=csv&gid=1814658863';
  // WW_LAST_TS is injected at build time by CI — always accurate at page load
  var _lastMs = (typeof WW_LAST_TS !== 'undefined' && WW_LAST_TS) ? WW_LAST_TS * 1000 : 0;

  function parseET(str) {
    var m = str.trim().replace(/^"|"$/g,'').match(/(\\d+)\\/(\\d+)\\/(\\d+)\\s+(\\d+):(\\d+):(\\d+)/);
    if (!m) return 0;
    return Date.UTC(+m[3], +m[1]-1, +m[2], +m[4]+4, +m[5], +m[6]);
  }

  function tick() {
    if (!_lastMs) return;
    var diffMs = Date.now() - _lastMs;
    var diffS  = Math.floor(diffMs / 1000);
    var diffM  = Math.floor(diffS / 60);
    var diffH  = Math.floor(diffM / 60);
    var diffD  = Math.floor(diffH / 24);
    var el     = document.getElementById('droughtMain');
    if (!el) return;
    var txt;
    if (diffD >= 1) {
      var remH = diffH % 24;
      txt = diffD + 'd ' + remH + 'h';
    } else if (diffH >= 1) {
      var remM = diffM % 60;
      txt = diffH + 'h ' + remM + 'm';
    } else {
      txt = diffM + 'm';
    }
    el.textContent = txt;
  }

  function fetchSheet() {
    fetch(SHEET_CSV + '&_=' + Date.now())
      .then(function(r){ return r.text(); })
      .then(function(csv){
        var maxMs = 0;
        csv.trim().split('\\n').slice(1).forEach(function(line){
          var ts = parseET(line.split(',')[0]);
          if (ts > maxMs) maxMs = ts;
        });
        if (maxMs && maxMs > _lastMs) { _lastMs = maxMs; tick(); }
      })
      .catch(function(){});
  }

  // Run immediately from CI-patched value, then try live fetch
  if (_lastMs) tick();
  fetchSheet();
  setInterval(tick, 60000);
  setInterval(fetchSheet, 30 * 60 * 1000);
})();
</script>"""

# ── App icon (base64 PNG 180x180 — swap by replacing this string) ──────────────
_ICON_B64      = "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"
_MANIFEST_B64  = "eyJuYW1lIjoiV2VlbmllIFdhcnMgMjAyNiIsInNob3J0X25hbWUiOiJXZWVuaWUgV2FycyIsImRpc3BsYXkiOiJzdGFuZGFsb25lIiwiYmFja2dyb3VuZF9jb2xvciI6IiNmMGY0ZmIiLCJ0aGVtZV9jb2xvciI6IiMwMDI4NjgiLCJzdGFydF91cmwiOiIvIiwiaWNvbnMiOlt7InNyYyI6ImRhdGE6aW1hZ2UvcG5nO2Jhc2U2NCxpVkJPUncwS0dnb0FBQUFOU1VoRVVnQUFBTFFBQUFDMENBSUFBQUN5cjVGbEFBQUJXR2xEUTFCSlEwTWdVSEp2Wm1sc1pRQUFlSng5a0xGTHcxQVF4cjlXcGFCMUVCMGNIREtKUTVTU0NybzR0QlZFY1FoVndlcVV2cWFwa01aSGtpSUZOLytCZ3YrQkNzNXVGb2M2T2pnSW9wUG81dVNrNEtMbGVTK0pwQ0o2aitOK2ZPKzc0emdnT1c1d2J2Y0RxRHUrVzF6S0s1dWxMU1gxakFTOUlBem04Wnl1cjByK3JqL2ovVDcwM2s3TFdiLy8vNDNCaXVreHFwK1VHY1pkSDBpb3hQcWV6eVh2RTQrNXRCUnhTN0lWOG9ua2Nzam5nV2U5V0NDK0psWll6YWdRdnhDcjVSN2Q2dUc2M1dEUkRuTDd0T2xzck1rNWxCTll4QTQ4Y05ndzBJUUNIZGsvL0xPQnY0QmRjamZoVXArRkduenF5WkVpSjVqRXkzREFNQU9WV0VPR1VwTjNqdTUzRjkxUGpiV0RKMkNoSTRTNGlMV1ZEbkEyUnlkcng5clVQREF5QkZ5MXVlRWFnZFJIbWF4V2dkZFRZTGdFak41UXo3Wlh6V3JoOXVrOE1QQW94TnNra0RvRXVpMGhQbzZFNkI1VDh3Tnc2WHdCQTZkaUU4SFlXaE1BQU5yY1NVUkJWSGphdFAxWHJHeG5saWFJcmJWK3MwM1k0Ni9udmJ6a3BidTBtU1F6V1ZsWlZWMit1NmU3ZXJxbkJRa1NCRW1ROUNSQTc0S2VoY0ZBMGd3Z1lGNkUwWU5HYWpQZDFlVXJ5MDJhU2svdnlldjk4ZWVFM2VZM2ErbGhSNXg3cmlPWjJhMUlna2xFeEluWXNmZmF5MzdmdC9DN1Avd3BIRHdFUUFRQWdCQUFSQ1NFNEdvSExFb3IxSW9RaWFoNUNRQVFFWWtBQUVSdy9taWVQL2gzOHpoNGlZaVFTQ3NGQ01EQ2tRRUFoWm01ZVVQenlRREFMQWg0Y0Z5RUNEaDd0VG1HMlFzSXM3ZmQvVFk0OU8zTnA3R0lpRUJ6WEFBb0lzek5rd0lnTENDQXpOdzh5Y3d4eGhoakNPSHdrd0FpZ3Q2TDk4NzdFR01JSVlyTVBtZitOaEdBRUdLUUVDV0lBQ0d5Q01uOGtKczNBNGh3akN6Q3dMSDVTbUZtRmhhT0lmb1lTQ2tDVkVTSUFNaUlaSlVtSWlMU1NwRld5cEF4aGtnVEtSUUdZWUhtUEl0QUhBMUhGeTVjMk5yYVhGeGFQZnZFdWNYRnBSQWlNMnR0ckUzcXFycXpjYWZUN3lWS2pVYTc3VTQzK0pCbWViZlRaMWVOcXhxelZhMlVldEE0VUJFQUlLQWkwa29mV0F3QzR0eHVRQVJ4ZHBFRUJlOGF3K3ovWW93d3Y5SXdOdzRRUUVRM3UzQUNzMThqSWlJNGUyNzJKa0daWDJNUlFRUkNRcUw3clE4QmtBNzk1ZDF2Ykt5aStkTDVnZUJkUzVrWkdZSXdBUUxpZ2NVM2I0Z3hOcFl4cytuWmcwSmc3MzBJb2JFZllRa3h4QkFqeHhoWlJMeVB3WWM2ZWhjalJ3YVFHQm14T1RnUkZnRmhFR1l4elpmZXRaYVpkY1RtdTRVaENnbEVqc3lCV2NvUWhFV1lJek56WUlnZ3dDeUFRQ0xBVVVDSUZJREVHS3E2MnQvZDkzVVlENGZiR3hzRzBkb2tzUmJCaXcrdUtvdlJ5Q2d5clJUWUY2T3hWdHIwTENVR0pTeGtLZHVXUnJuM2htc2N3OXpJQ1lrVUF0NTdWd0kwSnZLb1IzUFZHTEE1czNjdGIvNnh6WStidnh1UUdoT0F3NTREQk8rNTJSRVo1dGNweHNPT3FuazA3dVRnbWNaS1prWnc3enRuRmlhek53ak1ma3hqL00wUHVPc2FFZVdRWHlSQ2Ewa3BMYUpFQk9XUTE1ajdJbWIyem51R0VDR0V3STBIa3BuN0VaWWc3RG5HR0dWMm9WRUVHS0pJRkFGaVpCRUdFWkhtNmdnemN4QVJBR1JoRkVBUlpta2NIRWRtRVk0K1J0OVlhSXd4aENpc0Z4Wld1NzBZdk4vZkhSVGpJazFObXFTQ3doTEg0K25lenFDY1R1UGFjb2oxZER3SUllNk94d3NMeTdsUk5tdlZwUFZkRnczM1hwdDdROEpETC84WEcwZHp0ODF2NWJtWEYwRkVwUlF6dy96YXd5RUxuUjJBUUhOSDNSZHJEaTdGNGVjUEx1UmhFN2tudE5IaHcwVkJCZ0NtK2FFaWdvQ1N1K0dQQUZpRWlCclAwUVNYZXcyRkdqY0xFbWYzQ2draUtrUm1Ca1JqYkJEaHVTTnJqckM1SDJZL1FYanVtRGhHRVpFbzdHSU0za2ZISXVKallHSGdKbXB4Q1A3Z3g2TE12RXh6d0JGbk1WTkVtbytVMkFRN0ZvRVlvNFRJUGdnSUNudnZKZnE2ZE5XMDZ1UjV2OXRMa2xZQ0NZb2VEWWQ3Mnp1VHdUaFBra2dXMG1WOStQemVQWC96MFBERlJnQUE5TURibXF0MzRDbnczbHdBbTZ4RjVMQlJIajZHZ3dQaHc0SHFFWWVCZU5jNU5YOGVEemtWbkR1QUptTGhYZnVVUTRjMzh6cUh3eXZkNnpBTzVSeno0eis0MGlDemowQnNiQnhKY1JSQlFCRjFjRk1nQWdJUUFSN2tTUWVSY0dZdXpXSEZHSVdGcFRHYXlNeUMwTGdYWVlreHNJaEVudDBpekRGeWhNWWJBVE0wWWFtSmJqUDNqS2lhOEM4UVJFUVlHWXF5YUhWSGhyRFR5Wk1rV1Zqb0lNbkcxdTU0T3ZIT2MwU0F4TFQ2R3Y1VFBPNnhyUWQ5enkveUlLS1pKM2lZbzdyUGlBOWN5MzJaNzRIYnVNL3hIQTVBQi9keDQ3ZmovQU1iaDlkOEZzKzkxTUhuekMvaS9BK1I3N1ArKzZ6My9xZ3FoMkxlb2VNNThJV0VTSVRNTXJNaVFrR1VlZTdjNUVPTjU1QjVUSkltWldQaXVjM0VHSDJvR3p2RHhtb0ZCS0FPMFR2bk9ZcFJERUFvSmpVdGF4WjY3YXpkU2x1ZHZjR29uRll4QUpnMjJ5Vjl2OC80TWxkeDMwV1NMM3pQd1pXKy80bysyb0JrN2xRT0I0dUREem00NmdldlBtZ3VELzNEaDBmTXhsQVFVTzU2cjBQSkVQTGMxcHRRZU5nNFpwL1AwR1JDOS82R21kYzV1S0lQOGMwUDJQU2g2RE9yckJCQVdBUVlBQlZSazgvU3ZDWTR5SjF4bG04akhrck11YW1hb0ltWklDQUlGRVZDRE43eHp2Yk9SdW1Vd240bk14QVVvdFYyc1cvVHREMmRGREV5Njg0Z3BQOXBQTWN2Nm1idzBabkszVnJqMFFaMDJDYStvalYvVVY0bER6K0d3MTl4WDFsKzRIZ2Urdlh6Sy9zTEg4K2gwZ3p2ajh1SEhNL2hEQXdBY1BZczM4Mm5pWXd4ZDQ5T0FJa1FNUW96RzB3cGxHV1Jwd0N4cm9xSkswMldadTFPa3VacG1yY1NLOHcxWnVVUTlDejQ0ZnlMRWVoUVJCWkFnWHV1cGN3enlJZWNsQzg4QmZqbzk4Z0Rkdzk4b1d0NXFGVTk2REFlRERxUGN2bUhEMnhXV1Q4UXFoNXhPUi80b0FjL3VjbGR2dHEzSExpdXd6L25VUzRRRDVrTkhvcUdpQWpBVFR0blZtSWhJcUVDQlFLUm9rNXdZYm5MZ1M5ZXVqQWFEVHJkWG5BK3lkQm93a1FUb3BaVURRdmRKUElCWjFVVGlCQ2lTSk50VWRPSFVnd3lONHVEUE82ZW5FQ0VDVmp1di9nczg1QThUKzdpNFI5NXR6bHhYNnZsaTJMQmdXTy83ejMzM2R5UENpNTNlMmpJQjBmQjh3UzRTYkVGN3ptb3hoTWNYTGtISTlyZHF3VjA5NXJOSTB1VHcrSzlpZitzbS9LbEh2VFJXUmNpM08wNUFlRGQ4d0RNTW05S3dFRUZQZ3R6SUY0NGdtU3RuRVFKR0FaczU2MVcxbEtFaEtBVUVSR3gxdHJxdThVa29XRkF3SWl6SHhhSmlVRXhvdEJkai9jbDNrSG1ubkJXc2NuQnpmV0wrLyt2N2p6dXRqVHVyY3dQU293SG53UjhJTGcwMTQvby9wY08zRHMrbUN2UVBYNmU3OCtzSDh5S3Z1RFJXTjVYVHZ0QUh2YnJEcG5zZlZFU21CbUprQkhtblRlbHlCakR3cEdqbXYxQWFJcG5FZFoxWFZTalNkcHJFOUprZnh5RTAyNDd5Uk1RWVZjektrSkxJTUY3WVNackFPbkJBNDJJSUlCQ2pCVFl4MnJLSWpaSkV0S0JveHo0akVNVjdPRTcra3RQMzMzSjNVTlAzK0Zld3FPeWgza1RySG1XNWlZaXMvYkhyRXNCSXRRVW5FMEpUSTEzRVg0dzU1MjNqdW1nRS8rb2tJY1Bjd0ROZ2ZEaDZITTRvWG1FLzdqZlVjSE0wY25jS0djV1NRU0lnc2l6SmlJSzBxeDNFaUpwNVZ3SUFyWGo3YzNiR056YThjZFVyeVZFWEljb1V3YXRMNy85enM2ZGpaZCs1ZlhoY0RqYTJFR2pJTW96NTgrUFEzM3IrdFhqSjAvYjVkWEI5dTVnZXpjU3JCNDdtdmU3Zk9obkhMNFhCV0IvUFA3MDBtZVhiMTRSNWlNcnE4K2VlK3I0OGxyVENNTkQ3NlREL2RKZjFuOGN1SHI1cFlwbmdURC9lbXlhZGNLaXRCWVJBa2FjUlhFUlliaHJtak1mZmJpbytVLzNPR2pWZjJtMS8xQmJ1ZTg5czNDRzkrZFdFbGxycmEycEtrZUVrZXZkM1UySXZ0M3ZwWjFFQkRqR2lKNVo5R0JyZDNCbkhlcnFremZmUExaMjdLa25udjNlbi8xRnBnMjEwZ3MvZWZmSXd0bzRiRno5L01MUzBxSk9VOUt6alBqd1NLeHA4eExBL21qdzNSLy82S2Z2dmpXc0MwYXdaSzdjdXZNSHYvTTd4L3BMS1BlTVBMNGdManlxOFhVNGs3OC9YWCswSTdtbktwNG5PU2drSUtSMVkxOGNtWWdVME43MmxvL3h5TXB5WWtnQlRTYmp3bFdvRkpETzBuWmlzam9Fams0aFJNRkg1Y0tQY2xkeVQzMHhUenNla3IvQ1E0UFI0ZFB5WUs3ejBHTG40RTltMHdLUUptejRHSTFOQkxHb2c2RFNTaU56akV5a0VCV0xKMlJpQmNpNnQ3Qlk3dXhoakZ4VTlYU2FLU29IZTd2Ykc4ZmFwM1NJSnNacjc3NjNzWEZuZWZsclZpdWp0Q0RJb2Z5QkJVUkVBWGpoank1KzhzTzNmekwxbFRFbUVucm05ejUrLy9IalI0Kzg4VzB0czR4M1BrRkYrTEtBOG92Nmc0ZmVSdmZrdG93QVRJbzFDUkx1N1crWGRibTd1VDNZMjl2YjIzZEZ0YkxZWFdwM2JyODN5Yk9rbTdXcmVwcjJzdEw3d1dBaW9sWldqajUyOW16ZWFsVjFFRElzOEZVcTdZZjJ3QjVXNFh5SkovaUM1UFErQTMzNG56ZHBJQUtIR0ptUmFEeVo3QTJHTEtpMUFhNFFVR3RMcUJBQ2trS3hRYUxHR0FDaWJlVlBmKzJsd2RiT2hZOC9ITy90THZhN0JNTHN3bVJ5Ni9OTGViL3RYWDNsZy9lZlBBOXJqei9PZ2lneUw3K2I4U3lVcnY3NHlvV1JueVJKSXNLQ2dBb2R1T3MzYjFSVjNVa3pCcDZWeVk4K05ZZC8yRU56eVM4OVgvT2NZSjRNeWF6TktBSUtsVUlaRDNjL2ZQZnRHOWV2MzltNHZiMjlReUg2MnE4dHI2d3NMYmJpSWt4M2I5KzZZUW5PUEhicXpKbXpXWjZmN0xiRDZuaXdONzUxNStKSFcxZU9QbloyNWVSWlZ6czBMVUFTNEY4dUxzcC9oSEY4U1hWenQ3eVdCOGNYTVFZUkFjSHB0UExPS1VXRUpDeUt5R2dOd0lnQ2hGRVVDK3ZSY0ZSTXAwTHFzU2ZQcmE0ZXVmaisreWZPbmozOXhKTjNOamVDOXhHQXNtenQySW16Wjg1ZS9maXo2Y2FtT25zbUNJRE1KMnJOaUpCb1hFeTM5L2ZRR2dVVVVKb2FtRFFWZGVXOGh6UURRU0ZzK25icVlUL3Z3Vk9EWDlqTWVERDVPUFFTenhFQnJFZ3BSS1dvTHFZZnZ2LzI3ZXVYUG5qcnJhdlhybFd4N3JVNzdTVExiVjZOSit2VDhhY2ZmaEFJZXYzZTN0N2VEOS81ZUcxMXVkM09qaDVaTy8vVVk0K2ZPSDEwYlhsOWZmMTczL25UcDE3NityTXZ2VTRZQWxOVUpNQUlPRzlINGhjSHU0ZTd0RWMzVHg4VlFiNDRIR1BUUkJWQkFFSzVXNWloUkk0QVFNb1FtV1o4S0NDUkdRRTFFUUVqc1pCZ1lDV2lWZGJxTEs5T0sxZDYzdDNjU1h2OXJ6LzdiTDYwTlByOHN2UEJHenp6NGpQanZmMk45WTFlcjk5ZlhJd0lrWUR1SDhVak55aUV5R0lSQkdoVzk2SFdtcFFDd0ptUHVhOGFBNUJIbFBWSU5CdFMvY0lwSnpaaFZ5blNBdFBKcUs2S0d6ZHV2UFd6bjZ6ZnVqd2U3dTV1NzNybmtrU3ZMUFpTbFl3R0JhdHcvTWt6eTJ1cjE2L2Q0TXB2YjIyUk5hUEowTlYxbWlTWExweDg1Y1h6cDQ0Zk9mSFk4YUlhdi9PVDd3NEh1Mi84K3UrTWhxTjgrUlJwRXlOL3hSRHdTL2lEQnllaitNczJCUTdTYXFOMWxxWktLV1lCZ2VEOURLMHhTN2hGSTB1czlUT3Z2Z3dRbEZZczBGdGJ6dk5UMlVLdjlISDE1TWx2L043dnRwZVdGaDQ3dVhWbmZWcFdwMTU0cm4vMG1EQmFBQUcrMjhrVWlNSjVscTMybDYvZXZsMmlWMVloZ3lJRWtUUk5nQ2d5TUlvUUtrUkdFQ0ppMGZNcDgzM1ZIUU5NNnJJb0MrOURKMjkxVzIzQ21lMGZydjBPdkF1QklHQUVCUmlpc0FLZGFDdm9kblkyTG43OCtVY2Z2THR4Njhaa01xMktxYStuZFNoWk9FL1R0Y1YrcHMyUkkwZGVlR0cxMisyOC8vNzdkKzdjUHJheS9Qeno1MTk1OGVsTDE2OWR1SEsxMzEyZGprWWZmdmE1Q3l5aVRwODk5MXUvODd1cksrLzg0SWMvOHQ0L2ZmN1ozVXVEcytlZVoxR05PYzh2SVFsNEVKejNkL0FMN3ZqRGc3MHZUak1mQ3JFN2ZCNW1lZTY4VzlsQW1lU1FBMjZBYWtRRWlERnk4QkVBbUFPS0o2V1JqQWdoS0ZMS0JWZU1kblRTNndFeVJrWWhtM2VFMEVjbTB2M0hUaTQ4ZG9JNUFzdkpNMDh3TUNzQWxjNUx4M3ZtSUJxd25lWmZQLzlDTVozdWp2YjN5N0ZvaWpFQzR0cktTcWFOeElnR2lyTDQrTXFsd1dSRVZtYzJUVWt2WkszSGo1K3l4b2hJRUc3R1I2TmljdVBPN2FxdWxOSURNMWpzTHh4WlhsWE5ETy9SOXgrTElFQnFFZ1d5ZmVmYVJ4Ky84K2tuSDYvZnZMTzN0ZTZkTnpZeHFFMlNFWVQrWXErYnQzMlEvYjBSa0wxeGUvMzZ0ZXVqOFZnUjNieTkrZjVubHhZWFZ3TEsxdDY0azRURVdtdXlLNWV1NzI3dmZIYnA0bS84MmplZk9IWDg1WmRmZnZPOUQ1OTYrdXp3MXRYTHZqajN3cTlXTlNPeDNJc0srTUtCN1M4OHJQNGwzTTk5RCsrOUNGdVRCQjlHbzFFSUFRUjhDQXJBR0lPRUlBU2lBWW5kZUxwOVdVT01jM3RqQVpBb0JFaEtlUklHTUpFUU9EYXdSUUNNd2dnOHEyYnZabFVSUkNNOTg4UzVvMnRIaHNQaFgvNzBCNS9ldUd3UVcybCsrc1FKYTdXdm1kQ01pK0YzdnZlOW05c2JOczh3Y0Z1YlgvMzZxMGZXamhpalpkNURaWkd0bmUwUUFpRnBwVnp3WlZsV2RkVnF0VGp5ZkpKMEtHL0ZXVFBJcGtZaTdOeTVlZkhUajk5Lys2ZlhybCtvUTNCVjVldEthMTNWa3hpZzAycWZPbmwwY2FHL3RiRzl0Yk5kVkhGMzRxWmxNWmxNb3BmSVBvRFR1cnl4TTZtRE4wclYxZVRZMm1wbTdMQWE3SStMcXpkdWIvOFBmL1Q4MDArLzl0clhCZUN0bi8vMDVlZWYzdHk5czdOK05lc2QxU3BIakJ4Wm9namRMZWdPZzA3dUcvMGZvRU8rdk4vMWhUMzF3OG5vL0E5eFB0S1pBZW9hMUJJaUtrV3VycDJ2QlFRUmxMRFNXaWNKRURZTktDUkVjU3JzNk1hNGVUWlR3OGFCaTdDSkVKdHBMODF1U3dRRUZPWVozUGZCSVdwdXMzd3BPN2F5ZG5Wbi9kT3JsNnRZUFhmbXlWTkhqOHVzUWFlSUZDUFd6T3g4TE9yblhuemg2Nis4WW8ySnpBZlkwS29zaTZJNGV2VG94WXNYSjVQcDBhTkgydTEyVlZYdGR2c0w4bjRDdWZMSmg1YysvK1RhaFU5M045ZURyN1ZLdHZjR2tmMVN0NDhBVlZXemtXTW4xeDQ3ZHVUMnJkdTcrL3VWOXlwcEZTNE94bVh0b3VjWm9yWDJFTUVEU0JXREFpaHVyVnVsU0ZFR1JrMkt3U2pjV3YvZWg1OTlwcEw4eXZVYjEyN2NldkdacDNCNCs4NzIzdWxuWG9tK2dCZ1FGRUZDU2pQRWgxWm05d1BWSGowaytvVUFlSTg0Tzlqa0xFMXZub2hRSVNBb3BVaFJNMG9qSktYMURMWkhBZ2pHcWs1SGFUNkVDdVlHYkFLSVJCb1FFUUp3aUtCbVBSU2NZUVpFQklFUHdYWmwxc2NGamt5QWlUYVR5V1NwMi8zRzh5OTNzbmFNRVFrSkdWRWlTQlRHVUNlSmV2SHBaNDRzTG9OdmNFdXpjeVpOalJGamxxWldtenpOUWdnQ2thQVo0dDh6TEVDUnhLclJZUC9IMy8vZXozLzAzWDZ2dTlocjE1blptRTYyQmdQbllqdlBCSVFsdHJ2cGlhTnIvVTVuYTJ0emEyY0hsT291TEJXVjNMNXgxY2VJUkV5RXdpSml0ZXEza2xZcnIycGZPNjhRRVNPSUJJNCtNb0VhRjc2OGZxZjJrcVoyYjM5Q2RmM0NVK2VHbSt1VGhkN3g0MGRycndzbUJoMnhtZE1RUUR4d3M0ZjdWUGUxK3g2S1JIbXdwZkhJY2hjUFR3c2JsekZ2V0RZWU9lSEliTFVoUVVJaW9nYnFBYVNSd3F4UnhzMTlUa3FwTkZmNm5weEdCQlNPeS9MVytyb0E5SHU5SXl0cnhtZ2YvSFF5cnIxWGlnUlJFQlZDcWt4bXJGV2FoUVBQYmhGVUJDS2p2VUdtOUcrLzlxM256andsMG94a0JTQnljTnhjaWVpN2k5MFRSNDRRUUp4ZFpVR0FHR09XcGNhYTlmV041Y1dsWHJjM0hBNUdvOUhhOHVyaFFYYnpId29wTmVyeXBVOS8rTVB2am5hM24zcnl0TFgyNnRWcjE2N2ZHaGZUTkVzVytzc2NZKzJLTExkblR4OWY3SFoydHdhNzIzdFoxdG9iN2JUYjJXUXlpc3hOMmRmT2t0eXFZOGRYY3B0NlYwZUdzdkozdHJmTElpQnhNM3B4dnNpVHhBV3NQZnZJbFhjRWN1WEd4cC8rK2Q4Y1dWMTc0K1VYVjNPNGRIT3Zza3NtTlFDMVFpVU1RbkpnMWwrY05EeUlHbmxVV0RsNDlUQ2NTdTdwQUtBQUl0TEIvUlNZQlZHaHdobk1ySEdVQUVpQU5Lc3RZZDZFZ01qczliMGxJQ2pBL2VuNHo3Ly9kK3NiNjkvOCttdC84RnUvWjBsZnZYUDd4Mi8rYkh0dlZ5c2REWkpXV3V0T2xpKzBPaWRYanh3L2ZyeWZkNXRHdWxHNnJNdFVtZi84TjMvdk4xNy9sVmFhaFFhQUp5Z012bW5QSVdxbEFWVm9icUQ3QVNOd1pIWHQ1dTNiWlZXeXlIUTZYVnhZNlBXNk1VUkVuRSsvVUN2bGlzbFBmdnFqdi83T256NTIrdGpqWjA2dTM5NzgvZzkrT0JyWFFKd21TQko5VmFGU2lUSFBQWG5PS3RqZEdlMFBKblVkZHpjSFVUQ0VNQm1QQ1Nsd1hPaTFqcTcydXEyODArOE1kL2QzOWdiNysrT3FqcUFJa1FKckh5SmpCSW1nRENrVFEzRE1KRENjaU1iSlQ5LzZZRzF0eVZQNDJuUFBaTjJqdW05UW5QYzE1bDFXV2dFZFpFbnloUWltTHloNnZ3Qk8rNld0TXdTTXdqTjBMVDEwUEk2ejdBY0JHTENwWm1LdDUvNktHckFjS0IxajNCN3MzZHJkcXJ3WFJUYzI3dnp0MzMvL28wdWZWekVnQUNoUmlwaFFLYktramRKblRwejh6ZGQrOWN5SlV6b2lNQnRydi8yTlg3SEdKTWF5U0RNNUJBRmhLaXRmZW9jQVd0bmQwZVFIYi81Y0N4eGJXTmFKYVNKK1kvYmR2SDM2c2NlcXVnN0JkN3VkZHJzRGlNSjN5VTQyc2NYKzloLys2Ly8rd21jZlBmZk1VLzFlN3dmZi9lR2RqZTJxcXJxZEhtbE1MUmJUU1YzR3hlWE9TK2VmUi9EcjY1dWpVZWtxdjdtMU55cnFmcisvdHo4c3loSTVyaTcwVjFkNnJSU0xZcnF4dlZ2WHNhd2RrT3EyTXg5Q0ZSek9odDhJU3FabDJVb1NSZ1JGTEZLRTZBZFR0YkswUFp6KzYvL3d4My8zM2UvLzgvL3NuLy9EZjNTbTA3WHZmWHg1ZDloZVBuVXVDbXVnQ1BJTFFUZnVEeXR6WU1YQjZPVEFsUjZld3owVXlDSUF6QkVFQ09sdUlYR29WNjNJYUtXYkhrZkR0a0FRNUtqbmN3Y1JFRUtzNjNwN2E5dDdiNjF0cGRuMmNQK3Zmdmo5dHk5OGpOWm9iUUdFVUVpaFFxV3NJYVBLc256djA0OGh3SC94Ky85NHBkV1B6S2l3Mys0SWN6alU4aEtFQUxJL0d0WjF6Y0lCaEFsKytQYlBiOTI1K2JXbm5udjJpU2VYVjFaeWs4NndzQUI1bXJYVG5BaEJJTWJJSEhBV0lTRko3R0IzNDd2ZitkT3RqWnV2dnZ4Q3E1Vi81Ni8vZGpLWmlFaTczVmxaN1k5R3hjYkcxblF5T0hKMCtadXZmbTJoMjdwMDVlcDBVazJMRXJWZU8zWnN3WE5SRklQeGtBaFhWMWI3L2U3bTFnWVppeUtEL2YzRUpHUlZ1NU12ZFBzYm05dlR1Z29Sa0RRS29pQWhoSVpURUlSRkNJbUI5NGFURUUyM3Z4U1kvL3lQLy9DNWMwKysrUEx6dHk5K2VPTHAxNFVqNDZ4Ry80cjE2aGZNZXcrSUYzSXZmUCtoN3psRTRRRm1GaERkWkJGeUQxMVFrU0pDclRVUnlSeWZHUVBHU0xwcGZ3TWlFKzZOaGg5ZnZQRERkMzQyS3NaSzBjN3U5by9mZmZObkZ6NE1GcEVZV0RRaU50ZFpzY1FvQUtreU9zZExONjlmdVg1OThkbGVreHo3RUE1OWZUTU9wUWl3dnI5VDFaVWlDcUdPTVhpUVQ2OWR2clYrNTgxUFB6aDM1dXdUanoxKzlzVEpoVmIzVUIyR0xFeElERkVRRWJSd2ZlWEt4eC85NU1jWFAveGdaYkZENkgvMjVrKzhxemxLY0s2VHQ2bzZGRldwTlAzS3QxNy8xamRmVThnWFAvMTBzTDFyakRsMjdPU2tkTHVEOGZWYnQ1eDNvYXdYRnhhT0hUOTYrY3ExL2RGRUVFVkVhMVhHS0VVWVRjcjlZUUVjNWt3RkVRQlNaRWlGRUwxd2swYUJDQkpPdlNjbnJaaTJiRDR0eG4vMFozKzJ1WDVqL2RxTkoxLzh0b0JvUVdJSnhETmdzSHlsbnZyOWpZMDVuKzh1T3Y4Uk03YkQyZTZCandreEtnR0ZKQUJCUkZDVW9obDRERWtyYlNoQkpFYUJDQ0xJVEJ4WkUySlU2QlZldlgzcnAyKzkrZkhubjA3S2dwUlNpTzlmK2l4ZStkekZRRW9GSHpTU0lrS2twbkJnNXVaQWlXZzZuVjYvY2VPbHA1NVRwQjl5eEFKRXREK2RYTDExczZ6cmZ0Wis0ZGxucmRhM3R6WUdrOUZvTXJtOGNlZmE3dGJQUHZuZ21UTlB2UEhTMTU0NGZpcFZabjZPbEFpajZCQ2owdjdUajk3K216LzV3MWlVL1hZZW5mL0JEMzZVNUZtNzNmS09WNVo3L1g1L01oMHRkRnZMajUwNC84UVRPc0tWcTljR084UEZ6b0pudkxXNS9lbVZxNE5Sb1kxTzAzUmxwYlBZNzkyNWRXTTRHaXBVRWJncDFDS3ppd3dFcnF3SVVDdUZKSWlndFlrOFp5S0pJSUFoYWtCeUxzVFJGS0lmVGZPcTE4NnUzYnlsSVh6enRkZWpMeE9ldXNoUklWTHJRY0RwZlVPbGgrSWR2M3FYN0tGNVNVT2dFaEdhZzlZRmdCQm1mZ2RCRVNtbGxOTDNrSG1RQWFMVzFoYStldS9paGIvLytjK3UzYjRoekNheEJDTENFY1E3UnlGMGMwdGFsODRCQjVYWVdlOVBnR05EeVF2OXJKTWF5ekZxcFIrRWRqZW44dmJteHZVN3R6VFJFOGRPL3ZQZi9MMkZibTl2c0wrNXUvM1J4Yy9mLy96VGZUY2QrZXJOajk5ZlgxLy9CNisvOGJYekwyWTJhU2l5RFliSmFCZ05OOS84OFEvMjErOTBlcTI4dTNUeDBoV1R0bUlFVjllZGJyZmY2d3RBWm8xdzZLWkc2dnJtMWF2RlpIcGk3ZVQrL3ZETytrWVYzRFBubml5Y2l5RlUwOG5heXRMZTNtQnpaMThSQ1FBUklzejRTMGFSZ0FBQnpVQ2dnZ0Fva1dKa0FVRkVBUUkwUUJFaUN6T0M4MUVCdFhKMWUzc1lmU1RocDU4WkhxTnBDd3NGTks2Q2FhVklpWWdRZlRrYytvdTVGNCtDT0IybWJSNys1QmdpQ0pCV1RUc09VU0ZaUkNXQWhBcFJJY0VNWk1xenNoZlJvNHI2MHNhdGp5NSsvdU1QM2xuZjJ6VjJoamNtUXFWc1pNNlVmdXJVNldlZk9OZHJkMjZzMy9ueE8yOE82M0lHZXdjQWtlRDlFeWNlKzlXWFh6OTU1SmpXOTdnTk9jQVZFd1htcXpldkQ4dHBtcWJuemo1eGZQVUloM0JrWWVuRTh0cnpaNTk2NXNtbi92UjdmN094dDJPU2RHTi85eTkrOEYyYnBsOTcva1VPUEovd1NUWGFlL043ZjdkNysyYU16aVM5U1RXMVdZcG9Sc014S29yc2RuWTMyNjEybXBnMFNSWEpyZlZiWlZrZE9YN3krcDN0VHk5ZVpKQ0ZoVVhuZy9jK1VUcnZkMU5yQnNPUjFvUUVJZ0xNaUtnTVdaTXdjMUhVV2dHSXNJQTFoamtZSWxaU2hVaUtqTkVoc01Sb2xBUUFZdENLRk1oNFhKWlYzZTEwTHQ3WWVPdjlEMS81eHZseTk5YVY2N3ZaeXRHbHZHc3c5ZmpJT0hLNFd2bGkzTkFqQ1IrUEFEMHg4NXh6ZDVkMk9HK0ROQ2xxUkpCRENIa1JZQUhXLzhPZi84a25seThVMGRzOHc0aW13Y01vUlVaWk1OODQvOUszWG5tMW43YzEwTG5ISGxkYWYrZEgzN3Q3SEFoR20xZWVQZi9pVTg4b3BlSWhhRGtLRUNFUVJtWVJHRTdHbDY1ZDhjR3ZMaTQvZGU0Y0NEam5HS0hKNUY5NTV2eTBtUDY3di95ekdHUFN6b2JGNVBzLy8vSFIxZFdqUzZzeFJDU1NXTDcxays5Zit2QzlXQmNtMWYxKzM5cGtmWDE3YTNOOWJYVTFTYzMyOXZaaXY5L3J0WXRpR2lQc0RmZkxvang5NXV6RlMxYy8vUHp6Z01vZ1Rhdk53YVFvblQreTJEdi83TG5kblczblhMZWJSV1pGNUp4VFNobGptaForbm1nUTZiYmFSVlVTa1FoNEwwVlJKb2tCUlRFR2hhSVVBSXRSQUFqTHZUeEwwdjNCS0xWNmMzZUlITjcvL01ZUGZ2VCt4Kys5Rnp3LzgvTEx6Mm0xZVB4eHBBeEVtQjVPbHZtUEhKMDhGSFg3cFdBNUFRQlFPQU9jQ2lBSk0wZEFBZjNKUngrdkhUczZpVzU3ZjVjU1ZzYWdNYWhJQWI1ODd0bHZ2L3FOaGF5TmdWbWl0dWJFMFdPcHNSTlhHMk1hMzJXdFNXM0NpaVJHRkR4Z21RS2hGOTdhMjcyNWZtZDdmL2ZXeHVibk42NzUybWtpRmlsOHJSUVpBUkZoQXVINDdCUG5UcDU2N05yR0RhUFI5bHEzZHU2OC9lRzd2L1g2cnhza0FuNzdaei8ra3ovODl4WjhucVhHMmlSTnQ3ZjNON2UyejU0K25SaXp1N2V6MU8rZE9Ibml6cDA3TzN0N3dOak5rbU1uam0zczdIOTI4VXFyMWZZQ1pWa1daVUdFQkd4eVBSanZiVzV2Q2JJeEpnV2JKV1phZ2pFbUlkVnV0NjFOQk1HZ1d1ejFSbVVST1NKUnFPSm9PaGxPSmp1RG9mZFJDMm1qSTRuV3ROQk84aVNKTHZSYTdmRjRGS01uWS9ZbTViLzlvNy9lM3RyT05Cbk5KMVlXbVhEcHlGbUZOdDVMN1g1d0RQc29IT1I5eFBHSDBxNE84NFFSc2VIeTM1dmVIaVE2akFvQVFlbFVHY1BDSWdoSUFrQ2lTRkQvaS8vc0Q1NDUrK1QxemR2Ly9aLzg0YlFxclRGRXBBRVhiZjYxWjg0dnQ3dGMrMW1WZnhmUXk3T212UUF6azdvSHV5TXNqTEE5SHJ6eitjY2ZmZjdwbmMzTmFWMU15c3BISWNUYm14di80Vy8rOHVYbm4zM2xpYWVQTFN4empERUVBdDFPODZWZS84YWQ2MnJXdnFlUFAvdjBwYWRlUEw2NjdNZkQ5My8rMC9GZzkrWHp6K1N0MXEzTjlmWDE5VTgvdlhqcytJbkZwYVVMbjM4V2tTUEN4NTk5Rm1Kd01RYm5RVVRXQjVzN2V5ckpBOEQrYUZTV2xTWlNpTlpvSXpnZGpFRkNmNkdOcUJOdHRFZ242U1kyeVd6YTcvWGFlU3NFdjl4ZmJPZDVGZnhvUEJhRVR0Nk9Fais3ZlBXNk1kdjcrK1BDeHhnWmRSQ3M2cGducHQvdlozbTZ0NTl0YjI4eWg3b29OOHN5K3BCUzJ1MHZXZUlWQkt1a1Zrb0ZGSXdQRmlhL25PZVlvNTdwd2N3VURqbVBReEM3Q0FCSzBjRWYyc1Jxb3h2Y3VERE1HVVpSZi92cnJ5WGFNa3FuM1I3dEZJcklHS09ZcmRJZG5TZ0dKbUlRUUZSYXNaQ1BJQWhDd2h5QUZJTXl5aGdrRHd3SUxFSks3WTRHZi9Pakgvem92YmVMV0ZxaUdCbEpWQXpJRWpoOGZ1V3phM2R1N0d6cy92NnYvdHB5djZkWm9hTEl3aHk4OTk0RlpaUzJ5WDR4MmQ3YmVlem8wYi8rcTcvODdOMDN6ejErdXR0YjJMaXptWnI4MG9WcmFaTDF1b3QzdG5jOFFBeFl1Y0pvN1lPTXgxT0puTnQ4ZDM4d0xrcjJ2Z3d1Z2xpcjBpUXhTdVhHdHRMRVd0WHVyQVV2YVpJWUFjMndzcnFrU1BXNlhVVE1qRzNsK1ZLL2YzUjVlVzh3V04vZWJyVmFuWGE3OHE2VnBZK2RPSEgxeHMwYmR6WnViMjY3VUVPa291SnlVclR6WkhHcGYrTEVpVTQ3MmQvZjU4QW9XRktWZGpydmZuS3BLTXRYeC9HMFR2SzFFNGcyUHNEd2VOUVE3bEc1NXoxL2duaUE1NkJEQU9hQTJMU2s1L2JYMUs0QnVJSFFBNG9pSWpRS3RWSW9nQnhFU0lnVWdZQW1wSWJOMzFqVHJKb1dBY1JHbFVEa01QWHhmcHk3TWxxUk9rQlVFRkJWVno5NTk2M3YvZXhIcFRDd3o3UTVjK3JVem1Dd3ZiMXo2dVNwZHBMZDNGd3ZFWDc0NGJ0RlhieDQ3cW1WYnQva2FTbGhlM2ZIK3lBY05TdlFpbG04OTNWZHZ2ZmVXOHRMaTh0THkxZXZYSFVoVW1KQ2pFbVNiRzV1Qm00VWRxVGY3NDNINDhIK0VGQ1dGNVppaUp0Yk80SWFPREpJcXJDZHRhM1JJTHpRYVdlNXlYS1Raa2tJMGtwYWNWb3RkWHNuVGg0dnB0UEZoY1Ztc0dDMXRsb25TWktuYWN1bUsvMGxwSmltMmhoYTdpOHVMeXllT0hyc3M0dVhQNzkrcy9RZVViSEF1S2pINWNhNHFJNnVMS1JweWpGQ2pCRjB6ZjdtcmRGMDZtN3RqSis2ZFBXTjMvanRvOCs5TEpEZ0w4dksrSUorK1gzYUU0MElTcU1VTlhmNTl4TVZSRUJyclpRK0ZIWVFBV0lJbXBDTTBrU0VtcEJVak94ODNUQzlVYWs0bytOZ0kvTWt3a2lLUk0yR3RDSUdxTkc4WWhGa0FJMjNkamJmL09TRGtvTm9VZ0ZlTy8vSzA4ODkrOWMvL3Z1aXJQL0pyLy8yMGVYVi8rOWYvdkVudDIrQWhwOTk5dUg3bjMzYU5qWnZaMlROK3RhR010cVF6bXlxckIxendSQTNibDlWeEZtdmUrSEtaUkZneFAzMW5jQThLVXZsZllnUlFkSTBIWTZHdzhFd3NZa3hCZ0UzdHJlTlZnM1kzQ0ptVmkzMDIwM1RvcDNsZVo3a3JVeUpkUHJkR0dMUzZoeGRYbDFkWEE3ZEJhTjFraVJKYWtmalVTZlBDYVN1eTh6cWRtb3JOMEhDZHBZWkNsbGllNTNXeWtKdmRYWHB3cFdydDNmMnk4QkJ3R2kxdFRlc25UdTYwcmVJRWFoeW5qM0h3SHZqcVZnOUhYOHdtVTcvb05kZmV1enBNb2grMkRqdGNKUDBVUVh0L1hPNE9mK0dEclcvR3VXcSt5aGhzMkppbnFTSVNJUUlTRXBybUwwS0NNSWNBb3RHQUVJVWJtRGF4QUIxOUxGMmQ4Vkpacm1GRU0raWhnSU5JRUlpVVJDZ2tlbGhqa29vY2x6ZjN0b2U3cXZFZUIrT3JoNzUrc3RmM3g3dTM3cDk1OXpKeDU0OWRiYlQ2UncvY3ZTanl4ZkJlMENGU2VwRG5JekhnM0lxaHRwWnJwVW1VZ1Fvd2xVNWVmZnpEeWVEUGQxcGtWTFRvZ0NrNEx5ZzhpSFUzZ0Zpdjl1UElRNUh3enhQKy8yK3I5MysvbjRJSWN1UzFObzBTVEg2TERVTEN3dUdkS3ZWcXFzcVM2eWxwTjl1STRBUUgxMVpYVnRhTmtvblNkZDduMlU1V1ZVRnA3UkNBQjk4djlmVldtbldRbUFVYVpzeWkwbE1xakhQa3RYKzRzZFhybHk0Zm5NNG1SS2dpSnFVYmpTYXJpMTBiS0k2UVJDd1VwWFc2RXVYOW5xa3lROEdjS0pHSVVEOVMwRE12NGhpZWJqRE1RZk9QZUw5ZUZjbXJVRWtFellTYWdnaWtYME1tb1ZGd01mQUxFZ1VRZGc3WDlWTmxPRkRDWTJJTlBKV1BuaHRrSkFpUjBRa1VnMElRMEJpalB1RFFSMERhcTBGZWd2OWtTdCsvTzZiZFZHOC9NVFR2U1RiMmQvYjNkbUpaZFZaV0hqamxkZWVPWGwyb2QzWkt3Wi8rc1B2YmU1dlowbHFqTkZLaVlnQitmQ2RuNFh0emNWdVp6cWRGbVdwdEFZa1ZBb1lhK2RBcE5mckcyUDM5N2FNTmd2OWhjbGs3R3Jubk91MTI3bE5VMjJYZXQxRVl6dkxXNjFXcDlOR3dMMjkzWGFldFZ2dHhKakIvbjZ2MzIrbGVhL2JOVnFVMHBPcHE5MVlpNDJ1U3ZQTVZRV2g1SGxLSkZhYkNCeWF4a0dNaGpCTGpOWDlidDdxOVR0NWxuNzQyY1Z4RlpBZ2VEY2NUcGQ2N2VXRjNuUmFLcVdOd2hnQ0l0VmxqWUZIKzd2OTZkaDBGbjhoMXR4WDZwWWVJbFJHWnZrS0FsMEVoTmcwdm9sUW9qQUFSR0FmUlRkaU1MVnpnU01SSVF0ejVCaTExa3FwUmptUlNEWDI0Wnp6M3NjR053Z1FmV3k0L3dmQlNoRWRzSUVWMGM1dytEYy8vdUZubjMvMi9Ka25ubm44aWEzaDNnL2VmL1B5amFzMlNkNTQ1ZFYvL091L3VkTHRLNkszUHZrd2h0REwyLzFXeTJxamxSYUFhckIzNS9xbHg1Y1h5eHEyZHdmS21OU1lhVms1eno1SVdmbCtwOXZ2TFUyblkrZkxKTzBXaytsa05MSFd0TkkwdDBsdWtvVnU3OFRLY2l2VldaSjIydTBreThhVDhkYWRzclhRVyt4MTY2THM1WG0zMWJLWkJTV0t4Q2hJclM3TFVrSElOS2FHZ2loRDRPcFNVYVlRRURCRWlSRmlFRzZHRUFDZHpENjJ0cHlsMWhqMTJlWHJHL3VEbXFYMnZEZWF0anQ1Szh1R283Rk5ySzlpQU5qWTJ0ZlJ2L1RTUzcxK2YreG5WS012YldjZDVnay9hbzZQaHlMRlFlL3JzSFRNVEFxeThTTHp3SUlBQkNSSU1uY2REV2FMUVNKbVdpRVZWWG50K3JYSlpDSkVQRTgvalRHTlppakpYUTJRRUlMM25rbm0wbDhSQ2RRY01ZUU44RmxFZkFBQ1J0Z2JEVzdkdkxIVTd2M0cxNys1dHJUODJhMXJQM3p2N1ozQi9ybXpUMzdybFZkWDJyMEljbjN6enQrLzlmTVl3dExDUXN0WVFIUWhJUE4wWjl0d25BN0hkN1kyU3VjWDh1N2UvcWdvYWhhdTZyb3B3S2JUeVhnOFloWm1uazZuUkpSb293QzdlYnZmNnB3K2VXSzEzMDZOT3JLNllwUWVGK1Z3YjMrcHYyaVVXdWoweG9naHNkMXVSMnNOSWthYnNxcGlqRm1XTmZmQXRDaGFXZHBxdHhPVEhHZ3lJVGVoUFBnWVFFQnJnMFNXNDhtMVJZQ24yM24yemllZnJ1K1BRaFdHNC9HVkcxVTdheUZSbm1aV21WRlJGY1BKZElwS2tUQTNZaGNBLy85U3lKbEZscS9NQ2p0VSt3QVJvV1E2ZXZmQnRhdmZmL2ZkeXJOT0ZYQWswcWlpVmxhUk9laldJQUFKMWh3WUdVbUNORUJhUmdRaUlVSm1CQUNsVksvWFEwUWZJMm9LRXZNOC80MVh2M24rOFhNTXVMSzY5dFRaY3pyQ3QxOTY5ZFRLRVd2c25iM3RuL3o4NTFkdjMyd3ZkTkxFR0tJUVNZR1VlMXM4R2lRMkdVM0dvMUVSQUdyMmU1TnA4S3kwcW1KczZhU3VLK2VLc3E3eUxJTVFnZy85VGdjUTJsbTZ0ckJ3ZkdYbCtPcGl0NVVib203ZVlZN1UwcnMyNlI4L25tUTJ5N09pbkxSYTNYWXJ6MXV0UEUxR3d6MGtBaFptZG1VSk1TYldoTWlwVGZJc2Q4N1Z6b21JRXVUU1NmQ2t5VmlqdEE3ZUs2MjFNaWRYVmpyZFhwSmxiMzM0MGViMmZoM0RZT0ltWmNnVFk1TWtTOUkyQUFLbmJkUHVXVXRNb21hVXNBTXN5d1BrcmtkQlRmRUJERzhURy9DUUNDNERrRktIVlBNYWt0Q01Nb3dLbVVDSWhVUnc3dXliQVRyb0FFRlVTNzk1N2ZPLy9ONzNyMit1MnpTQndJelNaQ1hXMmdjNDRORTVGMk5FQW1CZ2xycXVoZmxBd0JVRWllajQwYVA5ZG1kenNHZFVna0NkVm43MjhjZDdDLzJJc0pvbS8ralgvc0h3L01zbmpodzFTbCsrZGYxN2IvL3MvYzgvSldOMG83WUpTQUNKZ3UzUm5nUW5LR1ZaeGhoTmtoYkYxTlcxVFRMblBVUkJGb2dSVWJJazBVYTdvbHpvOXRwcGhzQkgrc3RMN2M1aXI1MGFaYXp0NXEwOHo2MjFWZTNXMXRhbTAwbkxwaTJiK2l5M1NkSk9Vb2hNRGVSNkpvd0xXdXNzeTNxOS90N2VubmUraEpLWmpURWlMRUpwS3ZWb2xyREhNQU9heEJpTjFndUk1NTg4V3dkdnpKV2QzVUZaVmo3R3diUjBibU5sY2FuZDZYUVRZM1g0NUtNUEhqLy91blJhQW13ak1yQVFmc25JL2hmMEdZM1c0SmVtS1NJOEUvTnRoczF6OUUwSWdLRDF2LzJydnh6dkRaWVhGOFpsQVN4QUloSVIwR3F0a0JxVUNKRmlabEVZQ1Qwd01VWUdFQTRpRSsrbXpnc3BKSURJbytsa2MzK1B5QnFkTk9qRXFxcmUrL2lqbGY1aWYzRXgxM2E1MzIrbjZkNTQvT2JGajkvNzVLTmJHK3RzdFNIaUdJU1psVVpBeGV6SFEvUys4TDUwSGdoRDhOTnhjQjYwRW94Ums2QTRpM21XWlFKU1ZlVnlwOXZ2dEJSZ0wrK2RXRnRaYk9YZHhPYldaQmJibVVhT3dMRXNKcDF1WGhaam94U0JaR25HTVhKa3JUVUtXR09iUU16TVNaTFVkZDFnK1oxenpOeHF0WklraVRFNkgvTGNSazQ5TnlJbm9oUVJZZ1R3ZFFuQ0xVMlByU3hYMDJtb2E0bE9DUVNHeURJYUZ5YXhsblFFZGZIaTlmVTdOMWZQSDYwREFxSWl4WE4yMHk4MGJMc3Y1emhNZXVDSFNSWWNxQTF3bzVHTkZGRXJ0QVFhQk9kU0pjTHNRMEEycVI2TjluLy9WNy9kN3ZYLzNkLytwZmRPbzBaU3dKTFlwRUdpTi9EREdHUEJjYjhZQjJDRkdrRlFnS3pkR2crLzg5Ty9mK1haNTFzMkxTYVR6MjllKytqSzVmM0pSSk1CN3dBZ0FMejl5WWNiK3pzblQ1MWFiSGRqOEh2ajRhM045ZDNCb0hiT0dLTlpsTWFJWFBtYUVSQW83dTd3ZEtxSlhBZzJTYXE2QmlRUjlDRkdIeEJFYTh6enROdHU1VWxXVkVXUzVRdWRianRQTTVzczl4ZVcreDBNZnFIWFhWbGJaWEVjZmVtaWMwNDRKbHF2TGkwbDFpcUZ2VTZuZHM1cWc0UlZXWFU2SFdzVDU3MVdPa1RIek43N3lKd2tpYlcyS2RlMTF0NTdSWmluYVJWbWVwL0dhQmRDNDdoRERBQnFzZDFlVzF3Y0YyV1FXTGhhYVNQTUJtMDVMV3BFYk9XVFNjbSswc2hlRkJNMCtKZ3ZtSTM5WWdyQmMraFgweGg5RUZjMjE1UlRpbFFVVWFRVjZidTZjeUFJVVZoSXQvU3ZmdjNWMy8zVlg3OTA4NGJFMk9DUkc5a1BhMjFUNkpNUUtiV3h1LzNEajk1LzcrSW5FWUJBQUJ1bUFrU1VOei85NFBQclZ5eHBYMWFEOGJqZDdYempwWmRDVmIvLzdydlJLbVdVQjc1ODUrYU43UTJqbE16dU43RktXMk1Va2tFaUFNOFNYWmhNUzhWUjluWjhYU2RhZzRoM3RTQ0dpQzV5QXcxSnJVMFR0ZEJiV095MG8zTUwzWTdWcXBWa2FXSzZlZnY0MGRYTWFtSlpXbDdXU21tVFM0aWp3VlNVdFBPVzgyNnh2K0NEanpHbWVXN1RKREkzamVBa2ExdHRqT0dHT3RWcEt4WnU1Ym0xdHE3ckJwMTdJQWdXWStRWVp0SVh5TVlReGhnSWdDRjZSNENKdG91OWZsR1h2RDhJSWttV0pkcldkWVhBcGEvYzN1aWROMzk2K29XdmEya0owb0VxNlZlMGp5OVFrY05HeW9mNUFJcjFJRHFrc1dPdEZCSUFpdEtFQ29FUXNPRk9FZ0FIVnFoUy9jKysvYnRyaXlzZlhicElRQWdVT0tKUVJpcExFcTIweEVnTjY4V2F6eTlkdm5uN1ZwSW5NMklUSUFGcUlHWFVkRG9kVm5WTEorZFBuLzJWVjE5LzhlbG55N3FHS3I3NStjZElyQlFhcGFtaGZDTmFvR1pzMnhSeUFSZzQ2aUNocW1OWkxDYTJuaGFHOUdSU0dLMFJzSEl5bUpSVkNBSmd0T3EwV3dUY01scExURks3dUxSZ3RUWkVpVGI5ZHFmWGEvYzdYWTBZWTJTUDJpYXNJRTlUYXhKbHRROWVhZFZrNDRDZ3RGYUlXdXU4M2JMR2hNbzFaWjZ4U2FwYXRTc2pSMk1NRWxWVnBiVnVOTFZDQ0FDU1dGMFdoWmVZNjVZd0U0aFJKRUxzdlVac1oxbGVGSzAwOWExOFVybklzYWhMcFJRSFQwSXF6VzlkdnhsRys5VHRjaVNFSUkrNDVQZnBzVHd5ck1COFd3SkFGQWt4UGxSaGNXWWNDQ2lvaVlnQU5Tb2lwWkdGQlprUkNGV1U0TUdDN2Vpai9TVU5TQXpkUEhmQnM0L2dCV0xVTXdSV2szM0Mwc0xDYXkrL2VIdjM1cWdzbE5LTk9yL1JHaUxYdFdzcCs5VGpUNzc4OVBrWG4zNTJzZGUzU25lejFqLzl2ZDhYd3A5LyttNGdNSW5WMXBKcTFoU2dDTEJ3YktCSWdPQmpXWlFKNkpmT1A5TWovYk9yMTdqMncrRzAwMjRiYmFweVZJY0FJZ25oOGJXVnBYNTdmMiszazZjcFVhdlZYbDFjenF6VlJJbld5d3VMYVdhTk5ubVNHcVUwa1ZJS0lkbzBUWk9VaGJ2ZHJvamdQTmRUU2pYdG5LYVZWMVpWVlZWcGt1akVBa29FQ0NBU0F3SVlZM0dPM1c1MHd4UXBiUXdIOU43SEVGazRoaUNSTlZKcUtEY3FTMHluMHk3cUNpb1hRa1JtamhFQ0IyQkR1cFZtM25tTkVJVUJmMGw5anZ2N0hBZGM2VVBsekNNK3JXbDdLSUFnN0psOUNMV0F3cmtnVHdTbDdhTDJJaExpVTZjZi8xLzkwLzhpeE9qTHV2YTFkL1dwWXljOHg3bkVrNlJLdi83Q2k4YW85ei82WUdkL3R3eGVBSlZTclRSYldWaDg3c3k1cHg1LzR1alNjcWEwc0xDQU1KODZzdll2L3ZFL1BIcGk5YzBQM3RzZUR4cDllWVVVaVNLSUQ0R0JHNUc1bEpJVGkwZGZlK21WTjE1ODdxMGZmSzhxcDhJOEtTdFF5aUpWZFdRR0RYQnNlZkhwMHlmN25kWjJtaGlDUEUyT3JhM2xOc216UEUzVFRpdERwTlFrUnBrWW8xRXFNblBVSWdxMVJCU1RKSXFvcW1zRUFLWVFJeW1GUkkwMHNRdStZV2ZWd1FzaHhRZ01oaElpRW1hR3dCeVpJeWxsaktGSWRWMUhINnhXTGdSZ3BobDhpaEVrTWJyZmFSZDFPUzMwMEpqRXFsZ0xOMFIwYTBRRVNVMnIrdmJORzQ4dm5RNXlkMC9EQVh2MndkbktGNnM5MzArV1BXUVo5MEVQWndVdElKR2FBeFlwQkE1TmkxeEVCSDFnNTVGVlJ5TmhaRjVkV1QyeXZFb0FFWUE1Q2dKR3ZnOGszMDlidi83QzExOSsvSmxSTVozVVpXQVBBTjI4dmREdGRmSzJKUVVnUGdSTnM5bzZoTERhVy9qSDMvcU5GNTU4NXZQcmwyL2N2TEc3dHpzb3B5RUU5dDRTR1pQMHV1MGpTNnZuVHA1OTV2VFo0eWRPakxadWYvY3YvenA0cjR3V3BxcjBRVUVRWnBGT1pwODdjK2JFeXJKQjZaMDg0Y3VKVFpMRmJqOHpWaXVkWjFtcURCRW0xaEtSMFRvRUR3QzZ5WndReWVqWTdJVXhEVHcvb3BjWVkxVlZZaTE3cDdST2tnU0praVJwZXNHTnBIVUlJWVpRVlZVSWRaYWx6RnhWMVV6bHdwaHBXVFFGUzNNUE5XSGVoNXEwV3V6MUpsVTlMaXJubzNjVE5rQ0kxaGl0dFNhYVRxZEtLNlVVUm1rUUxBOXRneDVjK3kvbkt4eHNDSmx6WWg4S0l5SnFlRzRId3JVa2MyNWtRMmNPbm91cUtqMHpLajBUL283Y3RFME90Q2hSVWFPOWNmZ0xGS2psWG4rNXZ6aHJob2lJaUNKaUZnNnhhY2I1K2NoSFFKREJrbjdpK0trelI0OVBYeWpHNDlIZWROd0liNWpFWmtuYTczVDYzWDQzeXhWU291M250OWF2WDd2Vzc3VUNzMk1PM3FjNlVZYXNpMmVPSFgzaTFOSE1FZ0NrU1pJdUxxZ2dtVXBUYTZDWkI0R2thVW9pVFlJVlJZd3hpZ2dCbGRJMnlTQkdZU2JDSUZFcmphaVNKQ0Vpamt5RUVhVDBUaXVsclFHV3FxcnFxbXE2TEdRTUVKbzBDVEUwNmZRY3FUdXpudWJTYXExRENER3lVcVJSUWFLNjdVNTdQQjFOeTM0bkw0b3BJeWlGeHFoR0w3M1kzMU1RUkptWkJ2NjlNVUllRUxXOVAvZWNhWlBjdmZJeTN5cDFHQW4yRUdlRENuR212Q1RDMVBUUGhCU3FocjVVbFZWWiswaHpKZ0Vlc0V6dUlWN2UzL25uUnBOWlFpUDZCZGdnQnVaYlMyYXFPbkpZMWJXQkZTaWdYcnV6ME9rOU5vTzZJc3d0R0JHYW5VZFZWZS90N1d1Ykl1akIvaGJQMUUrUVdKYjduZWVmT2RkcFRJTW9OVFkxbG9nVmNsTmJOVm9saUNRZ0tCSkMwRnBiYTYweFNpa2lqWXpHSmtUZ1E5QWltQ0w3b0pTS01WWlYyVEFTdlBjMlNRUkFJOFVRbkhNaVlveXBvM2MrOVBzdGNSSTVXbXNSSVlUZ25FY0VyWFdNUVNsanJURkdUNmNGSVJJcGhhSFRTbnVkZkREV2tldHVwek90cThieEpDWXR5NUpEMEFRU0FRUitJU0dQZ3cxVk0xRG1mUjB3WnEzMWwrY3VoNVlaTVVmdmZhT3F5SkdMc2lqcmlsdW9Ed2p5YytiTVhVMnR1elBmdTJ6K3V4cUxEd0dsZlpFU2dIRGtJRUVqSVpGR1VvZ0N3TUlzcy9VaTF0RHU3bmFVdUxHOU94aE5tY1VvUlFDVzZNenh0V09yeTBhZzRld1pVdUFqS1VBbGFXcVlJY2FHSjg0c0ZKaTExbHJySkVtYWthRXcxMlZWTm9KRUFOS2trMXFKU0F4QmFkME1xVFJpNUZoN3o0RE5BcDRtVjBVa2E4eDBVbUpranRHSDRKeXJxZ29RSThjMFNadWRhOHhzclczbE1KcE9mS2hCcUdYdGNyZnJuRk43NkNNbmlablc1WFE2clIwUVVGMVZXbW4wTUJOR1BsUnQ0b01pK1UydGNWaEo4dDdHUmRPRVo0N041cXY1TW8ySGxqOE4zL0Z1YjU1ajlLNVJFNVlRUWxrSHh5Q0FUUVBrN3B4bVpvZHpoT044ZUFQejlXeDNWZXdiWGNzNUVScS9JaENoQWNrekhXWjVOenN0d0dwRkNPUHBlRG9wWFJUU1NJaUN2TkJyUFhIeWVHYXNDdHpJVnNVWWpiSmFvMUlrSWtyTlBLUnpOV0t6VnBCQnBLb3FBdVc5YjQ2aDhSTktLWk5ZUmFvQkJoeXNaOUJhaTFLVmQxVlJSRklJWUsyTk1YcnZHOFdDcW5TK3JJWEZjeUNrVHJmdm5LdnJPb1Ntc3hDVlVpemM3QUlUa2VDOEtEQWtDOTAyQXUyUEIxTlg1U29WaUNGZzdZcWJONjZDTUNHUkVCOUlaVCtrb1hub21ZZk5XZVJnSHhRQ2d4eGV1SEhmTXJLNWhRa0lOWnNVbXFHTUlrV0FoSVRBUHZqYUJXSUZncHFiUzBzemVkRVphUmkxZ0tEZ1lhbmVaalRmTUNybEVKRDU3dGJHZVJ5U0E4M2lBMHVhWnlGTmJQUjhjRVBNQXFkQ1ZFU0xTMHV1ZGpGRVVrU0VXaXVOc056djl0cHRpcXlKQkhtVzl3SEhpTTQ3NTMyV1pRQU51NFNiMjFlVWdIQ0lVYUZXUkZyckdLTnpyc205R2tTajk2R0IyaDRzS3VBWUpVU0ZGS0svV3liTWVhUWNvNXJIU21hMlNacm4rYlNZOXZwOVFobU9CdVBSMEh0dnJXbFExa3FES0xCV2RTa1ZnVkV4YnZZbWFhVUp3VE51YnQyNWRldGE1L2lUNHZnL1JobGVZdE4wd2tlVk52ZHJhaU1KZ0NLYUZTeUMyaGhVaElDRUZHS3N5aEk1VTRENlQ3Ly9kelFqeENtam04MlVtQmdpUlpaU1kyempvbzNXQ2trcFJVU0tsTktxT2MxS2tCVE5sa00yTFRZRVFqNkFEaHpzOW10Y042cURxQ1NOWGplTFJBSXZvUjdzRHllVHZKVWJZK3ZBQk1JVVhSUk55cEJpaVI3aW5QZ0xFUmhRTVNDenFCaHNralF4cmxsOUZTQUE2c0RPR29Rd1c5Sm1FNXNtcWJGR3BUYUdLQ3d4Q25OVWlwQ0lZeVNsRElEM3ZvSHpHMk5za3FCRVRTckdpTWlvMlB2b3FtbzhuYUpKNnFvYWxWTzFjV3RwY1hteDF6MzEyS24xMit0VlZVVUVsb0FBSXBUYXhKS0FVbmUyTURDWGRTWE1JT0lpTUFyVkpVYmsyZGp5UzFaQk5LWFFnK08wSnRnZ0tZNFJCTlNCS3N2RGRoZk5LRVVnV3BOV1drREFnRFdXbEJaaFlQSXV4TUJBZ2lqNjMvN05uemNBMU1QN3pSUXhJU25VV3B1R1NHbVV5c2dZYTVWUzFwcW1kNlMxTnRvWWExSmxqREV6QzFNNklhMk4wVW9yclF3cG94cEpJVkNFWkpwZkhuMEkzdm15TEl1cTJpL0x3WEM0Tzl3WlhyMlNwU25IVWdOeGNNemN5dEs4MVdKbUg3d21wYlVDa1Joanc3b3oydGpFS0VWR0tXQnBVb1FRUWhNUmxOYk5PYTZxV2lsbHRFbVNCQldsYVJwOHFJcUNpS0FCelljb0luVmROOWZBV250STBCNFBGc3lDUU9BNEtxZjdvOEcwOHFQUnFQSThtVTdiclZ2OVR2djB5ZU9KVGRKV04wU255QWxBQU5Hb1NKRkVsV1VaalBhTk1URUVWOWZkYm5kcGFZa2dZdlRTYUdQQ0x5a3ZKeUxCZTRteDJYejdwU3orWnFlWFVxcTVveEJRRzlNRTZNalJPZCtRMXdGUkl6V2lPNDMwVXZNRktIRytCbUQrdjdteUxCNG9mVGJLWWpPU0pVRFRqWjFSSWRTTUVLR05NYVFJa1daclBJZ1VLbElDTVVidlF5aXJxaWhMVi92SXpBVExMTm9tcW5JWWF1WmdDZkxFTG5UYVNzM0JzTTJHdllib0R5d2MyRVZyVE8wZENoaXRqZElOblM2eEZnRkRaTVRaMnFLbWhBRUFyZ01LSXhFU1JzL000bUlNZFgyM2JVcUtqQkpFOWdFa0lpRVFPT2Jkd1NBSzd3MUhvOG5VQmFnRTlxY1RRaHpWZmpqZHVYYjd6dkxTOHVPblQ2YldHRlJKb2lsNmhRUUtkZVNXMVlaSWtmWUNvbjJXNWtxbGhCSTVDcGlIN01kOG1HYUxRaVNsNE41QlNlMjVMRjBqa0pRblZ2RVhyejBCUkJLSVJHU05hWFJaRUVVZ0NITmtxQ3NmSTZ0VU1ZSU9jckJuNSs2eEVLcERSY3pEMk45ei9ZK21ubW0wb0NLelJCRThrQlpGcUFCRlp1MFdQS0RmS0NKdUJLaUVBQTBaSk1VUVBWU2hiUFo5TklNdVFraVNKTTNTaHYzUW1HdGo0ODU1Qlp3WWc0aEs2MVRycXF4OENGWnJhMjFpTGFtWmRMR1dtVlp1Z3hiTDgzd3lIaC91S1JHaUFvTEdiaHFVQmpORUpxTUJJZmdZQUlmVGNWMjdhUjMyUnNQdDNkMjZkdE9pWmtJbVd4WlZsQ0pOck5GMll6Z00xMldsM3pteXNwWXBUVEVnb2hKb0pVa3J6N0lzSDAwTEZySFd4c2hYTGwrK2NmUGF1UlBQeFhqdnJpQ2NiVWIrb3BVMjg3SWxoRENjakVlamNjTXVTMWRYRGl1UEh1eDh1WWYvMHNqM0lDcXRrSWc1Tkh1TUFjRTdYOWQxSS9NaVNIb21wRFNMUml4enpUQ1ErUUs4QTFMMFBkcWo5NjJCSld4ZVZ3Q0NhcmFuUkJwU2ViTzhqbEEzbTBzSVVLRnU1bmtDd3NJaFJvaXhaYzFTWjNWWVZtNDhzVW8xTGt5VGFtVzVvcWJCMGZnQUtjdENRTnA1cnExcFFna2c1bm5lYk5va2JiUk41aFpKQ0tRVW9TS3JyUGRoYjNlM2lTQkUxUFJDRUlsbmxUQ2cwc3hlSUFDaWN5RzQ0SnpiMkJzUHkzSTBHZS9zYjAvcmNqeVpEc2VUeWpzWGVUaXVGV3FUR0FXeDA4cVRKTkZsbGVmSjlzNW1WV2E5YnE5UmtraU1XZXozKzZOeFdaUzE4eVhYR1dOUmg2Mk5XOCtnRDZCbmRkTnNXZlBEVnlrY05CQU9lUHFJV0VmZW0wd0hveEVDWmpZSnpETVErUVA3ZUE4THRqWktUaVNzNXZMVEJBUUFMc2JTMXhFWUZSQ3lmaUM1dld0NGNwOEUyY09GaXc2WTJZY1cyOHdPS001YUo0cUUwY2Nna2NreEtRS3RRV21yS1RNNnpkUGVrZDdxNHZKang0ODlmdXpVbXovOC9wLzh1Mytqd0dtTnBGUzMwMjNsT1NLd3pGS0tvaWdFbUJTRkVEeGlqQXdNMHFoM2EyM1RSSWhDakFTb0ZDSUlBNHNDWWhaQ3o2RXFDdS85VExxbzFXb0k5aUl6WDZpMFpuWWhDbUFZRE1lVjU3M2hZR052Zkh0My8vYkcrbkE2WUlnZ2FscjdPdm9rN3dTcnZZZ280OHZweUkyTU5VVU1aUWdMV1hyVTE5MTJ4cXdpa21MczVWazNTellhaWxuRVVGZldZREVkczZzWlVpS0FleWxIWDdTUEZFRmdOdWt2blorV2xZOU1xS0tJODNWa2JWQXpQSExMM2N6T0NLd21EY1FFT0x1NUlVU3V2WXNTTEVTaXFBOGZoOHg2c2dqd2xUSHpENjRReFh0RVpJWEllMzk2N2NRVEp4NFB0Vk9DV2lscmJaN25uVmErME8zMCsvMXVwOVB2ZERUcFBNdjMxOWZUSkxlZ3ZLKzB3cVdGQldyVzJRa2dVVm5YUHNST0oyOGlVck9YelFYbm1hdzJIRVFwZzBDTWlqazJBWStJd0pIU2l0bjcyaUdwTERjZHJmTThUMnlDaENHRXVxcVlQUURVVlZtNXFpanJzcXIzOTBjRnk4MjluUnZybTFkdjN4bE9DMlUxS3JXeWVrd2xETFhMRjFkeTBzNTU0WWhKUGhrTnhrVzF1WGM3MW5VblRjNGVXNTQ2ZWVMRXlZV1dKcUpPWmxkNjNVOWlxT282czNaVUZNaGdiS0swUVo2ZHNxK2lxRC92VGJLSStNQ2o4YmdzcStiWkVFSlp1bGFhMnNUQWwrMU1SY1FrU2JVeG5wdjJQd0NBODk0NXI1QVcyaTNWYjJtQzJZcm9Kb0Znc0FDQzJPZzJhWkhEOVRIS29iNzZ3VUtOUS8zU3hqRXlVRHo0blI2NG84enYvOHB2ZlAyNWw4akhpS0NVVWtpS2lKUUdRZ0ZtOEFhSVEwU1FKRTJiYkNQRzJFclRUcDVxbzFRRXJWU01NYkNBMVlQSkpJYVk1Um1SRW1hcnRRQXNkQlBVdXZLaHBWTXZJb0JhUUh6UVdqTkxDRkdUMHFCTk85ZG0xajgxeGdKSFlWYUtuSThpVWxaVkZXUlExamMzTnFZMWYzang4dFhOellnSW12SzFJOFpZSk5NOWNzSm9QZGdmdGxwNUVLVnNFSTRrWVdWNXBTeUx5WGc4SFkzMmRuZS8vL0cxSDM5ODlZWFRKMzc5MVJlZWUvTHNRdHBhYWk5bTJreTA5aUdtYVU0cVRxWkZaRURFQnI4Z2p4Q2N2TzllUE1nZUtoOUcwNkxaZWNDRUljcDBXdWVadHcydDVJRmQ3dmM5ak5iR0dGL1hCRXFCaWxGSzV3T0ROY2x5djl0ZjZXcnYvZDA2ZHI1b1o1NnZ4VVlKYWRiSloyaFVrcHUxTHZQZVc3Tk44ZTVTYmdTQzJRaUhSWVNxOE0zWFgzdnAzTk81U2NUT1BRelB0cVkxV0VkU3lGRklxUkRpOFNOSFR4MDlmdW16VHdGRksxVTdSekNuK0JFcGdPMjl2V2xabG1XcHRjNnozRnFUcFprMVJxa3FTWk5FR1NNQkFvaElZcXcyS2lKRTc0VlpsQWF0RTdxN2ZqekdRQ2hhYTFTdHFmUDdlM3RKbG5sMisrUHE0dTJ0VDI3Y0hOVmhjZTNFNHVyUmhaWGwwYVJZWEZwKzlwbW52L2Y5NzE2L2RUdlZpWGVUcUFnVmxjVlVZbjMyOUNsbEZZTmtuYTd0OWxyN2U1UFI3dWQzN295K04zMzdrd3YvK0xmL3dhblY1YlhWMVVGUnhkcGxlZDVwNmIyOXZhSW9kTjVxMUEvZ2tFd2d6c1lCZkc4dGVvOUdiMW1XWlZITVptTE1ERmlVeFdTaWxBUnJiWnFtRDEzNlBOOS9DTjU3N3gxek01OUNaZzdlZzRoSlRidWRMdWFaZnZueHA3ejNUUjBmbVYzd3pybUlFcGs1UmhFSnpGR1lRNFFtcVcxYXNBZ0N3TkRBaWdCRk5DbFdJa29hcFJ4RUJCYU45STBYdi80N2IzeTduZWNJSVFLUUtEeTQySGR6RkFJRktCQmpYRmhZN3ZSNlB0WjVtaWdRQzZxdXFqeTFxSlRuT0MySzhXaGFWRlVWSGZvWVFQVnRVdFRPczBTZXltalM2WFNuUG9KQWxxUkFxa2JXUUNSTUxFekFIQ2ZUc1NpdGFwVVkyMmxuS2pXWWtJNGtpSmlhRXZuQ25ZMmZ2di9CUjFldXEvYkMybU5ubno3Ly9PcmFVV1krZS9hSmwxOSttUWh2M3JyOXdidnZreFpoaWh5VHBOVkowOEQxZEREcDlGdXR6SUl5UnFsdXBzTmFkMjk3TnpDc0Q2Yi96My85eHk4OWRUcnRXREpVVEtySmRtV3hqOWdMcFZPcEFFb2pLSHQzYTA0REFuMG9lVm9Za0JocFdqdm5BNEtna0NCR2dDckc0YlNNTVN6MXVtbWFnakROOXE3UEl0RmNKb01GTVVMZ09RaU5oV01RN3hpUXROWXRrK1FKNmYvdFAvK2ZoaEE0Y29naGh0ZzBmQUtLOTk0NUYwTU1IRjBNM3JuYWUrZHFGMElJZ1lWOWpIVmQreGlDRHk0R0VRN3NYYWg4aUVLb2xGcnVMVHh6N3FtWG4zcjIyTktLbXMrWEc0anEzV1VjOXlkS2pBQTJzY2JZTE0wU1M2MVdxeW1HUkZOWlZOYzNOMGVEcVhkdVVwZWtWS2RkTzJIdlBTSVpOTTY1VnF0bHJWVktwOGF1TGZkNzNaWUdBb1lzU1prcEtCUUpta0lWWTBnem8wQ2NRMk96TEFWdHJtNlAvdnFuUC92MCtsVVgrUHpYWHY5Zi94LytqeDk4OUxsNDZQUTcwNkxJK3QxQk9UWTJuM2hKdWxtb2lyS3NkR2RwWjFEdTM3NXBPK25hOG9vaXVuYnRxbmZlS20wMDJjUWtOcW1xc3QvdDcrN3UvUDBISDlmUmE2UC8wYSs4UE5qZnZYYjk5dExxRW1DRVEyQ3dlNGNtZ0k5SVFCQ3hybDFSVEdjcHB6UkJId0U0ZUU5NWtpUUpJVDZxSjlaOGNwWmxTV0pEakVTRUFGWHR5ckptWVdPTXRkWmFvNDhzTGQ2akVYTzQrSmdyM2pkemtUakRDelJyM1JxUk9xNDVObDNiWmlqb3ZYUGVNd0lSdFZxdGJydVRhdFBZTFNDcVJrMEdaa3VONzkwM05ZdFpScWxmL2RhdmZ2cmhPNjZjdExNdUloSnBpUkxKWDc1MjlkYkd6bUJVMUw0bXJmcmRibFU2Vis5T1hlMGpsMVdOaUs2cWpkYXJxMnVaVWR1N3JhTkhqeDAvZGt4OGpCU0RydU40MGtxTVZTUWlObEV4V0ltaGp2N0hINzMvOTIrK2YzdFE3azZMS3RCb1ZBeEs5K0dGeTI5OCs5Zkx3Zmhidi9iRzIrKzg5ZDU3SDlRQldsbHZVdFU2eXlSQVVZNSs3Vi84Z2FMdVgvKzMvK2RRRU9ZZFVyWWNqN2QzOXpOckZHRzczV3AxMjU0akVJNG1JeCtnMVdsWHhYamp6cDJYbm52cTZPcngyNXZyRWdFVlJvYTdGMEh1cnVXT2MrSjh3NCs3T3hJbnFseVlsbUV1elNIem9FTXVjRk82Q1dxRU9LZkMzNDhrYWlZYlNxc0QrS256VmZBT0JhM1JXV0lUYTNTRWVNZ1dIamF3bVdGUlFDRVFJcEJxMGdwQ0ZKRFl5RC9nckdVbUxJaU5VdTRzVitVNWcwSU9TSldIbGpQaEErVjQwNE12aXlMNktzUldaRFltMFpvMmRqZnVyRzhNaDlQS3hiU1Y5dnQ5VjRmMW5mM0F3WW5VUVVabHJaVTJTbW1GZzl0YjdjeTJCcU5yNnp0TE4rNjBFb3NJdlg2M1plajQwcExXdWlvck81Nk95K210cmQzM1BydmdsZWtkT2JFNTNZM09UWWRUWkxuNDRjZlhMdDlhK2orMTkvZDMvL0pQLzlXVnk1ZHRrcjcyK3V1blQ1K3V4NXYxdE9JSXhpYTdXNFB1Y2crVGRPbllZMCsvK3EzMWo5NHhKckZFV2h1V0FBb0pLU0d0a1k2dXJHNXNiUFFUM1Y4NWZ2M1dscCs0TjE3NytwbFhYMmVrS0F6M3JEUEh3NU42UHJoakQvRVZtYUgyb2ZZUkdGRkRtcVV4b3ZNQkJBR29xbHhaVmxwYlJZZjBKdSt0WDd6M0xJeUlJdHlNekVMd01YaXRLTEZKWW8yMVdqZTVKTklYNlN6UFM1TFpTakNZbzV5YitvUkRqQWZ0c2daSTFzZzNORXNXOENHRTBBZmxKUTROZGtnWmsyUlpHV3FPb1poT29OOHJhM2Q3YzN0YWVlZkRZMmZPdER1OTdhMnRXeHZiZzJtUmQxdWQvdUtaazQ4LzhlVDV2YjI5MFdoQ1dycTkxdGI2dXA5T3grUGh6VTgvM2QwYnROS2t2N3lZNTRrRkVNR2lLSFoyOTB1SmxaZm5YM3oxeVhOUC9mQkhmejhaand4aDdaMGh5QlRXMC9GLytEZi9xdFhyL04yZi9kdkc4aTk5OHVQLzZ2LytYNTQ4MnJ2MGlSbVVreXpQYm4zd1h0YS9EU0JrYk9Wa01wME1wbVVUT2FsUjF4TE9zeFRxNm9rakswK2ZYQ1dpMGFTY0RzY0J6RnR2dmZmdDMvck5QRzlGUUJJZ3dOaHdHQSsxRys5RGdza2NhQjQ0T3U5aThGRkNuclNXRmhiSzB1M3U3Yk9BSWlycWFqS2Q1bG1tRE41ZDcvcUE4MUJLcFRacHNIeGFrZmVoZG9HUXJEV2t5ZWlEclFuM2k0ZktGek9yRHJkalVTbDhHRytHNW9SdStUTFZWVG9FSFJJRW03ZTZ2WDZzUys4OUlJdnc1dVptV2RSb01wdVpHM2MyOTBhWEFIQmhhZW5vNlROcGFqdExxMDgrLzdXako4NU1pK0w0MFdQckcxZWVPSGVhZy9xYnYvamIvZDJkaGRIK3FicTZmT25pNXQ1KzIyZEtHUUYrOG9rbmYrT2ZQUGZ2LytqUG5qdjkrQ3N2dlBMV08rOFdrMUdybFE4SEF3R0pMR2hNZjJseFkzdHJLVGlsakRJazBULy8vUGwvOSsvL2VEU1V4R1paRm9LWDQyZFBMUnc3dm43bDUyNjR2WDNwYzR5ZVl3UmtocWdZalpEUldqaWVQMzNzYTA4OTBXbTNkeWVUSDd6MWRxZVQ5cFo3Tnk1ZC9mQ3phNy8yTDd0alFDQ01Jc0tpQVNQS2JHaDl6K3JyR1Z0VUF5T0NqN0dzU29Gb3RPcTEyNHU5L2dnSHc0SFVnUUhSc1F3blJhL25FcFBlMjVhY1lVdG5DelVZdE5LSnNVWnJRdkVoaE1qR0tLTVJLUm9GZWw1YThsZmtWSDExVGQzRFdNaXYzbEhqeUNkUG5IanUyZWZlblE1ZE1RR0FMRTJGY1RpY2JtM3REYWNsS094ME84dkx5MnNyeXlKUmdKVEFkSC92MDkzOVRxZHpZclg5eC8vKy8vUDFWNzd4UC85Zi9PL092L3p5OHZLcXpYdTNiMTI3ZGVuai85ZC8rOTlNeGhPalRhZmIyZHJZK09kLzhFLys5LytiLzJYVzZ2NzFYLy9kY0xobnJEMUFEa2NCVDdyZlc5cmJYSytHT3lnUmdsZUd4aVBuSWs0cktSMGphdUZnbENHaExNa21lMXMzTG42ODBrOHgraEJaTVhOQUZsVVYxV28zVytwMnQ3ZTJKK05KR1FJeWxKUEM5ZjNha2JVcWVMS21SNnF1U3lZeFd0ZmUzeGZnN3gzVGl3QURxT0I5V1pZczBzN3picXVWR2N0NXE5M3B1TUc0NlRXVTNrMnFzcDBuNnBCMUhHd3lKNlFRZ3F0ckgveDhjZ29oUkJIUlJpZkdHRlNHbEJiZ0I3dTEzQWp0NGtQMUlmQ3VSc2pkMUFuaEsraUVQR3FOeU1FK0JBQ0owYmM3M2RXMTQ0NFprRVZpZDJscC9QRm5WMi9jbmtaTzIyMXJyUWhQcHROdXA0c1FiYUsyYmw5OTc3MjNoVldXNSsvOVpQbjJoU3ZGWGpFWngzL3lQL21YVzZQeHI3MTAvdkxGajlkVzE3NzJ0YSsvOWViUHJMR2hkcnZGOVAveVgvNVh6NTgvWDFYK3dvVkwxaHFVVUR0bkZMRkNEbEpPaStnZGhOcVZVMHVZcEVsRWZ2K2RENzcxNi85d2M3UlJGYVBJQVJFdnZQL3oya1VOQVF5MU82WW9ScldyTlNrVUFzVWx4SEk4K2NZelovSkVoOXFKd3NGZ3NyV3pOWm9NTDF4eFpRMnZMaXkzREgzMHp0c2Z2ZmxUamZMVStSZU92dmlpaUJhbU9VSUdEMlEyUklTSUl3QUwxbDZjaTBycHhKcXNsV2tWczhSMnN0WmtYTGpBQUJBakZJV3IyNXhid2tPenQ0T2V1dmRoTWkzcXNpSVFGQTVST3k5TVlLeTJ4aUNSS0pwcDVkOHpTTUdtdHNDN0VvZ3NENmR5TnpDRVdZLzEvbUQwQmV2YUh4bGNFTDF3QUZGSlV0UkJSYWdFZnZiZSs5Ly8yZHVVWlV1ZGp0V21xaXJ2ZzNOdVVoYktFQ2dCa2Vsa01wazZBTDUrL1NxaEt1czdkLzc4UC9TUEhha2grVGYvM1g5MytmMFBWdGI2VDU0NW5wQUt0WnVXcGRaNnNqZjUzdVlQTklBR3JMVFdXU3NCaWhCblFMbzRyZlp1b2E4bjB5SzNTWkxvNkhsbk5Qemd2WitTeVhxdDd2NWd4M3Z2Z2hBZ0s5UkowczN0OWUwN0FvakVnSkVRYlpJY1A3WjY5c1RSbzYwV2l0S0pDUUVXT3IzaFpHUmE2ZDV3YjZtYmYvZmYvcjgvZXVlZHRsVWRaUzlzN2pMU3NaZStMZ0l5MjV4Nno0NkVHWFFOWWxWVklVUkZLczh5YXkyZ0dFTnBxbW1HNklNUVlqR2RGcTZqdE5YM1lrVWFYb3l5Q1JnWHNHeWdzaHpaT1NjQVNab1lheG9SRWcwc2pkeTlDRWJnV2NNVDRzRTlIU1ZRQSthYzd3VlNnTnk4QzFFQVNBQWtzRUpxMW5RQUVIeEprbkUvWktIcHl4TWlnQkpGQ0ZtM0pZU0trcjF4K2M3YlB4ZFNDNzF1ak95OUM4RUhqc0Z6N1Z5bWJPMWRGZjFjRHM4MHJhUldxeld1M2QvK3hYZGUvK2F2dmZ2akg1R3J4b1AxblR0WHJWRkZXYWRweXQ1bmllbG5XUzlKbFZManlXU3ZtS3FzRlJrTW9DQ0k5OVZrRkVLTXdSY2lFU01LSk1iY3VuSDExT25UenozempUZmZlN3NvOXRhT25iSHRya25NM3AxTENHWi9aMWMxN0ZNU0VUeDU2dlNpaFRQSGpxU0trREd4R1dsemRIMTVXQTY3dmM2TFR6eHhyTi9kWGIveDJKSFZ4VlpyYTMxemNPUDJ0Ui8vNU1pejU5SGt3TkxJck4rbkwwdUlWZUJ4VVRvZjB0UzI4a1FEUjgra0tFdVQxSnFxcWdTTmlOUlZYVTZMUE5Xa0ZjNTF4bkdlZVdnaW83UkM0eGtpb28vQmg0QUFSbXRGSk1DQmcwWUJZSzZjbTQ2R0dMMnhhZDdyZzZKWmxodVlRaFFRUnQxSWV6U2dRS3c5MUY0WmpVYUxJb1U4MXdSNTVETHVMOVVYYUxJdlpoR3R6cHg3Y21HaHY1Qm5OMjl2VEgzc2RmTmlPbWxLSCtiSUlpQVNnNWVvQXNLMExJdWloSGxvRm1CQTZyUVg2akpzM3JyWnlyTENGOHl4bGJmcXFvcGw3V0xRRXRmYStmTm5UcDllTzJxTTNkemEvT0RLbFF1YnU2eVRCdjBGQWlGRUlsS0tmS2haQWlvVVFDUTFHdTYvOWVZUGR2ZDJiTkk1ZHZxeDI1dlRoZFl4WHR3WlRYYUtva2lzaWl3QytKdS8vVnMzYm0yWU5PbDJjMTlWU0N6aUFielMwc3F6VE90VEsydkhGNVpSVVRVWTM3bDA0K2R2djIwS0I5MnNHazlhaTYwSUQ5a0RSMEFJVU5mMXBKZ3lRR0p0a2xpYTdZRkJhMnlXWmFQeDFITzBtaEE1ZUUrSVdxa1pCSGlPT1dWdU50K3hoSWhJSWNheUtyMzNXaHRqRXdFSU1VUU9talVTcU9IbW5aOTg1MCtxNGY1enIvN0tjMis4QWFTRVdTbTF1NzF4OFdkdmtzQzUxMS92SEZrUkVLN2o1dnJHblF1ZlRMYTNFS203c3RRN3RycDI1R1I3YVRuS1lkTENGKzFEYkNRUUgrWlBoQkVxNzVhWGwxOTU1ZXNYUHZwZ2EzczNzNmt4Rm1pMnpxSkI3amRTVDhKQ2dNZ3NMTUk0YXlDeGNPUjJwN08xTjd4NjQwYTcyeHNQTm8zUncrRTRoZ0NDa1ZFeFBIbjB5Sys5L05LcG84ZUljRGcrdGJ5MlZQendKMWUyUjVSbWloUWhhSzJZV1pwbUFFQU1JZ0RJTUo1T0U1TnhVYXZlNlhGdEVtTUdPemNYZXVuMXp5OEpNeXA5NnVTSjVhWGx5MWV2Yjl5KzhRZi9zejlnQ0FnUkJGMnNsYUZXTzlVRTViaUlQdFRqaWF2cW5kc2JlN2MzVHErdXlXaEN6cWtZTlNEZnU1VjJmdmFBR1dybmErY1ZxU3hOckRGRUtJZ2dyRFYxMnRsb2JMbjJTV0t5eEpwRUI0NUd0TkVhRHRwc0tJamNiT29LTVNCaURMRXM2OENjcGttV2FFM05TUVROQUVDS1hkajUvTXBnNDg2WnM4OGlFak1nUkNUeXhmaWpILzBnMDhsVEw3K2t0ZUlRYmw2NDhKTy8rUFBkcXhkalhRS0x0cWE5dFBENlAvcG5UNzN4QnBOR0JuekFTZHl2VVhTSTVUZXYxcVJaNHh5YmFaejNCa0ZDM05qWVNyUmxWeEtLQzdGcGtRR0FCQkdPSE9Kc3NaeHVUbzhDNFNidktZdHBweGM3clp5RHIxeEpwRk5qWXZEQmUwTGlFRk90VGg4Nyt0aXhJOHNMUFI5Q3I1T25uWHgvVWd4KzhOUDlFTFROT0RvUkRzRXp4MGFZWURhNVJva1JnTWxGZnVyYzgvMkZ0WisvODYvNnVWbElqMnh0N25YeS9QbG5uOVdKdm56bCtxMWJkMzcvMjYrZWYreUU0U0EyaTg0TFNxcVVKUkwyUjlmV01xdW40OUZ3Yno4NDEyOTNyVkcxRndOb1ZiTXNGdy8zdmVicnVpVkVMbW9Yb3hpbFcxbW1GZUdzTFNJRWtsamR5bE1oYXFWWm5yZTBoaGdoTWpiTHY1c3RZQWQzcGc4aHhxZ1FRd2dOaHNVYWxXbWxxQ0VVZ0RZdVJoMmRCQUZwV2R0S0RWQWprQzRDUUl5SmtEVUpXQzBpNDYyOUQ3Ny9QNjYvOS9iYWtTTW5YbjAxYjdlMmJ0MjVmdlhhZER5bEdRYmxLMVc2RHlXQXo3cHRESWJvYjcvem5ULzV3ejlhNkhWYXJiU3FwcVFJWWpPT2lzWVlqQmlablhjc0xJSHp2TjFxRlpPeURtRkdpR0NPMDJJUXhVejJ4OFZrRDV2RWlFaTBqc3lLZWJuZlgreTFNZnBRVHBYU1NOTFIrdVhISDk5YzMvM1I1NTg3aVVob2pBNGhrSnJUbWhFQkpMVkozdTBKeDFUSG5UdWY3MjdkTElaYlIxc25pLzM5Zmk5YjZQUXVYcnk0UHhxNEFOOTg4YmwvK1h1L21ZVElRVlJpbEFLSk1RSmFVcUdxa0lNQzhTR3NMQy92YisxRlh5cWxqRkUyejBUcithYnoyWFRsY0hIblEyaEltbG1hNXEyTUR2aExpQWlnbE82MDI0eUZKbVdNVmdnaUpEeUQ2SUdFZzhZOElvaHdDRUZiRlppRER3Q2lsVFkybVl0R3NRNnUxdHFBOXdnTUNHQ05Rb3dJa1VFSDlERUt4S2lSR0lWeDgrYnQ5WTgvelpQMHBkLzg3ZWUrOWEwa2FVMUhvNHVmZm1ZWEZ4aXA0ZlFmREV3aTNGM1ovY1ZLaWJPdUt5RkV6dlBzaDkvNzNuLzlmL3UvYXVTdG5Yaml4Tkg5L1NFSWtGTGV1YVl2NzRNalJVVlI1bG1hNWxZcGxiZVNTVFdkYjhvR2pyRWFEMmNmN3Axd0tEMFlyYlJTSVVZTnNOcnZFMEE5bmFLeFFzRlltMXZUYWRueno1NjlzYmQxYVhPSEZmbG9BSkVSZ1lFQU5Rb0xpdy9WY0NRY1E4VGRHeGRzbWl3dGRDYkZmbDNCVXRaQ1YybUlKNVlXenovOXpLOTk4NVZPb3RFSEpFWVduVmlPTVRxM3VOQmY3SFJHKzROSmQrSDQwcHBpTVd2TCszRzdwVlJkajJ5L1k1STBTcHp2OHJ3UGtJRXVjbFZIUVV4VGxXbzBvS1FoT3lDS2NLSlJNZ3ZSdVpvdENLRndLSU5pWmxSTjU0dkZHR1d0NmJUejZhVGMzUnNBYVMvaU9SZ2xxZEdLU0ZoaTRCQ2NuazZuQysxdUU4K1ZVdnJlRlFnaHhoQkNTZ1FNNG1Dd3UxbFBCMGRXajUxODRxbTB0K0FEcDB1TDU5NTR6VGQ2cUEyYjhpc3dQKzliMzMzWWVXaXQxOWZ2cksydUF0ZVRTWjBrcVRIR2VVZkdhS05GMkRsSHBKeXJKY3JXMXRhUlk4czIwWG1ld043QnFVUVJjYzZsYVRxYmZUZFpqckFtUk1RazBkMWV0NWs5OXZvOVl5MGdUTHl6TmxuT3NwZWZPcmUxTnhoVXJocU9GNWRXOHp5cktnZWVJenRCTWRvWW5jVG9rZENhM0dxeVNveHcyOXArTzI5bnB0UHVkTHZ0Wjg2ZDYrakVqMHVicWNhc1ppQ3Bodm1odEsrci9mMzlqc2tXTzEybGRKSWtuY1RnQkJmNlhXdnRsQmthUFpBSE90ZDFWVFdyWWRJc05jWndrM3hoUTBGRFVpclBjeEVScm1LTXBNZzdGMElnb2p6TERqNUhhNjJWNlhXN0RSRzhydXNHMW1PdFVhUmd4dFFYSFlxUjRKb0VqeXhSS2JTV0JVVUFnYUNScGdnc0JFRWhLZzJreVZnQW1WVGxnb2dIQVFFbVVsb0wwa0hCZ3ZkY2VIelVkcnNIcFdlVW9oRENrMCtlTzNYcXNjbit6cmRmZjI1ejkwNVJqbllINHp4TGg2TlJDRUZyVTdqU3U0aUkwWVhKcEdxMVcrMTIxbWxudzhIMDhDcDNhN1QzSG1YV1hvd05DVkNrMDBwYnFjMU5zdER0RzJXU0pJMEFLZUJpS3grbDJZdG5uNUNBVjladnF6Uzd1Yjd0MmZjV09uVlZ1NnJwMVhKcWpRaFpvL0k4NzJyVHk5Tk02NlZPWjZuZkpjQWtTWmFYbDlwNVRoeTFvaWc0Sy8wQ1J4KzhxMFB0WW9nZ1ZGWkZWWStwMXpjYVdrbXFzQmFTdk5zVFRjSkFzNlhmaHlXdDJUT015Nm9PSVZIVTBtb21uYTZ3bVdnamdFSWxBTlpZclVPTVVZbEJsVGxYVmxWcGpCRlNpTVRNeGJRMEppQUJLU2duRlJFRkQ0aU5sQTAyc3ZjTXFLdHlLc0xCZTQ2TTJHeitJNUM3Y0xRRzg0NGFnd3F0M2xMZVhuU1Q2V2R2L2J5OTNHdXZyQVVtVUREYmZQeExNL29PaFJwbTZYYTdONjVmeDJyeStHLzkxczFiRnhLTnJUd2Jqa1ljb3lKVmxtVmRlOEFHbWFhMnRnYkc2SlhWMVNTeHpCTTRHQ1FMYTYyRnVkSDVFZ0VrWkdaa09YdmkyR3EvdTlqcEtjYkIvbjdHTVVsVENKeFp1OWhxOVUyeStvMmx6NjllWWFOdUgxbjU4T0xuKzd0N1NZeTlOTTJOenBPMDM4NDczVndSTGl3c3RGcnRQTkdkUE8vbWVUZFBOUkFnV0dNUlNRRXd1eEM4SnV1OTA2Z1Vxc2djZ2ljRTd3SzFiSlFScUNxMTdmWmlyOWpibUpUT3RMdEtXWWx6Z3VROUNTbDY3OHFxaXN4cG5yWFNqSnFJM0tDclpoaGdRU0pycmJXaExNc1FJaUFoWUYxWFNaS2FMRzgwT1dhcUNDZ0k2SDJvYXhjQzIwUWxTWUp6ako4QWFPY2lNb1VRUW93YVlTYmtJZHlBalpzVTF5aXRTUW5FaFdOcjNlWFYwZVhQcnJ6MTgxQVY1My85MXhZZmV3SXBtVE5YOERBbXZlRTNmSW5jLzczREYwVDB6cDArZmZxZi83UC8vUC94My96WFAzL3ZuVys5OXVxZmZ1ZXYrcjNlZUR3dG5OYzJpWkdOVWsyUjA2UTFNV0pWK2l6THRSNkUwTXlIa1lFQklNc3k3LzIwREdtU0NMRlU4YVVuSG4vNTNCTXRrRmFhSUV0aWJXYXNFZ0dSVk5sZXAxMkRaRmxyb1h0K2MzZDdwZGRleU96dE85dTcrM3Rrek9MU1VyL1h5VE9MQkVyaDZ1cmFZbitobldWWm1yQjM3U1JKU0ZQVE5sVEthbE5PSjBVWklJUkVLWWlpamM1aWFyVkZwS3FxRVhLYnlMVGVFNFYrR2tianNjN1N4UlBIQlEyQm16SHQ3NjFXYWhmcXFrYUdORW5USkVYRXlJSWdoMDRpSW9JaWxhWnBWVlhPTzJVc0toMUNkRDYyODFsUUl3UWtDRDdNWkNXOUEyRnJzeVN4c3lXU3pCQkZFMm9VRE02eEQyalViTUNPZ2tKRUZKbUYyU2lOUkNEY1crcWVmdlhsdDlldnhXSjA0YjMzUnFQUmE3Lzl1MGVlZjJGK1pPcHdJR2xBUFFLUGxIQis2UHBrSklnYy8ra2YvSUdmN1AzcmYvMnZSdnRiTGdTUTZjcENiMzgwaXFTME5vUVlZcXlkWXdSQ0dJL0cwMG5SWGVpdHJDeHVidXdxMGcyMXV5d0theXdSOVhzTHZpcnFzajZ6c3ZqdHI3MWdpUHQ1MnUxa2hKSmFxMFNJZ1lpRWtZbUVveUQzKzUzRWtvOThiSGx0OThSZ09KM1UzZ2xMdDlmTzhrUXB4UnpUTkYxZFdDQ2xGS0d4dHR0cSs5cHBCcy9DSUNneHRjWjdiWXhpNGRMWGplYkVqQmlrWkZ4TVBLZmo0WDRnWHNqWEhJcnB0Zk9qeDF5SWhCSVExS0dwUmpOa0thdkt1YUNWeWxLckZUV005VVlYZ3c5R0VETExLb3d4M25zR1VVU2tiSWpjY1A0NE1HTVVoTm81WVE3Q3plNmxORTJ0YWE1Z3N4MFVOQklCTVB1QWtkSHEyVEIzRHM2QXlNeVJWS044SUZiWngxOS9aYmkzK2RuMy9rY2J3dmppMWJmOFg3eVFxbFBQdmlBTW9HUXVWL2pGeTNVZk5aT2JxNEVJdUZnL2RlYjQ3Ny94Mm9kM2JxenY3S3oxdWs4OTg5ek5PMXUxUUwvWG14WkZpSEVHZm1RWlR5c0FLSjA3ZnZ6WXdoS01oaU90ZFpKWWEyME1JVGRwckp5RWVxbVR2WHp1VExlVmVGOGtxUmFKTGxZdUdJcWF0RUtqYlF0TXFLdWlua3lHUGxSWmt1UnBsdG8wMCthSUxHZHBXbGRsak1FbVdpbENnalJObGFLeUxKSTBTNVJWZ1RtS0p0SW1jZDZCZ0xGV0psSTczOGh2TlRLYnRYTmxWWmhNRDZ2eDFwNDUyZStBMUVQMm5hWEY1WlBIZEgrcGJ2UndIcGlHeGhqTHFnb2gyc1JrcVo3VEl1RlJlbkRXR3NjY21SbVJpR0prNzRQU0pqS0RCTkxLYUdPc2JaSlBwY2hhWTdRUmtBTWxZMUkyZ1FZQlNJaGFHVzFteW1jZ1VWaThRd1F4V2pXeWdneEpmL0hsMy9tOTEzNzNINmxlUnhUdjNyejV6bC85MVhCOXd5b0RvQVNJa1JpUUFWbWdXY0pNaC81QkVSU2hROXVtRGsxOW0yWW5HS3N2ZlBMZTJ6LzljYS9WZnYzWkYwNGZPejRjam80czluLzl0YTl4VlNPQVZwaGx0dHRwNTBsaUZTVldKVlpKakR1Ylc4WlNudHNzSVV1Y2tlUmFFbllkaXFjV3VpODhjZXJKMHljeFJBWE1VVnp0YmF1ZEx5d2tDLzMyeWtyVzZlaGNvV0tKYmpxZDdBLzJLKy9RNkZhN2xlV1doVW5ydkoyYlJKRWk1eDBIRjMydGhGTkZpVUlSeitKVFpZdzJoTmd3em9NTFJsbmhHZUJhT0RRTG1MMlBMdFJSVVZuNkdIeG1vb3JqckpXc1BmT3NxSVpKaENRellOWEJqTk01WDlSQkFCT3JNNk9SNTRJdGMrRFZqRDhnd3N5S0pMVkthOVVJRFB2SVVTQkVSTlNvVUJFUUE0SUNKQkFTQmlDWTFiR3pGb2lJaUxaWjZvUWJyTE0xeGxqVDdGeG1ST1pZT3ljQTFscEZNK2FjQkVnV0ZzNy81bS9ZaGM0N2YvdDN1TFU5K3V6eXpiZmZXejZ5NXExVkVhaFIrL2dsdFNhQVVDUzRqV3ZYWSttbUZ0cVNMR1hKaHFibzZ6ZGVmaFlFLytiSFA2dGlzRlpwZ1U2ZW0xWWFvMit3K1lpa1FwVm96QlBieWZMTTJySXNOTkRSNWFXVnBmNnhsWlZlcDdlN3Q2TkloU3BPUzVlZjZIVldWakZQbGRZbWNoaGlPcHdPWkJCanJLb0NSTnA1cDkzcitSQThZNUJvck9xbVBZbGNWK1NtWXhmRktsMTdGMW15TExQR3hpcHlZRzAxa2xSVkhXSlVTbUhBcXFwaWNJME1zbk4xV1ZXZTY3U1QxUXlwVVVaVmVXNkIydW14TTBFVVBZeFNob2gxWFJWRkFRaDVsaWRKZW9nNEpQY3RZbW9DdERZNjBWeHhGVGlBVWlCU2xVV2FKbmxtRklzSVdtdWFoZCtOb20zakNPSFFCRjVuclZhVDZ4S0JNcWhGQ1JNTEVIQU1qcHhqbGtRbnFJZ0JtVmdKY0FETXUwKzkvb1lTODg0Zi9ZZHFiN0I1OWZKa01tbjFGeEVFQ1IrYWdqNkVYWFBRV1VjQkFJNFlBUldhdXE3SzNVbkg5dEpXSWpFa051bGtpVkpJaE4vNDJ2bkZwZlpQMy9sZ1kzT3JsK2NydmQ1Q3Y5dHFOY1ExTDhJazFPaFFKOFlTTTZuK3lhUEhqaTZ2WmxscVNNZklkemJYc3lUeDNxWEdrazR3YllGV1pHM3dsY216L21LL3JFc1BFSVdtaGR2WTNNMnlUcmZUcmF2YWhSQzlWQkV5YTVNa1VjUVdGVE5YWlpWbkZFT3N5cEo5UUNLMEtmQU1DRWZ6UmdJaGFxMWNxQ2JGbEVHVTFtMmI1bHBKZEN2THErVlVPaWNldzg1Q2VZQzNuSmZmaUtCRW9zQzBZaGRZRTJXSk5sWTNPTy9Ha2c0RGJtUStQQ2RTcVZVVGdpb3dBZ3JMbUtNdXhrblNReUFSTVRQWmJwa0pUeVNXa0tJRTVrYlJRTFRKVTBGUWVhb1RFMXhkVFliSUFhSWdpZ0FVdzNFSVVkblpwdGttb1dpdUoyU3RzeSsvZE91RGQ2OE8zbmRWNVgxUXMvSElMNEw3T2dCYzM2VnpBU2tkYTMvbjRxVzFZNnRKdXdYQ3ViWFJCVTFLWW5qdTNKa25UcXhjdm55NUxpb3RsS1pKMXNuekxDZFNNUVlSVWtvamdBWnFwMW0zMTEzczlvQjVNcGwyV3UzZHdYNnIzVTZUeEVKTXM1U0pRcWlSU0FIWDQ0a3ZKMFNtMzE4aWt3bmdZSCt3c2I1cGpEbHorclF4QmxoOGlJVXZTY1FxVFlvSUtITE0walJORW10TTVBZ2dXcUZ6cmlIMUYwV3BOR1ZaR21QMHpzVVFmUWpXV20yTVlGQklWbXNpV0ZsYXVyQy9zN1o0d3FNV1lYeGdjU1FnZWpjdllvMU8wdVJMVjFNMzAza2lOTlpLN1RrRVJvd29aVmxVbVVsMUVrTWNqcWVUeWFScDBodHJ0VFp6ZURNM2N2ZmFhSTFLOVZjWFZaYVV1L3ZyTjI0dFBmMnNhSTFJZmpyWnVuVlRRSkpPUjVBSVVCbERwRU9NTEJKRWJKYWx2WFlVUnExbHpzbEhnZnYySHNwQmpuUkkxT0V3ZW5RR0poSlFBQ0l4eWJMKzB0TGUrbnExdjVXdTlMeEdLNUlnSnBvSUtJYlFNZXI1Sng4dkprVjBRUnZkNnJielBHY21hd3dBS3ExSkFGZ1NhNjJ5cnFyTHVpYXRRZ3o3KzN2TFMwdklNZFZvVXh1NUxzZkQ4V1FpdmxtZm9JeTFMSWlFL1g0M1NlMmtMQzlmdTZxTld1d3ZCQUlGbUdHaVNkbkVUcWZGcEs1YmVkWk8yM09pRUFjWHRVbXFxclNXWGUxaUNDR0tTYTJ4dHVILytSQnFINjJ4TVRLQTFNN3ZEc0t0TzdlQVdpNUxOQkN3Z0RxczJpTUF3SURPaDdLcWhVTmliRzR0UWNNYUU4Q21KSlQ3NEwyTmZSbWwwMFRqT1ByUUVPOTVpdGlxbzlFQ0NNd2hjbWh3UmRacW94VmcwNUtBcGhHcWxWYUlhdkhJMnRLcGt6YzJ0ajUvOTUxa2Vlblk0NDhaYXpZdVhkNjVmbjFoYldYMTVIRWlIVUxZMzk3cHREcmRoVjRFUUFpajNkMzluVjBoVFB0ZG0yVWc5N1RPRDFOZ3ZvZ1VmREIvYWZCREFnejR4QXZuUHpoeFZNWkRiY25YZGNzbU1KZTBNMGdDdHRYcEx2WldRVmlFMisxV0NESDQyT3YxQ0lFamE2UHIybFZWRlNHNDRLcTZ5cko4T0JnMkhUWlhUS3BpUEpxT2FsK1puU3pVQVdNMGFhSVNLNGhWY0M1VzdZVlcyczZPbnp5NXRiUDEzb2Z2di9iSzE0dzJTcEhXQ2dCY1hXdVZlaFJzdEVVaWV4OUNpSVNtcWoyQTFIVmR1MW9JdkErK2pBM1FPc1FZWXBnMlZYRU1kVjJSU1F0UE80TlJtbVNZS1VRaG9RZHZMQVlwdmErOFE0STBzWW5XelU1MW51OGJmMGdIY2tadkJtdDBhclZ6TlF1QWNPVkNVZnRXSzdOR2FUMHZUQkdTeE5yRUVnbWp6SVRQQURVb0NpSzYzWDc2dFc4TTdxeHZyOTk4ODAvLzVOaXhWV1BNOXZxNkt5WlB2ZmpHNHJHamFacVU0K2tIUC96cGRMQi83cm1uZTZ2TFphZ3Z2Ly9CclN2WElFL1h6cDdKc3h6dTJVRDdWU1dMN211MEkySVU3aDQ3MGoyNk5uVkZZbE9vS3FWMFVVeEQ4TktJYXFNeUtra1NZNGlBUmFQUm1nTjZCQ2duVTBJS1BnaEFvK1VWT1ZwbFl1MkdnNEZXT3ZwUWx0VjBQSTNlWjBrbUxBMjhvZFB0NmtvWGRjbGFPK1M5enk2c0xDeWxPbHRZV0h6Lyt2WDE5WTBqYTJ2YWFBNWMxM1dhcG1tYWRUcEpZalFSK3VpS2NxcVVzb211cW9yQmwwWGhPQWhBVVJTZFRpdUtjQXpUNmFTcXlyS2FqTWJEL2tLZkNiTldXMkZWVm5GaExTZWpoSUdGU2RHRDA2blN1U29FSkpVbVNiTTM3V0NGQXh5RStnZThOWXRvcmJNMG5aUXVSbWxXOVU0bTQzWnVWSnFGMEdqN3pueE00OFB4MEwycUlZcm53QUpIenozOTZqLzVaNS85Nk8rM3JsNjkrdmtGWTB6YXlrKzk4dUxqcjcyV2RCZWlBc2RodEx0OTVZYy8yMzN6YmROSm1MQVlUOGp6NDYrOWVPclo1eFVRejRsdmM4QWpBOXpEUy9oaVZGZ2ppOFVBRURoYldEbjU1Tk5YdHU1SWhIYXJQUnFQcDlPeGN3NEFtVmxwWlJ4NkFpQnRpRndNd3BFNUZrVWhrVW1UcXlxT1VXbnRmZlRPSTZnWVl4T0dSN3Y3bTl2Ykx2ZzBjWVpLYTVRTHpqbWZEUWN0bTJvRmx6YzIvdjZqei9lM2QzLzdteSsvOGRycmFaWlprNnl2YjNZNkhaTVlZVEhhV0d1SmNGb1V6bEdhcGczTldKdVo4RUh0M0hnNkZrUWZnbmRPRzQxR2FVWGFHT2Q5WkVCVUlZaXhsaEcwSWtONmFhMjN1TEk2RGtJS2FOWVJnVGtOV21LVWN1bzVTbUowbGxnMTB3YWVKNkVpeldLTGV4c2RNZ09LSXlYV1dtUHFVREVJTVRTNU5Xa3JvSU56TEV4RVNXSTBOWTJHdVN3cWkyNTZvRDRFc09yRTg4KzJsaFlHZDI2VDV6UkwyOTF1MGwvS2xoYXI2S0dvQlBIMEM4KzJFK04yOTZycHBBcHVhWFg1eEdObm52ckcxN3JMaTZFQnJBdktJWFhLWDJhNEFzak1Oa3VQUFhWdTU5TVBTMWVFcXZMZUZVWGx2VGZHTmp0eURKQXdlOUthQ0JEcnVnWmdhNjFWdWlyTEJ2VGt5a29wclpUeUxvaUFVbW84SHQrNGVmTzlUejdkblU3T25qNTU1c1FwWks3cktvVFE3ZmlRaGN2WHJyMTM4Y0tkY1UwTXQyNnZiMjF1OWhjV2JHS3JzaXFyeWxpampGYldnbEZNNUNYNjJzY1lGUkVpbG1VcHR1bnNnREUyY0JTQWRxZE5TakZBczhhRmpCWkZyVzZYUTVnVzAxWnFoL1gwOU1wU3A5TmxEbWx1UXNNUE84Um9aUmJuZkVPYk1NWW1hUXJ6alNwOFdONzYwYjY1WWR4UGF4ZENRRUh2NDNSYWQ5dFJoQUdSaFpWUzFoZ2toSGgzc3lRemEwRGl3QkFoQ2lOTGYybHQ1Y2lKTkVzVGEzMWc3MFBwU2dnaEFobXRUejN6OUlsemoyUGtXTHV5S0pJMDYvYVhzbjRIU2VOTUZWZUJOUHI2OHdIc2ZSN2lZV3IrZko5eW9nQ0xPdm5NYzVkKzh2M2k1dlhnNmtrSWJtOHdHazhYRjB5akExbEVWa2dFS3JPV3RHYUd1dlpLSjBHQ3pDVU1HaktPRjI0OFZhL1QyOTNhbVZaVnU5K2JSUGZweFV1MzFqZWZmdklKU3dSUmpFMEgwMkp2TkJLdEVlcE9hbGI2eXhqQmw0NkRRS29pUzJRQWhtWTlwVkpLQUJESkI2WkVNMUxwS2xBa2dZWFFwS2tHa1VZcFR5c2Z2RktLQlVmanllNytmaENPd2hKQTYxUkIzQnFXdFNjM0htbzFCdDFESkNJVVptbVdLZ3FWZGF5clFJaXRKTEhhTkRyakFZRzRFWTNGdzdzVFpnUnMwSUN4SVZjYlZIbG1SMlB5UUl6b2ZSeU9KNTFPMTBXT0FpQnNMUnFyUlBoZ1d4T3p4QmgxNE9oRENDSE15RFBRN0JKUnloZ1hpcXFhdUJnME5RMnhNSjFNclRiZGZoK0oyajRFam1DTUJvVUMvOGwyWUNJMFN2c203NXg2L3Z5Rks1ZEdoWXNzdytGd2YzKy8xKzNNb1BUTTNudE5XZ0dJOTNOVjZCblNSMmtOaldVRVg5ZTFFcFZZbStYNTR0SlNYVmNMbmM2WjQwZjNoNU5yMTYrSHFrNnpUQ3RkMTg0WTgrTDU1NWUzZGk5ZXVuTGl5T3FwNDhleUxCOE5SeHhqdjk5dnBoVUhncnhFWkt3Unh5QlExODQ3MTFodGpKRWxPTzltZ200K1NQQmVtTDFQazZUVDdScGozTFRnQ0N3eW1wWUxDOW5lWkh6OTF2b1Q1MVFJd1ZxSzg3UitudDNMdENpY2M5cWFkcnZkWk1SZkxaazdVQmNtYTJ5VzVXVWRZb3djMGRWeE9CeVZaZUdjWXhaanpJRmNla09yUldFUjBURXdCd25Nd0FMYzFIR2tTU21rR09Od3VGZTd5aHJyYkZiVjlYUTZnVmF2OXFGaE92Z1FoVGdJazZpRFhoZk1IUUhoZlRPV2d3V1dJSStXYlo5dGNXQ1pGdE85Y2pLbFdFRkVSWWhRVjdXckhTSUdDUTMxSzBod1VUV1FkRzFNWkVaRm9BMlFnaWdnSVVTdnRWWU1ScEdJdEx1ZFpOc1N3T3JLNHFrMWRlNngwM1Z3KzN0N1JFcGJtNlJwTzh2WGpody9lK3dFQkpkYU14Mk5OelkzMnIxZWYyR3gwK2tuaVVXQ0dMbXArRFRxV21vUXFWeE5pTXJvU1ZFU1VSM0tFSHhWVlUzNlJVUkthK2ZEWUR5ZVRFc1dHazBLWXhKRnRETVlpaytPOXBKaHNiKy9jMzNwN09QUlJ6QzYwY0ZSS0FEZ21ZdXljTUcxVXBza1Joc3Q3QnZBeWtQWkhqSVRrR0pBbVNjaVloV2xWaXVTcXZZaVZGYThQeGhOeTBudFBRdW5Oakdrb2tRVTRUa2RPaUpxWVFraGVCOFVvaElnUkUyS2pHR0F5V1IwOC9xVjZYalliclhibmI2Z01zWVlPNXV6Uk9GR3VGK1FCUERlNnZWTFJNUyt2S29SY1hWVmxvVzJKc21UNEtLNE9KMU9xNkpzZEUxRjBCQnBwVUlNd2t4S1NiTi9UN1RTQ29DRW84Z01WWlJvYlRRQmdsYTYxVzdmV2I4em1rNVlZdUZxc3FaMmRhdlY2ZlVXeXFxY1RNdXFkc3hSSTliT2pTYVRsU05ycTBlTzJEVGh5Tjc1SkxWTjltQXpHMklJT3V6dTdDWnBZaExyYXRlRUd5KytLS2Npb0xVbXBWallsYVZFQmtJWElwRUtrVW16UWVXakh4V2daV3J0OFhxd3JTUTRjU1NLbVJ2UEp3QzFxeXRYQzRLMUpra3RZc09RUUdJVXhFZlJndkFRa1VsWU5HR2EyQ3l4azdJQ2d1aDVOQnJYdmhKRXBWU1dKSXEwekJoVEFzZ3N3aUhvWm11T0R4NlYxcVJJYTFJS2hLdks3VzV2YmR5NlVVeUc0MWI3K0FsYVdqcVM1bGxxcmRJMEc5ek5LSHYvU1dBKzkvNDJVa21haW9pcjZ5ekxXVWR4Y1g4NGNNR0pFMk5USXFxY3oyemlRMkRtMUdnVzhTR2dSaEprQVVFSk1UTCsvMWo3enlkTDAvUzhFN3ZOWTE1enpzbVRyakxMdHU4ZTArTXdCbVpnQ0pBTFlBa1F4RktHaWlCbElxVFkySy82Sy9SQi80WkNDb2tTcVEydGxpU1dJQWlTQWduQ0RHWXdwbWU2dXJ1NmZLVS81aldQdTI5OWVMTWFQUVBRclpUZnFxS3FNdXVjNXp6dmJhN3JkeWt6RzJzQjBGcWI4bWJUYlZmOTVzbVRwN2JpcXEyYjJTeUU4Y1g1S2JHdHZWOWRyYnB1ZTNaK2Z2djQ2TFZYN3QyOGQvdmc0TUM1bW9nQUtlV0NLWlVpUkpSTEZoVUNxbnpGeENWbUtXS01UU2tWZ0ZLZ2JocnZ2VWdwT2FuQWFuTzVkM0RncktucnBtM3JLWk0ybG1SclJLWGN4VnJrNnVRUjd0NjJiRjRpcmxTQmhpR0VrQWl4cVgzdExJZ0F3cVFKaEU5dFV2NkRsbVpGNHJxcTY3cTJtejZtUEVtMVJYUWkrM3B2cloxeTVxL2hYVVUweDJLbWRybVVrZ1Y4WloyMTFsb0E3THIrL1B4aUhQclFkNU40WkhlNU5KVzNWYVdFSmVkUEhyMmZET2IrZlJrT2Y0RkgvVTk4V0tybW5DcnZKV1ZIWml4cHM5NFk1aUdHUG95enVpVW1OcWFJaEJpQkVKaFRLVUNVVXl5bDVESUI5VUVRWWt4Tlk4bFlSSXhTK2pnOHV6Zzl2VHhMUm96M1lNMW02SFBKbDl2Vnd5Y2YzN3h4bENUR0V2c3lQSGp4U0EzczdTeWRzenM3MWprUFJGbkVYcjhyTUF3RElvN2RLRmtaUVlvYXNwdllxMGdXelFsaUVySUFvdHZ0bHBsalNxY3ZYdVNVWTByenRnN2pFRE9rb3VzaGZQYlc3WWI5d21LR0FBVEVJT1VUbGJqMlE0eEZyRFd6eWxzVmxLS2ZTdDNRdjNRKy9vcTdCQkVRTEZManFzWlhLVzBGcmdYMURHUU5WczRheHF3c3FBQ0Npb0lZbGN6MURyWUlPbXV0Y2M0NTU1QlFWZGp3Zkw1QVNlMXN0dHhaem1ZenNJeHNVaW1mb0hBUkVmLy9lVy9nZFdDdVFnNXhlN1VpRVVpRkVKRndER0d6MmV3dWxuOUJFeEROdVNBb3ZZUVVzSy9NdEV4U21Yam5JbElRQUhVWXg5UExpMjRjcHIrUVZITGZ4WnhVSWFSMHVkMjBzeGtpc25QTHZiMmg3ODR1ejllYmRZenB6ZGZ3WUgrZkNBRzFsSUtBSVViblRNNTVpRkZWdzVnQW9HM2JwcTdYNi9WcXZXTERPYVh0Tmx0bUpDb2lWVlVOdytDY3ErdTZYSWl2NnUxMmxVRkI5Znp5TWcxNzNjWEZ6bkc0dkR5cERodkRyb2dnUWtwbEdBWVJxZXVxcWp3ZzZ2ODRON0lDSUZSVlZWWFZhcnY5OUJ6VkdPTXIveE5qdEVsb1lVUkZRSkhKZU1mV1dtc1FJWmNjUzlvL09GbzA3YmE3OGxXOWQzU0w2aG9BaUZsQkkyQyt0dHpvcHcvdnA3OUJBUUVBL3ZIeVF2NnFzZ1JWTWdMQlJKSlJSQ3hTUk5VM3RUTW1sZXlkQ1NHV2tzWVlpNVNpU0FDR2NJeEJrM3J2Y3k0d3BTcGhOSWFKSmlFOVcyTUxRRWl4NjdvWHB5Yy8vUENEZGJmdXdoQ1NVRmFna2tKZ01ybklkdWhPMTVlVk1SVmJCckdXa0ZCVVAzNzZDTURHblBZUER1cTZVZERhV3pTQ3hqS3hSMG94aFJ5SWFTeVJ2TTBJQ1pRTUN3QURqaUV3MjFMeTVEY0JKZ01aU2dKcnJhZFkyS0FhbHFPYkI5ek1uai84S08yb25kOHlqUWNwd0thUGNZd0pnTHh6bFdWRVVVWFVhVHIyMHNhTytCT0RwZWxSOEttY3BHbVZMOTdpclBXcks3TVpoaW0xVFRDejgyUXN2TVNTaWFwQVlaU0pOS3BNNUwyM3hoQXlxaWtGeHh4RVpMRzc2dzkzWXpnd3J2YStaVFJUVHkySUNPWGFpZy80bDhPYXJyMi9jRzFkL1krTHduUTZRdkt5MzFHQWtuSnkzaTEzZDdzWHowb3B4bGdrdXJxNkdtNE16dGNwUnAySzBKeDlWUlVWeldVU3hxVmttWXcxemxvYmhyR2V6NHFVNTgrZTNmL3d3OVBUMHlTbEgrTVlwYTZzTlZBbUI2b3pZMG9YNjlYZWxDMHFKY1prS211dExibU1vWHY2L1BFWStuYld0azA3WHl4MkZqdElyRG1EQ2hOcUg1VXhxNlF4c3JlSE53NWpqRkp5My9jaVFwUm1iVHRyRCtJNHJyb3RBREFSSys0dmRtQzlZZEdqM2RuZS91THdyWGVmeEptNThhYUFUNHFFcUFxZm1BYnF1cmJHL0pYYXI2a3crSW5jbmI5eWk0V0lkVlZYZGIwZEJ5a3ZuZG5URjZMK0JWMFdvOENZaThrRmxLeGpjSWJCWW1JRlNaS0VCYmx4ek96SkVodnJIQ0JOWTNjREJvMVJFVUJWQS9JU3ZUKzU3U1l6S3lLUVRwRVVQOGJNeHBlLytTbmRLQ2tRS0x4TWlSS1E0cTFOMWh2clU4bER0L0dXcG10MnU5MzJJUmhmcDVJbkc0VHp0dVNrSXBOcHg3QkpwV0JLeHRwVUtLU01jVHkvT1AzUkJ6KzZ2TG9xT2JJMUtVbk1VaUVXVWlKazVsQnlFcEYrYUNxbmhyeGhhMEV4amFscytvMWQyMXhTaU9NeTdJYWN4TkRlalVNUVNIMG5LREduREVxcTQ3RHR1aDRRbkdFQUhXT1lVSnhrZUV4eEdQSXJyNy85Nk1tRFB2Ukh1L3ZFbEhKUkJSbTNyOXpaWFcxT1Z5L085ajc3NVdBV0pGbGg4dHJrTWNaWWlqWGMxSFl5Wk9xbnN3citLcUhNcHdlTW43YktUYnFaeXBqSzhUUXRtRUlLbUptWmtCREtkWDRDQUVuQmxNUk1vUk9NVU1aNCtmUUZHSFRXRWJKdkcyY3NLVmoyTkFXYXZJeUlVclNPeHFTWnAxaE9VU0JVVkVSQ0FNYnI2Q1pEL0pKRXFQaGo3R3Y5Skdqd1drTituVFg1c3NZU2tZbVJrZk4yMkNxSjg1WXlha2pHbUs3dm10bWNpTmxZaEtJeUpiNktZV2Ftb2lubm1GSkFCV01OSW5UajlrZjMzenU3T1BIZWVUU3Vyc1lZWlF5RW1HTkVCQUVsTmtVenFlWlM1bzEzbGlSakVSbkNPSXo5eGVwTUpZMmhGaTE5SElZMHpoZnRjclpMMDNvYmNBck42N3FPaUVJSW81VDVmR1ltN0YwdXBaVFpiSllCbno4L0lUWmhEREdNdTN0N2NiMHhBTDZ4bi8zTW16Y1A2dlgrWVFhVHg4NzdDbFFBT1lsMFl4QlJhNDN6aG40aXIrYy9XT1QvVllXZ0FxaGhxcnhIUWsxQ1JOWlladnN5Q1FXaDRBU0xKQzFUanNSMHFHUjdjdks5My8vL1hEMS9XdS91SEgveHA5NzR3cnN6UUl1b0NJWnB2THg2OHVCSDYzWG42bG16V0lZd3JzNVBDUEhnMXUyRE8zZGRYYUVDZ3Fob0dFTUtZNDdKR2VQcnlsUTEwSFMwV1RVREVsd2ZULzAwdDhVUTZMUnVVcHhzUU5iWjVkN2g1WHFURkRHWEVxUHpsZUdxNi9yZGxKaW5DRGhLSWdTRVRFVWs1YVFxMWhwQ1NpV09jYkNJWjFjblR4NC9NQllCdGFxc1RxN0dJaEpUN1QwekZWQUUyQVpaSEN5dG9SaURJejhPdzdRUmQ5YUdFTGE4VFhGRXpCZFg1MmZucHdqNjdtZS9LS1dFUEtvcVc2TUp0dDBXRkJhTGhXRXNxaUZHSWhaVzBUS08vZjdlM3NPSEQ3dHViYTFSME1WaVBvekRkaE82MEQzNDhNR3RvM2RiNzdjeE9WK0JnZ0tCc1RHTXd4Z1UxQnBUV1k5SW43QUY5VDg0U1B6M1ByMEZrS0NxdkRXbUcwWW11cTR5WDhheFRhRnFLbW03T1gveGRHMEV3RnVIbXJlcjFkV0xaNnVISDhYTjR2Q2R6ekliSUNnQ1pDbWxkUC9iMy9tajMvOG5SOGUzbG9jM0g0WVAwVllYTDU1ZFBIMXk0ODd0ci8yTlg3N3g2bXNPVFVZNWZmcnMvaC85eWRXVHh6RW54MmErczVnZjNLaDJaM3RIeDhmM1hrTkhNcVhZZjJJUFJBVEVuTks0dmpKb1hWVUpvbWdwWThRNDVCU3RkOTB3bEN3VEN6RWxDU0d2VnV2ZDNlVWtBSEhlcXlnUldlS2lhc2xvUVZOWkFKQlVycmJyano3K0FBaENMR2tNM3JFeFhndEExcHZIaDBkN0J3ZDcrNVd2VGs1TzdqLzR5SGp2TFFsRUxhcEZFWEZuc2VpN2Z0Mk54dFhiYmxVa085K0k2SS9lKzBIajY3Mzl2VlRLdEdTWkJvbmJ6V2E1WExMbHpXYVRVM2JXQTBHL3ZXSnV6eTllcER6MFF6Y00vV0l4SzVvQkJBbVQ0b3V6OWVWbXZJRkF0ZXZSZ1FpZ1VkVXhqSEVxT0t5emJGN09sMVh4eCtJcC92Smo1ZCtYN2pZcGc1eTFsWFhYOVNNekFiSk9WeUJNb2lFUXhjc0wrY0VQelAvN0gvL2ovY1BEVisvZXdhekwvUnZqMlFzaWU5ak9hczlLQklnbDVVYy9ldjlINzMvdzVqZCsrZS84VC8rV3V1ci8vQS8veVEvZmZ3SzY3SHlLbC9IdEx0MDJOWWhlbnI3NDl1LyszdjEvL1M5UlVuMjRWMWYxNlFmdlFjbGk3T2UrK1F0SE4yK0xhVlFuSFBPUGRVMXh2ZjZqZi9hNzI3UHpONy8wZVNBOGYvcFlVMExDcDAvZTk5Wk9JMEZRbkhKY3Q1dUwrWHhuTnAvSDFjcDU0NXd4YkVvcERJaUlXZFd3dWNhNG9KNnRUcmVoNjJLOHVCcU1KV1JRbE1hNXcrWEI2N2Z1SHUzdkw1cWRPemZ2OUhmNk8vdTN1bkhZRE90dHQ3cmNYTWF4T084TlY4TzRNb1pMeWNpOEdVY2V3LzdlM2pDTWYvYnRQMzdycmJkbWk5Mm1hVU1NL1RBZzRXdzJDeUdNUWFZb3NVOUNHMk5NQ0pwemlURUN3SEs1ZTNUanhvTUhINE9odXEwZlBMdTRXc2U3akt2dVRQeVNUSXNBV2FRZmhwUXpFL3ZhVHp2MC85eXJBdjdxcmFkTUd6ZVJFbUxJeFU2Q2NJWEpscEJLU1Y3a2pqYzhtKzg4ZjNINjhjY2ZZMUpMOXZ4cVpadWRkNzc0cFJ0M1h5RjJPY2FUSjQvUG5qejYvT2MvODhXZitkcnl4b0dmNyt3ZDMvN3cyZXIrNDNOeDFjaSt6OGplZ2Zjbkh6ejQ3dS84TGd6YnQ3LzZsVy8remQvNi9OZS9mbkIwdERwOXNYNys0dURldmJ1Zi94eE85VGJDWHppZEZCUzA3emJmLzFmLzZzbWZmNDhOYmJ2MXd4Lys4UHpCbzdQbkw5WVh6M2ZtMVhwOUZXT0lLZWVFZ0R4RkZWdkw4MWs3bFZMR1RKK3p3TllJYUZheDF1WWNycTdPbmp4K2ZMN1piTVlzaUVXRjJEWlZzN2ZjMjJubUI0dTlVcUFVMVFJU2MrTnF6MWFMVHVtVFFManB0c0Nza0x0dWt6VEZBa1hSR011b3htS01BWUhheFNLWEZISzZXcS83ZmdBeWJGMk1zV2xhYjIwWWUyYWNMZHIxZWpNTjZQcnRkZ2loYVp0YngwZkh4emN1TGk4Mm05WHV6czZObmJtS2pzUVpuS2l4dGhsTGVYRnhzZTNHeXR1RHZmbXNkaUQ2NlpENlR3ZGoveWRTSGdWVUFXSXV6MC9QaHpBeVE4cHBWdGUzYng5N3gwV0tGQzFKQzZoMlc3N2Ntb085bllycmJ0di82S01QblBPd1BKZ2RIblRPWkdPejV1ZG5MNWoxQzEvN1lydFRaK3ovNkR2ZkdnS2lOSnVUazZIZmxLcEJNdTk5OU9UUjAvT2JONC9hc002bU9uanI3Yy8veXEvYy92eVhtS0E1dkhGNmR2cjQ0eE8wVlVHdEZOSlBGRWdxaUJnaEdoQXYyU2k5OXJrdjN2dnM1eTZmUFh2NDN2ZUhSNmZUK2dvQXh5R3BvQU5DeEt1cjgrV3lLZEo2VjAwMThZUmNuWkJxcXBCVFlzTE5aak9oTEs3RHBPamFVN3EvdngrNzBBK0RkNzZrbklmZ2pRMWpJRUpqdkxmMXJFWDJQb21XVXB4emRkUEVrdm93enVjTElCVENVSXBueTRhcnF0cHMxakVWWnZaVkJVb3hScEFpcWlFR0VjbEZ5TUFZeG02OVptWTJKbmRKUVRlYnpZY1BIcEFDcEV6ZUdEYmJ5MU5lSENYdEtwcTVTbUlZUTRpcTRMMjN6azRDblA5Y21jd25BN0ZQSDUxcEhhOHFSTlk3WjUxRlFtSm1FYVFrR25NZXRRVFViTUltY01XenRrbzVLZEk2cFJlaGZQdkRaMC9XRUdOL2N2cnhyVnNISDU5VnArZlBETkhwU2ZmNHllVXdVb2pDamt2b0ZFQVpyc1o4dGVwcnducTJ2N3k1ejRjM2syb2Vja3lxNUdqdTU3dTdvRkJ5VW1NK1RhV2RmbmFOSWprUEtlQ3NPbnJ0TmE2cmU1LzkvT0h0dTcvNy96cXBZZGp0MjQ4Zm5lY2lvb3FKQUNDVjB2ZmJ6YXFxYlNVZ09RY2lZaklsQ3lBUmN4SVpRMysxdmxSRzUrb29vNGhJenNDZXlLbEE0NXFMcS9WcXZRNDUzejI2K2RyeDdXNGMxMlBQYUdNWk0walJQS3RuUSs1eUdneGgzUzY2ZUpHbGhCQU1WNVk0RlMxYXR0c05JdGJlaDVTTVkwQWV4eEZKKzIwSElKcERqcUVrRzRZaHBoUzdycFFrSW1jbjU2L2N2YnU3Tjd1NDJnQTMzYmIvNGZzZmZlUG5qcXU2OWUwaVpRMDVEREVONHdCVW5HWFBacktDL1lTSWFybzhKanJnZi95Sm80cElCYW1VRVFFUkRRSTdGc09zTXUyelZFbUdOSWF1YThDWWRtYjY3UUNLUlEwellpa1F4OU1YTDhZRUh6MTRQc1l3ak4wUGZ2UlVWVVVDYUZDaFhDQURJUmpZcW9JZ2tUSXlHQVNyYUJOVUR5L3B3MmRYTy9OZDFGUlFRcEhkbzZNYnQyOERzL0JQZG1FQ2lxSmFOSmNDVFBXOEpXZUlEVlZtZVhEejNzMVhMNS8rQUdLYXhqcEZ4UnFyQ094ZGpMRWJ4ajVFWmk2U1orMU1GV1RTNmlIMlEzOXg5b3dJNjZiZVhLeUppQTFYMXBJaUVtLzdXS3N0U2EvNi9xT1Q1eCtjblQ1WnJTU21CeWZQQVBoNGJ6bXIvYXoxYUZnS2o3RVlFTU0wYitvUUJzT1RRME5DeWluSG5MS0lHT3RBc1VoT1pkejIyeGhTWlJ5aU5wWHR0NXRTaXJNdWhKQnpGaEEwWm9qaHc0OC9NazVpSExOa2xmclJ3NU4zdnh4YUltUjI1RUJsR0VPV3dvYnJxcHBDMS85L0FRWi9xc0tqVWtSRWpYR0d6WlJQbmxKQzhBQ0NDcFlJbld0YjhqdkpoQlJob0FKT0phOHZMNjVXNjZzaHRmTm45MTU1YTNmL0ZuTzk3YmNocjhkaGkwV0lWTkFvQWtpUmxGTXFnSVJNREV6SVNMUzdkK1BnN3IyVHRYejQ3UExlOFk0b1ZqdkxONzd5dGVYTm01TXNkb0pLVGg3K3lYYzVEY3RLem14dFBXdlJtSUthVXRvTTNmN0I0ZmJzZzVpeUtoS3laUmhENzV3RHBhNGIyaWF1TmlzaW1MV3o2NkEvZzdrRUxCeERMSUtLUElSeENDRVg4ZDVYM2tsUkVBU2s3VEQwZlYrUVRGMmZkdjJMSC8yZ0poYkgyN0ViTkwxMWRLUFJDaFZGRVkwandCamljdDdtMml2b3RVTzhsRENNZmJlT01RRkFLV0tkTTQ0dGFSY0d5TG5ydHBXajJ0c1hKeWUzYjkxbTVyT0xjOTlVdm5KakNDOU96MjdkMnBzdm1xdlYrdFZYYjdjdzFQTjZ1dzdEY0g1MFowZllEdU1Bb3Q0Wjc4MDAva0w0Skl4RWYyTE4rUjhsTmY2Rm9BSWhwVnhLQVZSMkpFbFRDaXBGbFZUUkdqdXIyZ3pHeGs0RVREZU1LWmRZU2hpN3A0OGVicTR1cytaNGRacTdxMWRmL2NMQjdidG1NVnR0c3BZMDlwdSs2d1M0cWl0RFFDUkVNc1pReHN6c0dPajQ5cXMvKzB1L2VIano3cE9uWjMvNHZZOVNmdTJvcGNPYnR4Wjd1MzZ4UVAyRWg2ZndGdzI3Z2tpT1NVdXh6cmF6bWJVbXhzS2kzY1dMRHorNmYzbTFHZ1g3VUJhTEpzWmgwaFJzdDcweEpxYjQ0c1V6WXFKanFxdDVXMW5SbUlZZWhZbU1xNXBZMGhoS0VqVklCb3dodHNiT3ExbERkcFA3RW9manVyRWxsNVN1VXM1TTNqcWJNNVhTc29WWXpzOVhHUk43QW5KTXNMOWM1cEsyMjI3YXZiR0I3V1k5bjgzNmZwaWlTV1BvNTR1RklTTElNUVpqY0F3alNOcmRYVjVjbmp0YnNUWGJ2c3VTclhFbGxkQ044MWx6c0w4WHhyaTNhLy9zZTkvNzJxOTgxVnJ2cTNvVEo1TWMxYzU1WjZZUitWOUIrdmxQbDBEZ05WS25GSWt4NVp6QlVsVzdLQkdrRUNJQWdUSVNLRE1aTThhMHVibzBZUnlrbEtMU2Q1dHhHR3MybFVYck5IVW5EOTcvbzgzbTlQRE9tNHRtdDNhTHJiczAvWGE5dnR4dXQzVTFOY3JLS0VnWThuRDcxbHMvOTlkK2RmL20zVzk5Ky92MzM3Ky9qZUhxc3Yvc29iOHp3NFBieHdwS2lrby9oaHlkbkVEQVhFcVpKRjZHRFFFeTBlWEo4eWZmKzhIRms4ZStyZmIyRGg4L3ZTUkdNcnhjN213MjI0bHZOQTRESWFaWSttNWIrMWJTNkJ3WlkxVVpnYnl6ejU2dVlnd3FZbjJsSUhYbFVhaXQ2b1Z2cWhadXU5bnRnNFBUcTB0OS9PQlBUNTZOdVZDSUZ2Q3dtdDlhN0RlenhodXpHbnRiTVRPUTBTSEVVbklZZ3lHcW02YkxPZWMwUFN6NnZtL2JGZ0RMZW9VQU1ZM0RPTXphbmJxdXU4MXFOcHV6TVlESWJDQ0dsQklxTnJQWjhmRnh0MTd0enFySGo1NTk3Zk8va0owSDFLT2pHMGk0NmJZeEppU3M2OXBiOXpMeFJ2NUhQMDNncFR0SVNza2w1NUxicHAxWHpYWWNzOHEwSFVNazFTS29TcEJSdW5Fd09hZFNjczRoaFdFNWExcERrL1M5VHlIbTdmTkhQN2hhbmUvZmVtTytkMk01MjJtYlhXT2JzL1BIbTY0alVFc0NVbExVNHp1dmZmVnJ2ekFFK2NNLy9KTkhINTljcnM1aUhOLy8wS1l6Y3lwWFY5MzZ6Yys5YzdCM29KYXZrMWsrQ1d0Q1JBREpSVVZTR0QvNjduZGowcHppUnovOHdlTWZmTy9Xelp1YmVPV2hPenJhNmNhUVZJYVV1M0h3emhsanVuNm9QZS9NV3NlUXcvcGtsU3Z2QVcwSWFmOWdkN3RaaFhFd0JMVXp6TlEyRFRJQ0tCazgyajhRM082UXQxYUtzWHUyelZrS3dEYkZWdUhHY3UrZ1d1N3VMbzl2SEo1ZW5CWFVUZHllYnM5VFNOWllRZHVQUXoxYktLRWpDR052clV0cFhLL1RmREhmZElQM2ZrSjE5ZjIycW1wbHMrNTdJbmFXbVEwUkcrT1dPenVRNHpnVUxkZWY2UFY2ZS9mdE8vWHVVdGtNT1czNkxxYnNETFZ1bXZOTTBPMk1MNE1NUHQyUC9PVWNpNy9FRFFkRUxSTjFSWFhNQVVpOU5kNmFicnJJWVFyNVFoWXlRSkhKenhxM3MyTVFJZWVpSlZhRzZtcFdFNUNVRklNQXN4WXNaVnk5ZUx5NXJKZUhCemRmWGU0Zjd1MHRySHYxK2ZPUHQrc1ROWlNTN08vZitPSzdQMnVvL3VGNzk3czRMdWJWdSs5OHVXMmJmL2RuMzMrOEhnTG4wMy81YnoyVzJjLzh0S01aOEFRWWVKbWJDd3FBazZrRVF2bnVIL3pCRDc3MUxhTThiQzhYVGFQR2J3WjBsZlBXYlBwUlJmc3U1Z3lOTjRpWVVqVEVsZDlUMWZPTGl6Nld1bW42elRoclo5dXRIY2ZnbkdXSVNLWnFadDdYdzlqWGJsWlhNOGpTT0wvZjdCemV1Zm5pL09UKzJmblBIZHdjTkt0cVcxV3Y3TzAzem1rV1EzQnJ2anVVbE1wb0ZHMWRJMkxmUTBFVEM1QXpJWTR0WWhpRHM2N3J1cnFwVmZYaTRtSzVzMlRpUWVQenMxUHZ2WlJpckIySHNhcXFNUVltR3NkUUcvdml4VGxSNmNkUTFmN2V2WnYzWG44OUxHOE9XSWZRRDhPZ3VYanZLdWNtSS8ya3BFZVFUMGNNL0VldmtPdncrcGQ1b3dpUWN4Nm53R1ZyclRVVDlxT1VvaUxYR1lRQXFzQ3pXWHZubGhsRFFTMEdjK1ZjelZTWmE4dVRBSWhxYlpTemhqeDA1dyt2VnBlN3U0Zkx2YU5tc1h1OGYzUnU4R3ExZnZXTmQzN3F5OThjUS9xemIvL1paZGZWamZ2Rm4vcmNmL0ZMUDd2WW1iMSs3ODcvNHgvL2l3R1lyaTQyWFk5RWh1aDZmai9GSUNLSUlJSnFFY2tGbUk5djM1a2ZIVnJuSG4vMGNmZmk1UGplNi9jTzNuM3l3KysrdUZyRDVhYjJWVDhtUkNUTFhSZHlMSWQ3KzJQSUY1ZVh4Q3lJNGFvblpSRTNET3NRTzBSa1oxdGZkNXNRWTlsWkxwZnRzcloyR0lkRnZZdldTQzRwNXJiSWI3L3plWVBjYVU0SW9VdEdDNEl3bUthcGJZb3Z0bFRWTmRjbWpFRVZTdEZoSE5iYnE1MTJsaFNHTURqbndOcE5TTTRhSkhONXVTS2lwTnFGMEk4UjBUQm5oNm9BODZZVkVXZXM4OTVhdTk3MjY4MzYxbjU3MVYxK2J2Y3cyVG1SR1RlcEg4WWloUTJ6c1lpVHh3SkZsVUQvc3I3dTA5TGlmMjgxZWowWXAra1lUQTREdzA3a09xeGVOSU5PSkdobEJQUyt1bkhEdlB1Rnp6LzgrTDdMeVdpQlV0UTVJaUExV0lvRlZWWG5zQUZNQUtsSTJqeDdmblhDcm1vV2g3NmR6NXZaNFkxYnk1M0RoNDgvM25hYmZ0MDEzTDUxNzhiZXpESEd2L1l6WCtxRy9uZCsvOS8xYmhHeUZRSEFETWlmL0g4RVZFQklRRlZ6U3UzKzNqZCs5VGQyMzNvN3B3SC85Yi84OXUvODgwZnZ2Ly8xdXo5alhyMzc1OS85ZHRzMFpFMFhCbU1CSkZuVTVlRmhWbjc4OU1SVlJNVGVXd0JnYTRES3R0dW9sR0VjQ21BY2h6SksyOHhVOHVGeVRra0p1SjNOVjFlWHp4NC96akcrZG5DOE5NNGpMZ1MzY2N5VmlhSytxcXE5ZVF4anppQWx6K1l6VTVseEdDZTdiTmYxV2Frb2JmclJHbGVRMGZwVXNCdTcyV3lXeWhoVHpxS29GZ2xUVEtvTVVKekwzcGlTTTFpYlVocUhVVXNwTWJkMWpVVzdUWi9ucUk2NmtMb2hBUnJyR21aWFJPVWxKQjkvRENMMzR5eEcwZXZiNWQ5L25haEN5U1duaElqRzJseWtsRTlicUdReTVxT1FnakVMYi83ZTMvOWYvTjd2L3M3OVAvKzJEaU9nWnNSWU5PYzg1aFJETm1TODkvTzJOZ2JHR0hKSU1lTzYzNnhlckxCcUV2QjdnZ3p1OXQxWHZ2VGxuL3JSOTk0NzN2Zjd5eWFGZnV5VGJacWYvOGFYN2o5ODl1M1RGdzllWEh5dEc5cDZwbG9JQ1NadHVDb3BYeXRnUWNFWWQzaG9GM3MycFZ1dnZQbkRuVDk2OGZqajg2ZTNMeTZmbjUyZTdPenNLYWczNUwydG1DeHpWVlhQbnAweDIwS1VVZ1NReXJ1ZG5SbzBoekdFckxGQUgySkk0OTdPem5LNXM3K3pVMWVlREdPbjFybDZmMi9vTzJkNFprM0pZU1BaV0xia2hoenFlWjFKZDI4Y1B2LzQwWG0vV29XK3FXYUdYZE8wcTlXR2pHSERGREVvb21vTTBSaXo3Y1lrRU9OWWxHZDFXMlRNcWM4bFdUVEdNWUNHbUcxTWhxd1VpREVYUkdQSU9acDdQSnk1NDhPZCtXSXhBcVlZMTl0ZUJDcnZGN09abFBqb3lhTng2SFozZC9mMjlsdzdBMEVSVUNoRmNoSDhpVVM5LzBERmluK1JKVnNZamJlV1Vaa3dUZkt5bHdSQkFEVElSVW5KbUNkUEg1MmR2Ymk4dkdqWml1R3hqMzVuMWl6YkZuQk1aVkhQbDdQNXhkT25yOTdjMjkzZitjR2ZmM2ZWYlEzYlZGS1FjTm1seC9mL1BJWXMrdk52dmZYWnIzejVpd2Q3Qmhndk42dW1iYnZObXUzc1ozN3FzODgrK3ZEcDVlWEZlclc3ZjRnQVJZc0M4R1JESWxRbHBDbFlpb1JRcExBejgvMkQ1ZkhSMCs4OSs5WWYvdEgrMGQ3UjRjRm11eDJIMEZqYjFyNUlRY3ZyYmgzSzJGWk5ONGJhZ0FJc1pxMWpUcmt3MDlpUDJ6NW9LZnU3OC8zOWhVUFFMR1BJamNFa2NkV3REaGJMMmRFTlRhSWhzbFF4QmlVeTN1MDRzM3Y3YUpYRGFyc3VPZmFwNDFuRjFxcW84MzQybTUxZVhoVFVVZ1FRZ3lRaWNOYkhVbUlCVVRxLzNHakd5ck1Da0RIcHBSY2UyRzZHT0lic25FWHZzNVF3REhkdTduL20zdUZoUzZEU3gwRXE3YmREMzIwSmNsUEp6SVJ3OXVMSmUzL2VqMXU4ZCsrd05YVmJSYVZwRkNCWmRFcGUray9vYjEvMmhwcGlMQ0xlK3RyWDNqdG5UUjgwaTN5Q1M4RlBaSVdxNWgvOGcvL0wwOGNQMHJaYlZuT3VteHV2dkhMcjlkZG04K1hPemc1YS84NWI3M3o1eTEvNXAvL29INjBmZmZUTnIzeHVZZjNIano3b1FzY0dOLzE0dXVrZm5xd3VucjMvblQrMXp0Z3ZmUEdMK3dmMXF1OGVQajQvdm5tOG5POEtwRmR2SGYzOHozN3RuLy8rNzYzSFpDemtwRG5IUE1aK0dFcEo5V3pXMVBQcFdMTzF4ckFpRklSbXVkeTdkZnZodC84MHJzTXJYMzFOc2Z6d3ZlOWFkRG5sSE1ja3VCMkdJSUNXeGpoNk5vVFNOaTBRcnpaOTVhc2l1ZS83WWNpdjNyNXhmTHgvZXZMQzFETnVaaUpsQ0NYRzhkR0xSeUdYejd6em1ZY1BuNEt0OXBhTEp1ZHhITnY1ek0zcUVIdU5LZVo0T2F4R3pkWTVkaFlKNGphMmJYdTFXVTljelp5VFFHN2FwZ0QySVNRbFpwdTBoSlRhZVNXajZjS0lSRm1FQ2V2S3h6UU9jYVFVRWlwTElTbWhhNXNiZXhjWHB5bHpBZFBIY2JYWmpKc09kZlFpdXNsbTZGL1piK3QyLytqMjdadEhCOXZOMEhWRGNRN0pJenU2SnA3TFh4bFE4ZVBYaGs3SndqRm5WWFhXTkpVejE5c291WWFDRm4zWlFDSVRnekhtOU5HSFRVN2N1S3Qrc3p0ZjNMeDlsN2dheHJ4WThKMmJONVh3K3gvY3Y0emo3LzNSdnoyNWV2ckxQL2N6UC9YMXIzejgwZjBuejU1ODhQSGp4cFdqNVVKS2YvbmlnL2QvdURnOE9xamFPOE1ZeTVpNnZqaGJRTHUycmQ3OTBtZmUrK0IreWV5cWF1alBMcDg5ZWZiZ28wY1BIMldWejN6aEs2KzkvVzdLSlluTW5EWFdNWk1TVnZYOHh1MjdkakhyaG0wY29pT25DblZ0QjgweFlqZm16WkRKR2lKRG9LMTNsdFFBZE1PWVUyUzJJY1pTOHY3QmNuZC9FWWUrcmFzYnh6Y3MxV0hzRVhFSTQ5bjJVaGgzTC9aMmRtZVNaVDBPMWpuVDFIMC9ucDQrTndRWDNjWDVzSHA4ZVdwM1drc1VZMitNSFllK2FlcmF1ejZPYUNobkdmcVVVaitmemRsV3d6Qm0xYUo0MVlkUmk3ZStDOFU0TW14QU15azQ3L3VTMlhEUnlLQUh5NzNMMC9QdGJuV3czODZYQitqYU1LYnRkdHR0TG5SN2JuSGZOdVJhUE53N2F0djU0ZEh0M1lOYnAvUnNkWFZ5ZnQ1ZkpqaTgvZXB1dXpNVkd5OUh6OWNuNHkvakdCU0FBS09XbUJNU1ZjNDBub2xBUkppQUNWQVJZZkk3VDdreUtvVG0wSnRmL3VsdnhKai82YmYrdEVEcCt6NTBQYU1KWFpjMVZLNTY4ZXowL3ZlL2UvSGs2YjgrZWZMODRlTXZmZTZ6M3BzdWxTR1ZmaXlPelA1dUhjNnZQdjd3KzNVN0k0TEQvVDNIN3RIREZ3L3lSemR2M3J4OTg5aTQrczZkTzhZWVl6aVAzZjF2ZitmN2YvenZuangrMk01M1hyM3pxcGFZVWlvcE8yTW1kbjNTNG95NWRmUHU4dmo0OFhlL2YzVzUzZGs5cUZ3N2pOdFNpbk8rZE1FWUtxVXdBNmdhMHpMcE1JNWd5Rm1ySUNwbE5xOE9EM2VsRkZMMTNsZFZOVzRURktoblRYRkRWOGFucDQ5U0hvK1doNmFBRkczbU8zVmRiN3Z0K2NWWjBQSFIyZU5PQTFVV2xEV0NjODRidDV3M2ZUZnN0TE5jOG92TDg4bGlLcW81WjJONEhBS3lsQ0pCTVlQMFkxYXltMzVzSGJXVnhhTGVzSGhUejF4dFdidCtWcm5sM3AyWWg3ZmVlZnZvK0VDcktuVDVZbk4xZnZhazJsNEZKMzFkbVoxNVVkakVUdVZGVEhGY2IyaTdXVDk4K0hBVFhMMjdOMXYrWndrOFlvd3hSa0wwVldXTVJWUmpEQ0tXY2swTS9Ja2J4L3o5My82dmZ1WG5mdWFQL3VSUHYvWGgvYWZiZm5QeHdyQVhwczJ3ZXRSZDdlM3ZyODVPdyttelYvZVhSTEo5OGVKZlAzM0NWVk8xYll4cEhGTkNVVWk3TTcvZTloLy84SHUrYXQ3OTRwZVh0ZXU3OWJhL1VxU3Fhc2dIRkRGRUpSVVFHdnUrMzZ3UTRQalczZDNEV3dGUW9NeU9EczF5V1FDVEZKRVVHZXU5blR1dnZyMTVmbDd0N0I3ZnZnSC83dDlDRWdUcXgrZ3RHMmZXWFJBbEpoVkovUmo2TVMyV3JhOGRNYm5LVlZSNVVnSk5RRWg4dFY0Tm0yaTU5azF0QUp5bklRMFB6eDgrT24xWTIxcUZGanRMYSszenk4dkwxZFY2M0pESDI3ZVBkeFk3Q0JxRzdURDAzaG95RkZJVVFEYW1NbFhKbVF3SnBGekdxcXFydWhyNkJHU1FKUmZKVXJKS0ZqRUZscGFobEpKa1BtK2tKTTllS3R6MG9iSnc3K1ppTVRmZDFWbDdIQWx0U1FsemxKTFBWNXQ2djh5UDk5YmJxN2crSDdyTjV2VHAwUFg5dGl2YkMraXhXNitIWVhUT3ZnejExays4SnovWjBPSVVyR1p5a3B3S2s2bHNaY2xralRKcGlBUmxFdmRPS2tFUlJTNEM1cmQvNnplT0Z2UE5adlhLblp1WEh6eFl2WGplMVBOcEdwSWJYellYWWJQNStsdXZ2SEs0djFtZmx4QVQ0TlBMMWNmUFR5NVd2UnFiRFpRY0hQbTVkVmZEeWYwZmZXdStzOFI3cnpTK3JqUVBRN3BhYmJOMkYrZVhOL2VhdnV1NmJrdEVYRlhMdXJuejlsdjFjbTdaMzNyam5iM0RmUUZibkNrcGdvb3lPSkpmK3Vtdi8vem4zZ1NuWTljNXdxc1NzOUoySEJBSW1Fb200dzFDNmJ2b0RCbkRLYWZWYXJVem4wOTVEL1BGUWtURHBtZFhQMzUraWtsZXU3ZlREMXV3WUNycVkySW10UGIrMmZPenpSYWVNZ0lLNEd3Mm55OW1kY1V4UmNrWkFMeDM1K2ZuM1dhRGdHR01xUUFZUXBnZTBxWDJSa3QyWHZlWHM2R1dia3d4UlZCbEppS1dGSW1JaVR5emlNWVlER1BYOVV3V1FaOCtmZmJPcTI4N3d5ZlBIczkybm5GOUIwdnZRWUJoQUFob2V1Sm9FSzIxeHF1VWxISTNEdjNZcjllaC8rQkhpOFhPN1Z1M2FNcWRWZ1g5aTNEUUgxdkZUUVpZZ0pKelNzbXdxWHdGQUora3lWeW45NGxNVGhORmtaSUZqWG4rMGNmOXZMMnh1LytOejMzeDhmUHo5VENtL2lvWFVZQzRsbUxNRjk5ODg5ZC8vbWVQOW5hZm56ejU0TU1QVDliYldWUE4yL2IwY3JOYTkyQ1pTWlVLU21nRUYzR2JuejdZemx0enNHL1lqa041OGV5c29GNWNuSVBjemtuNmJiL3B0MkRkblh1dkh0eTZVNEFReXNGeWFmZG1LUTJVTTRjckpxaUFzV3g5YlhKMjczM3dubEJaVkR5MlZSY1VjcDhKc3lSaUdvZUNtR1o3TzFDU043YXFUQ21wSHlNaDdPMHVtN3A1OFBqSm1IVGQ5ZHVyMVJ2M1hta2FmM2wrNFdkMWxHeHJ0N05ZclBzeEVzejNkMVBLSllzemR0WTIzbEhJb1l3bGhKTzZyaTBpa3Q5MGx6bEY3NnRZY3A3QTlVUk02SXgxenNhaUFKQkxaRU1XWFF4eE8wUXlqSVNsbEM0azlHaVF4akZaeTFLeXB2SE5lM2Q4SmFIdjJMZldMamZKVW9VR1N4b0hTNUFWUDNyMDRQNnpwd2JLakl1M3lBQ1ZtN1YrWVZ5OHZId2Y0SGtXRVo0WTh3b0tuOEI5ZnRLNmdvcElLaHBpVEZLY043NHlnQnBqa2pLRnFSUlZBQUtheU1RSVNTQVhOZi93SC8zRDIvZnUvZG8zZi9FYm4vblNIMy83KzAvT242a0lFSWpJYmpWNzUrN2RyMzdoWFZQMDVNWEp4V3I3N1B6cTJlbHBYNFFCS2tlaHNQTitWbG5XZ29YdjdkLzhhei8zVFZzdDNoKzZPTHEybmFlb3d6Q01KWVF3THRyR3MxbTJEV2dCa0lQRGZWODVDa01UKzNucFpGZ3RNQytxT2tzdXFaeC85SHk4V25PU3hsZHZIaDI5Ly9pQlk0TUtnS1dxcTNVZmt4WkYyL2ZSZTJCbklXbUtPWXc1NXp6VjRLL2UzVGs1T1h0eGVsSFBsK3ZWZWxIUGZkTThmdllVaWlpQmlNd1dPOERjYlhzRHlFVGVNaGlQQkJJR05iNmtGSFB4em5YRDZKQVFLZVZDYk5oYVM5aHZ1OGEzenNsMXJrU1JraFVCUzg1OUxJcHNySEZBVjV2aGNMODFLcHR0YncwalV5bFlSSm1vOXFiYnJGKzlkMVRadE8weUg5d0ZlekJzeHU1OHZlcUhOR3lkWGE5WDNkVzZyeXEvdjV4ZmJWZVhtL1d0VzY5KzVyWFhQSWh6OWEzYnQyOGMza0JpaFArb3RoUUJJZWNjWTh3aWpXSHZMUkdLbEp6enRYa0VkTnE3cVlxaXhwS0hJT1piNy8vb094OS8yQTNqMGVHZFhHSUx1TGU3YjZCVWRYM3Y2TmJCems3c2hoODhmdnppNG53VndoaEdOcFkxZzRiRzI2cXFaNzQyckJVeEE5ZWFubjM0Zzd0M1h0MTNpOGRoMkFpMzdieHk5UWZ2ZlFTYWRuZmEydWpOZzUxMzMzN3o3bkxuamJmZjNGL01GMUxHeHgrTmw1ZXB1OXFRckp2V0wrWlgyM1hGcm1KN3NMKzdhR2NmUFB6b2gvYy9QanZmYlB0eGxSTGJXaUE0WjdzaElXbmRlRUFZeHRodmczTzhXTTVGSVkyZEtsNWViYm94dTFhdHI1WE0yY1ZWSExhTnI2VHJxclpOQlZiYjdUQ01qWE5zckNFWFUrbjZya2lCa2tvcC9UaWt5bHRqcXFZZGh6R0VzVzFxSXZLbWFrV2hnREcyNzNyUmtpMmh0VGtsSW1RRVYvbnR0bU8yUndjN0NOazdieW9uSlNPU1lZdEVNUXl1WFZ4Y3JpNWIrUEliYjQ5RjUvT2REdDJzbmpmVmZMM2VYbDJlT3dkeE84UnVTS1BWRkxydGNMSzl1dWp1djNoeDl2cnR3NmF1OStlTDJyS1pyZ1VpMVI5UERQeHhIelVvSk1raEJpblpPVHR0TG9sWjlWT0c1NWVuUklxT2ZiZ2FrdWtGWHp4NS91R1QvL1pvdVE4aTgzWm15VlRXemRvWkd2N3c2Wk1ZNDZiYnJyWmJZSzdydW00YkNIbUlzYW04c1ZYam5MSG9nYnJWZWpXRUQ4YXUzM1IrLzZpNmNXdDMzeHcwdFhNQWgrYjR4djV0M3VhSEwyd3VYemc2bXIvKzZtSm44ZUx4NDh2ejg1MW0xdGFPcWwyQmNuS3hZc1M3ZXdkcytPTDBQUFpkUVA3V2Q5NzcvdjBIUVZEVXFwYVFNcEF5b1hlSWJBQWxoSGl4SGtrcGhWU0pEcUVzbWhvUVJFcktKYWZFUklZNXhGUlhyWlNTY2luREFKQldxMVU3bTZsSVNsbUZES0ZobzZJcEpBRHd4Z0ZDQ05FNkZ5V1BNUmhqMk1TY2MxM1hwU2dSR1V1cjFjWkNYZm1hTUROelc2RnJ2RFB1YXIzeXJNd3VwYWpNSUJoTFVFUnZiVzI5Z053ODNuM3pqZjNEZzcyVEQ4OE9YNFBidDNjTDJzVk8yNi9XVjV2THUwYzNYQU9YWWR5dVZ3Yzd5OFhCN3RQTFo2dStLOTIyWmRsZDdHeFdGNkFGc1FnZzZVKzZFS1pmRWZFMEd4V1FXR0kvakFoU1c4dUVDZ0pFZ1B5U280RkZSS0FBZ2dJSmNOSmtRSEIzc1QrZk5mTzI2VFo5eUxMcXgyaHBTSEsyN2Z0aGtKSkR6akdsT2RNazBnZFVaOWd4K01aNWEwMktsUFBDdTN0dnZubjMxcTNEM2YxWjI5YUxabmRua1hJcGNmUFZ6OXh4M25RUGZpaXhlTjhralUrZmIxOFFPZWR1M2pod2JCemg1ZG1MMlBmM2JoOGhtYkh2dGwxUFNsZHgvYjMzSC96Sjk3NlhrWUVzR1U5WmNwRjUzWGJiemhwR3hwZ3pJakpqVEdVeUdnLzk4TXJ0TzhNNGlrSmRWeUlLSUlYRk1iT3gyNjREeUZhcUdJc3h4aHJUOTExTzJScW5xc1JrNFJvN0JnaklSSVpVMUh1Znh6SEcxRFNRYzE2dk56czdTeEh4M3JWdDA2Y0VxdDU3SmNvNXJ6Y2JKcjlZN0Z5dExoRng4dU9UZGNvT1NxSVNxOWJua282WDdXZmV1dGNzNXJ0MjUxLzk0Lzkray8vRnJUdXZWa1YrOXUzUFBIb3hDME5Qelh3TXdSbjd0YysrZStmbTdYN3MvdnpERHhySEJCU2p0dTNDZVk5RXVlUnJ4dWVQcVlqL1FxUUxxaW5udmg5Q0NBQmduQVdBRkdQSitaT1M5YVhoRmlaSWh6SXFzMWxVelh3Ky85emJieC9mUFBxalAvdldndzgvNmtPUFdDZU5KWWVZNGtSZW4xZjEzcUs5Y1h3UVFoaGlVSFhEeVB0emYyLy84TTJqMndjN3UxVlZ0N05tdnRocHE5b1FHbWJ2VFZJbVVCUlJKRDI0WVl3RktFV2p4QlQ3b2ExcUxiTGRib1JrZWJoN2NSSnlpaUZzaDM2UW1KcWQvWC8yci8vTjkrOC8yT1lveEFYQXV6WnZ1MVJHWXlvMldIbC9lcmxXWkFSRFJNaGd2Y2txdHFKMVA0cUlzUFVWVGdsblEraEtOdXZ0QUZxOElZMlNRcXJuTlVwMlpzcmJMZ3BRSms0UW9ZZ2lrd0lRay9mVk9BYnY2OHA3UkRMRzVwekdzVGZXYnNPbWFwczg4bnE3M1ZrdVd0Y01RMmlBTDg1WHhqbnZxeERHWVFqV0dIWTBqR2t4YTV5RGVkV3l4bjY3NnJicHp1MUZlL3ZvN2p0Ny8rWmYvY20vK08vK3dmWnkrOW9yYi96bVQzL2R6dHcvLzhOL2UzYVc3dDQ4ZXZQVmU2L2RmZldubm41ZUFTby9uOCtiVzYrKzljWm4zMFVteVlVVUZHRGlmUDVGNEZXWnJQY3FJaVdYTEdYVERVTk9BRGhsRGVlY0pJU1NSdFdDcklTcXBZQ0tsS0pDSXBxVStLaXhmYjkxekcwenU5cXV6Njh1RFp1NmJZdHFsS1FBU0ZqNzZzYisvc0ZzWGxsZWVIdTB0M3U0dS9mWmU2LzgwaGUvOGxOdnZmM2F6VnV2M3I1OXRMZTduTTkybXJyeWpvMHoxcFlpRGdVQWk0Q2k1QnhTQ2pHbUdFWWlKVlJKaVlBQm9PUTRuN2VDRXNZMGhVeGgxaUhxZi9zdmZ2L3gxY3I2R2dHUllZakRtSUp4cUpBcmIxUzRId29nRWFrb2lJSnFNWWFxdWlhRUZBTWlwU0xqT0RBYlJHVkFRcW9xYncxdk5odEdYTzdzT0c4bmRwaHpGUkZKbVdUcW1ZaUllZktCaVVES1dYSUNnUGw4RnNLSWlDa2xhMHpNRVFESjJHRWNtWm1OalNsZnJUZFYxWXdobFFJSVVGWGVHTU1BMXRqRnJIV1dqUllzcGE3cmNUUHVIeTUzRmtmdHp2N1h2dm4xci8zMFY1dFo4K1R4ZytlUEgzempLMS84aFc5OG95SmNYNTQ5Zi9iNDh1TENHZDQ5T0ZqTVpyTjY5dWE3WHo1Ni9jMVM4aWVCRzU5a0orUkpvamFtNGZwckhNY2hqR0cxMmF5N0xTTHQ3UzduVFpQQ3VPMjc4OHVMRU1PdG82TjUyNGlrSWlVbktVVlhZOXlFd3E4Zjdta3U1ODlQbmp4NXN1bzJZd3B0WFIvczc1V1N4aFFSc1hadWQ3NnpOMXZNckwxMys5WTN2LzdUNzd6KzlydHZ2LzNaMTE2N3ViZS9NNS9ORnpPeVRFUm0wbWJrQktCYWNpbEpTeWFFa3BQbXhLb0d3SUJxeWxveUkwMjhMQ1NNTVNBak13T2dSY1BFWTByUEx5Ly8rRWYzQXlBak01SWlpS29TWkJEckhKSWQreHhEUm1PR1lXVG11cW1zTlV3OG04MFIwVEFoOGZuRnBZaTJiV1BZeEJDQXFhcjhHQWJKK2ZCZ2Y5NDBPY2FjTXpKWmIyTXBZMDRBeW1RUVVVcXByUE4xWlpqQ3RtdWFkaHlqOTc1dEswQk5VcklvTVNmUlQ2SzB3dGdUY0F4NXZkNENJak1CSUNFNWI1eTFNUVFpcWp3MzNuYnI5WjJidCs3ZXUvWFpMMzVoNzhZeHNGSEdkdGErOWRtM3Z2NHpYMTExbS8vdW4vejN2L1J6UC9mTnIzM3QxdEdOODh2THE4MzIxaXYzM25ycjlmVnFBNzY2OTRVdit1VWVhQ0ZqaU5nQUZTa0ZRRlZ6S1NubkdFdUlNYWNpdWFSU2tzaDJ1eDJHMFpBNVdDNW5sUitHN2JwZm4yOVd3N1pmTHVadFV4dERLcHF6cGdMclFWYXhtSys5L3ViQnptN1ZWS2IxZi9hREgvejVlei9DbmFVU1pDMk02TWcwcnFxTlk0R3Zmdm1uM25uelZTSUVRR3VRUUNTa2FmaWFWZmdhWTRaVHlERWlFa0RLQWxCVUNvQ1NNU0tpb05hNWZydkptS3FxS3FWSUVWSk1JVElpQXpBeGV4YUM5eDk4WEpRSWlhNEY5Wm1JREJzUTdmcUIyU2VWSUZtaVpCRW81V0E1SjZJVUV5QmFkcEp5ekdsaVQrenU3YVFRVXdqRVBNWllTcmx4NDhoNUdzZHRISU9na3JQRDJQZGp5am16aUxHR1dMV29ZMFJVWC9uUmdFcXVhcmRhWGUzdTdwQUJJQjNIWUJnVlRkZjFVc1JYTHFheGFmeXNiYkxna0NJeGlHQ0lTYUdnTXltbE1ZeWxvbDRUb0k3RGNIUjg2L2pXSzJTTW9KMVFWVmxMdFdqLzd2LzZmMlZuN2UvOHMvL2hmLzRidi9YNjBlMWJ2L0hiZlVxSnpNVm1FMktFeFN4bU9MOWFNeWdSTVNJQWhEUk9MR0lWVFNrQmNDNUZZaVpFWkVvNWhaZzBpNnVZbVlFUWllZnR6cXplYk5hYmJkOE53MERraVJoQWNzNHlqTEJKSm81aGRyUCsrdGUvL05ibjNuN2pXNjl0dG4ydnBSdUhQZ1ROeFR0bXhNMTIvZWF0VzVYaFo0OGZIZCs4YVoyTElSQXFxa0tlTkFVQWhFVUZpZ0pDa1RLdDRBRWtsV2lNS1VWS3lWUEpoS2p6Mld5eldaZFNFTUF3anpGMjNiQmN6RWxSSktQeEY2dnV3ZE1YN0ozbWxLVTQ1MGh4akxtUTVxeWxxR0ZnYXdUUmVBc3A3Ui9zNys3c3JxNnVja3JHR0NBT01SVVZhMHpienVadGN6NzB2akxXY001bGQyZVp3aWd4VzZZcFJXbm90MFNtMy9Zdjc3OUNaSHpsNjZvS2tvM0Z1dkZqVG1TTVVSakgzdGVPeUd3MjY3YXRoSFNNSWFmU3pPcUtHNUVpQXNheUEwTklvbUtOWVlJUUVpRVJtekdFcHZXK2FwcTZhZHQ1U2xJWm5vUmV6T3lkVjJaaC9wdS8vYmYvaC8vVC8rM2s2YlA1Yko3NzZKanJ0aVdrRzR2RnYzajQwZmY2MGN5WEJNQklsZlBDTkE2OTVBUk1iQTBoT21PUnNLVE1SSXlVWWhxR0FRVDJkZDljTlJzWlF4aXF5bytxR1pTY1JTSUZZalpFV1V2V2ZvMlhXN09CZURwYzNmLzRmWFE2WDlTZi84STczL3ZSL1JDQ2xNTE1sczJ3N2Q3OTNEdS85QXMvMXdCKzlOSDdBSHJ2eml0TWhBUklLcVdVa2xGWkNVRVVZVUxTS0txS1pCQlZMY2dJVWhCb1dnL21VZ2pSV1NzNUcyTUl3VHFUQlZOS3JCakRpSW9ubDV0UmlZMHBPUWNTTHV5TThiNHFaV2hzTTZCeHpxVmhOSllCWU5aVU40K09BTXEyMnc3RHdFaGMwMFIzWVdJbTZqYmRPSVM2c2lCNWQ3bVVFRmJycXh0N093aFExWDdNU1pQV3ZrSVlpcWhhQUlDYzFGdGFMT1pQVDA1eWpGVlZEVjBjNHJDLzNCMjJmZC9sbUNBbk5jNkZKTWFZbEJLeFlYVGpPQUJRemdFQmMwd0FTTXc1eHFyeXJGaDV6NVM5OTNQTHI3MTY3NjAzM3lDa1hDWjlQTEZ6eEt4b2hjSE4yczkvOFF2Ylo2ZVdxWEwrYXJXdXFDeTkvNXMvL2JXOU83ZituOS83OWc5KytINFMzdG5kMzkzZkY1R1VVNHh4R1BvWVJ4RkZ3MU5LWWNwWnMwaEtPZVhHVkR1bk8vZFBIczRYaTlyYnc1MEZSbEhCQXRpTlFRQlRLVEZHTGRsaW1WRTJmK2MzZjNWbVRZbGoxNjlzMDc3NnlwMW41MmRuNTJzMnhpR1AyLzRYdnZHTi8vSnYvSFVQNkVEdjNycnovZ2NmM0R5K3BWQU00OFRleXJtVWNhaXFTdVV2OExRNEdXRlRJb0k4aHV0YVQ0c1NnMnBSWlNKa25vZ3QzdGwrMEp5ekNxcnF5ZG5wbytkUGdXM1NtRXRoMVpReVRUeWpWQmpJT3lzaUlVUUFjTlkyVGQzMy9kblYrUkRDeEdrTVl3Z2hHRE5WUVJwQ3lMa3crMmJXcXVMekZ5YzdzOHI3S3FWWXBtcjUybE1LVWdxVG4rNjNxOVhWbmJzMzJaanpzN05iTjI3RVdHTEozdm5GamRucCtYa0pFUkVRQ1ZDbWFnbUJVaW94bGltcnloaVRVNWhpY2J5dkxLbEYwcHlRMVNEY09OcC8vWTFYVlRXbENmQ2ZpYTJJSUZGR0llTlVkZi80eHNPSFQ3ZWJUWm1yYlN5QkppMXp5TDkwOTNqWHlzZWIvdnNubDk5OTl2amsyWFkyWDdpbXJZM1BFcnFZbFlDdktiWnFHQkVwRjR4YXRua1kxMmt0UXp1dTI3WXBLSWQrWmdoT243OFlyNjRNTVJOSkFja1NWcHNTaFA4UC84My83bmgvcjNGK3RWbDFZOGdaeGhCRExDbm5OTVpmK2JtZi9UdS85dXNtSjVKRUJFM1REdDI2cERocmFwaWlPUkNKTUtkWWNwa1N3MHJPcWhPMHUyakpSUktBSUNxQWxCUkoxUktuRUNhaGM4NDV4ZEV5ZG1NdkdaMXhxdlFuMy8zQmR6NTRrTWx0TnVzWUlnQmFZdzJTQ0xBeHhDWU0vWmhpQklneHo5cW02NGFMaThzUXcrNXlSM0x4M3NjeGxKS05zeXJTTkEwUkEyWTJSTWFlbjEvbGxBNTNGNVo1SElOaE84WVVRZ0tncS9XbWNtaXRNYzZrbUl0cU5XOVBUNi82SWJJemx4ZGRTcm1wdlRQR1YxWGR6cHlyMm5ZZWM4cFpZaXpHbXE3dllvcGtYQitqTVVhTGlPYkttN3IyS0dWV1ZRQklVbHBEWC8zaXUyKzg5aXFVd3N6T1Y1dStNODZTSVRETXhpb3dBNjBmUDdkRm5YZDlQL2pLRzJOQVVRaXQ1UnEwQ2VQcjgrVm5iaHh6MXBQTHk3UFZkc2lqc0pSU1FNU1RxNnl2clBQR28yREpCWkdJekxSL1NTbHYxNXV6MC9OdDN6bkFPWG1qR0VQTVl3b3h4SkluU29yNW8rKzhkK3Y0Z0tROFBkOE1KYWRDNnlGcyt6NnN0ci8reTcvOGQzNzkxM0FZVTRtb0JiU29sdVZ5ZWYvKy9jTWJoNU5BalloVjFWbVhjKzY2emhBeE14YVFYRVRMTkhoVFVQYXNLaWdxb0NLU2NsWlZhd3lVZ2dJRnpNTUhMMkpPWC9uOEZ4NC9mdnp0SDM0VTFSQmNxdzBtNzVNQ09HUFpZZ0ZZZDl1dTY2TGhlcmJZZENPQk91ZWNSWWxwMmp6SEZKM3ozcnM0eWpXUklrOXNXZXk2amtXSVNFRzdiV2VkQTRDbWJjWStPT2V0blRLNWtRaHJYOFVZeDNGMDFnN0RJRktJaUprVnROdjI1K3V1ZGkwejFWWHRYQjFqempuUDU3TnhETG1JY3c0UnE3b2F4K0VsejAyN3JtTmpaMDIxbU04TmtDTWpSWEl1dVJSRW1sZ3FDRHA1Qk1JNFB2MzRrZS9IMmF4dG5OZFUraUVRc2FrcXkyYTUyTm5iV1Z3OE8xbU8vT2FYMy8zRlRmZmR4NC8vNU9UaGQ1NmRGaUhISmxDTUF4RmlLV1VjaGpBR1VBVXluMURJYzBxU3lyWnA5Y2F4Mll6TFdRc1R2Tm93TzF1eE40cm1uLzcrdjdwMzgxYlYrTXQrM1hWanlQTDA5R1M3dXZxZi9JMWYrNjIvOWtzNERLbmJEdHYxYkQ0ck9VdEt5OW1pcXR0blQ1L2RQRDV5enBXVXJoUHNVWE9PWkl5MUxMa000K2ljWWVLSklCZERNTlpLRWNsQlluU01SWEpKTXJsdVYxMzgvbnNmSmMxRitNKy85OE5ubDJ1M3N5UlYrQlNuRUJGTEtkNTVnOGdaWmsxN3N0a09ZUU1Bbm5DNTB6ckRWMWVibmVYU09PdGNTaWs1cWJ4ektVWmtEdU80dDVoeG9UaUd5dGdpS0lyV3VSRGpZakZmcmJicjlXQXNBcUt4dk8xN0ViQU1Zd3BrVE1rbERxTVNXbVlpQXNORENrQjB1ZDFjZGVzeHhXWTJONVhMdWFTQ0lXdlJNdW45RWNneXBUaEFaUWtoU1JsRGZPUHVqWGMvKzVsN2QrOEFLUm1MaEpManp1NCtWeFV3SXBsU3BQRjgrdno1ZUhvZVV3bGpyT3RxTnAvUG10a1lBeU5LemhMRjF0V2QxMTQ1RkExSmIrM3NmbUgzNEpmS1ovN2d3WWUvOTczdmZuQjExbHUyMVJ5Q3hoRGkwS1BrSXFBYXA5V0o1S3c1SStKcUhEOVliVS9sZ2JzT3V4RmlNdFo2VjNucnpFY25MMDdYbTZwMlNVby9EQ1dXcnR2K3ZiLzFtMy83RjM4NWJEYkFCb293MCtSaEg3dmUrZFI0OC9qUnc5M2xEZ0x5bFBoQ09JNVQzNGdpTWtWNFRBemxpWW1aY2phbFhQc2ZpU1NyQUtoS1RnbFVuejg3ZjNwK1ZwanYvOEVmbkt4WGFEem5qTXhTeXFmak1BMnpVUVNBdmZraUR5dHJPTVFBaUVRMnhwZ2pPZHZFbEdOS0tXVUF2THE2YWlyamZWVVFLMStwU0wvdEVIRFd0aUZFYXlwckxURlhsVCsvV0VYQm5jVXk1MjBwR1JESGtCWGw0bUlkWTBHZ1VvaVFhbDhicmxUTkdBb3hNVk5LMlJnWHM2alNHRVpWMXBmZ3hKS0xRTGxPamtkc2ZRMGUxcHRWNmNkMzNuaGpkM2VIbUgzbERWdnZIQ0dtbE91cVFiSU1JRU80ZXZCa1lTdXN1SUNxZ3JQT0VBTk5ENFhrblN0RituNTBRQTNZYkxuZXFSZWxldk1MWC8yVlY5LzZ0eC9kLzZmZis3UDMrZzNYYzg4T29FZ2lGQUZCVlNoUVJBQU1FZ0lnaFJDM1lUQ0NxcG8xQ3dnQ0tTQUM4TzM5L1pqeUdQT1ljNUFjdSs3di9kYmYvcTFmL01YUzk4NVFTbEdsb0lJeGxvakdNSUpJVmJuVDg5T21hWm1ZMkNoS0tWTitXU3FsaU1xVUxwaHpGdEhwbEZ4bk5ZaUlTSXhKQVpoSVJVck9JY2I3SDMvOHd5ZFArMUk2eVVGQkJDd2JVUmpEbUZKQ3hPbVd0bXdxWncyeTgzN01hVE1PUll0a3FSMHpTRDhNWXlpbFpEWmtpSExPUllRUUsrK3daR080Y2xXTXlWcExoRXg2dUwvWERXTVI3ZnRoak9WcU05YU5uN2YxMFBjaUZGSWhOamtMSUJhWmdyNHR2d3hQVVlDVVplaURDZ0Z5aURtTXFlUWlVZ0FBQ1JrcDUrS3NyWnczek41dzQzM3Q3TDNqNDcycWV1dTFlNHU5blhaVys2Wk5KVmROaTlZWjYwVUoyTlIxL2Z3SDl6LzYxbmRiVnlFUkViYXptYkVXQ0VNWXZiT01TSVFvUUVVellpWmdJaW9GcFJqR3ZYbnp6czJiNzl5OFRhTHI5Zlp5ZGFXSTFucDIzckdaMElHZ1lCRFpHamJzbFNwaElnUWlOcE5uOC9yTE5JWmp5UVhSSU5tWS81Zi8xZC81dFovOU9lMDdFUUVtYTdIdklvaHl6Z2JSc0NualdOVWVSRTlPVHRwMmxrcnhua3RSS1htNkpGU1ZrVVNrNnpwckxVQkZoUGtUVnJwcWlTbEhMY1lnWU13cDVDU0VROHhDS0FCR1dFU1ZVQkZLS1RrWDUyeWFiaDJGSXVxZEkxTG5uQUgxaU5aelU5dmFtaXlsSHdzVlVoVWtUaWtEb2ZOT2Nzd3h6V2Z6RkRPSTdpK1hxL1hWQkVuMmRmUGk1TnhieTF6bGZGWFZEaEJqRWpMV1Q1ZThxR0dXSUFvcWtrUFdJVVJyT2FZeURqbEZsWkp0ellSc0xaV1NjUEtBS0ZobTh0NVowL29HcEpRNG9JSWg5WmJ2M0w2RkNEbkd6VHF0WDV3ZTNUZ0NZbEVrcFp3VmtvNzk2bnQvK0NmZDVXVmxUQnFEcnlycnJLdXJPSTZXV1V1V29pckN6azdKOVZSQXBLQ1NZUXNFS2VmYW1uZVBialR3eFY5KzgzTi8vTUVIZjNqLy91Tmh1TkppdmJQa2lGTGlNUlMweUZhQWkxQlNLQmxBQUVsSlJWUkxVVlhqTFdYR0FpcGgrTi84N2QvK3RaLytacjlaazZoakt5WGlCSVZBa0p5N2ZsQlZGR0hBeFh4eHRkMzBmU2VxempmNFNYaG1LVTFkcTJnSXdSZ1dFVlZSd1ducGh3QWxseHdUQUdncUFHQXE5Nk9QUG5weHRpTDJJWlVDSUFLaWdxb3hoVktLc2Z6SkZ4R0NRa3FaRzJ1TWFWelZObTBveVZsMnpvSjJsbG1rTEJhTEhDTUFNQk16RUdvc21ZMFpReUJDdGliRVJFck91djc4YXJQZXRzZTN1bjQwaGhCcENHbTFEZk81QlFKVkZJVXdqSVlOQUlRUTV2TzVpQUtZa21FWUVpZ1RTNUZNeGszNWMxTXFMQk1hWmtRaW9seEtDaU9XaEpYdUxYWXRjeW1GRURVVlJUcmMyYTJOZmNsSEkrZHF4KzVIZi9nbjBvMjd5OTB3aHBMVHN0NTExakZ6ak5FWVdsMnRWY1UzamROaURVc0dieXNrQURTS0tFWFJUTG9rZlB2MmpkdDkrUHp4amIvMTVTOTk1K25qZi9iZWQzN3cvUFE4WlBKMUF4VkFLUUJLQ2lhQkFhdWtBZ1dtVmNDVTJRTEd0WDdzc29UNDkvL1diLzMxcjM5ajdGZElFRk5pVkVlb2tyVVVRK3lzRGJvRkFFTWNRNXpQMnN2TlZUdHJWQ0RuYUFpOU02a2ZWRFRGOUZJZGo5YWFLZkFOVlNjWFhpbEZVT013RXBLM0ZnUk96bGNocVhWK0hiWVQ1M0JLeFJSUUJhRXAzQVZVUlhNdUJjbGJXMVJiNjJmR0JTa2hseTZPWnFjMTFnRWtZdmFPQUFoSlZZcDNOVXBtTGxKVVFKVmdTQ0VYRVVzaGhMN3J3SkJyNjh2TnFxb29qajBvSVJrbEUzT2MySHJETUhydlJVR1JZc3J6aFdmanhoQnpLZDc1bUViTHRta2JVQVNBSXJHcVBLaDY0MUtJU1dJUU5RQkhPenUzamc1bWxaTlNpRUZBMGJxcThjNDdOZ1lVQVNpcnpoQk8zbi8vNHVIanZhWnh6b2NVcTZxYXRhMnZxa25tT2ZFcG1OaGJKa1RJUUtDQXFvYlJBSkd5TlVuQmlGSVNadHByNWxIUzNDMk9GMjk5NWVhTmo2NjJ2M2YvKzk5Nit2eDhPMnh5TUhVREFnelJJSUpCRldBaFZsQkNRVkpWL3Z4cmQ4b1EvdTV2L09aZi84clh5bm9GSkFhUlFVc01lUXJteUhtQ1I2dVVsSkpCQkVUci9kblphZTBxRUttOUZ5MGxaY1lKS1ZTa3ZIeStNSU5xQ0NOY2t6cFRTa2xWVVNHbTVJeXBtbWJWOStzdW5seXUrelRveTRRMjUxMHVPWVR3a3ExT2hNUkVsdGl3TVlha0ZGRXRwY1NTWWttSWFxeXBhciszdHdRc0l0SjFvWlNNYU9NNFdzT0ltQ1g2bWlmanBMTllPYi9lYmxOV0pGNWRyUnZuWjAwZDA0Qk1vRHlNTVJjdEJVb1dBRVprTFJCaW1zOFdwZVRWZW1XZGRjNzEvYkRjWGNZVWNvNmlZcTJaeldZaFJzbEZTNUVzbHVudXdmN3gzbTdsSEpaaXJUMitjYkMvWENBQU0xcnJqV0hiMU9LY2N5NmVYMzc0cDkrQlRUOXZXdC9VYk14eXVXeXF5bGpiRHdNVE9XdnF1dmJPSVJOYmc0Q2lXb29vSWpFeEcwSkNBVkxJT1ljWThXWGVpR0c3OU0zcmgwYy8vZGJudm5SODg4NXloMW5YMjhzMDlyNFlLZ0FJYkJpdFVjTm9EVmNPcmVHdnZQWDYvK3kvK1BXLy9wVXZsKzNhTXN2a3JpMUpTcGFjU2txTWxHTW9PWUdXQ1pNYVUxRFZpOHUxQ0RoRDN2a0pRWThLT1NiTnhRQnFLUVE0TlRsYVNnNEpSRXZPaUl4SW9wQnpJWFpTNEd5emZmL1I4NVBMUzFJa3dBa01OOFZscEFrdVNXU01tZElVbkhVSWFneW5NSTVqQjZoRUdITkNjMjFGTDZXSVFFNGlvdk4ycHFJaGpnREFqb3ZrdXE0QWlzVFJXUXRJMnlGdXh5aWdtMjIvczlQdUxPcTJiV011akVZRnQ5MXduZTVCSEZOT0tUT2JwbWsyMjI3YTd5TUNHa2FpbUhNZlJsRnRmZE40Ty9aOVRDR242Qkh2M1RpOGRXUC9ZRzlCZ3FWbzIxUjdPd3RyVEZWWGlPcThONVhQV3J4MUV1TEQ3L3pBYmNlWjlWcEswVkxQR2xkVlNuUjVlWVdJM2hDb2VsOFJFeWdTWE4vL3FzQ0lwWlNKWDRnd1JVckxKenc1eDB3eUpjMXJZL2lWM2YxM2pvNS8rdFUzUHJkLzQ1WDV6dWR2M2wxdE5tYzZVdHRDNWJXeVdGbFgrOW83ODNmL3hxOS83WjEzeHZVRklKU1NVMG9BNEN5QllaMzI3d1ZLS1NrbEprQkVZMDJSUE0xdCttRTRPdHdyUlVRRWtYSUtremN2eG9pSXFsSXlsQkxoSllSakFsaW5GSTB4b3JMZWJDcFh0TWpGMVNXb01wdGM4bVRJMHlrM0ZjQWFNMlg2NFhSMU1ER3hpaElCSVNJb0k4MThuYWtrMEhFY0oySGM3dTdlWXJZZ051TVFTZ21pR2xNaVJrWDB6cVlPbURDbW1FdFdGUUN3amtzcHFzWFlxcXByQmp1TU9lZkNyTVNhYzU1NmtMWnRoM0Y4T1dzbkVhbnErbXExSWtUSTRxdEtZb3FncE5wV2plVDh4cDA3OTQ1dWFFN0RaaXRLU0RTdFhtT01SRGhoN0VJS25GTEo5T0xCMDNoMjFTb2pvWlFDcUxWMW9CcFRIRU5vbVhLSzFyaSs3NmRpcnBUckNFNWlPMG5QNmJyV3dWSUtBU0RSOVU5dWpERnN3SWhxeVduSWdSUnVlblAwOXRzL2ZlL1Y5UkIyNXZYLy9WdC9jbGxaMTFSaE84aWdTd09mTzlyaC8rTi8vYitGY1VSUU5seHlScGlLQkNrNUc2U1NNeXFVWElhK1J3VG4zQ2U1bzl0dEowVm1iZFBPbW1uSE1Hejd2dTlCeFRCUFBDUkVUQ2xQdmVzMERSekdVVlZMRVdOc3prS0FGK3YxQjQrZlo2YXAyeTFGckxHR1dSRnpFU1kyMDNvQTJiQ3hrN1lERkFsRkpaWThyWEZTeVpQUnJ4UTFiQ3BmSzhCbXN4N0hYa0c4dDRCZ21RMlNkVDdtSkFBNWxXNE1TTlk1RDRoRWFKajZNYVFDSWVZeHhweHpWZFdUUW9LSXZMT2Z2QjhUaU5oYW0zUHV0NTNrWEdMeGhtcnZhK2VYODduRU9LK3FOKzY5VmtLSW9WTlZaRk9Lc0tYbGZLWWxOMDJGTUVVS3NEUHU5T01uNDhtNUI3TFdqbUVncHYzOUEyUXVLdHV1czlhbUdHTVl4aEJTbWw3VmxISTIxckF4MTA1ak50TTBTRlNtMXdTSkVORVlVZ1hRaVpDRFJBaEZFYkNnRmhKalhGMVZyeDhkdjNGOHJCQkM3dGJyampKK2RyZisrVmYzVGJlK01JcEltS1VRd0VSOHpTRmhFYTRxRUIzR3dWcGIxM1hPY1VMbU1yTmhZOGhjWEp6aDdlTmNTbE5WbTAwbm9pS2F0VERTaEl6SktTbUFpcFpjUk1RWUUzTk9NY1pVckxXNXlBUVh2TDd5cGh1U0NHVGlYMDlZV2VDWHVHcFZ1TDdtaWZVYWNTdVdXWmtUMkRIbkxGcUtHTkx0ZGxPS0FHaktvYW9xYTdpVVlvZzF5YmdOeGpWOTMrZVFWVmxVTjl1dWFlb3hEQ0VZc3U3ODRzbzM3V3huTVlSQVU4dEJJaXFsRkd0NFBwOWRYRnpFR0VzcHpOeFVWV2RZUkd4bERXTGpLcy9Hc3oyK2Q0OFF4cUhUbktyYXA1UWh4NXhsMXkrTXMza2NoMkdjemVZV21RczkrK0RoNXNYWndXeHVpTUZ3UlhYVE5HUTQ1RFRFd0V3QXNGNnZGNDEzVmVXY200SjJtcm8yempJekFsK0hiUlZGSWphc29GTjBGd0tvQ0NLcHlERDBWVk1UTTFzV1VSVkF1WDdEbThyODdPdXZmL2JHd1I5K2RQLy91dnAzNTJuNzV1M2ovVDB5VEpqR2lBakVKc2JSV1NOU3NFZ084YkxybTVjYUtpSnl6b1VwYkZmVnNLbHJqd0F4NXhpRGQ4Nnd1ZXk3elhxem1NOWlpcXJRRC8xMG1ISXVpRGliemFaOS9iYnZpZmp5OHRKWHRWL3VBcUpBVVdVRVlLSnlEWnRSVlNpbG9ERVRIR3JDRHJ6TWo0VnJEWkJpRVRGa25JbzFGclFVbFc0WWNjVGFPOUV5bmVNWUlnSVVwcGZka0ZIQVRUYzQzd0JJU2pGR0FvQk4zKzhzSzBEY3JMZk9PaW1pcE5lYkhRVWtydXNtNXp3TTQwU3R1cnE2dW4zNzltSXhYMjgydGZjYWk2WlVWYlZGckcxVk5hYmtrQUhISkNLZ0tRR1JzdzRCMnAxWlRDbUc0T2VMMHlmUDBtcXpOOSt4MWtEUm5ITXphNnBaTzNiamRydXhWZFhPWnYwdzd1M3ZhWTU4ZlZUbDA3SGZLc0xNS2tWRmVFcHRVbUJyeXJVblJTWmJMQ05LS2FCS1dhZWg3VFI0emtVbU1mVnUxZjdxdTE5NSsvYWRQL251bngzTnBYWEZjQUZiMVNLVFJsS0cyRlBXRWd0T0U2aVUyN3FPekYzZlRWQ2U2ZGlDcXJVOHh0Q053UXpza0JFcHB0U1BBekV0WnEwQ0ZKM1VIaW9pekpRa0k5SVE0aGlUYzFqTm1sS1VqZkhlR2NhU2lsRUNBWkdpekVvMDBaekx5N0N3Q1NSR2hOTk5SRXJNRnBHaUZHQlZBUXVNUlVPZVZDV0FaQWpVT0tNNVc4SVVZa1RBeHNjWUxLbUFvalg5T0hydmlUREdCS2hadUt4NlZTeTVUQUh4QUdEWVRLdE9SUFRlNTV5WHk1M05aalBWVlYyL1hTem0yKzI2cEZoYjV5elBtdXJHM2hJUlVZdW9ER092WUFxQlFXTXROczZUbHJadWwvUGxvbXEyWjFjNHhsbmJ6bWR6ekJKamROYll5bmQ5ZjM1eFhrcHVtYzVPVDJmenVhOHI1cGF2azY4QUFZWXdGaFZtSnJUZUFSSmFhM0hLNFpJQ29rZ0lxbHBVb1NnVVoxaWtxQlNZTmh1NUtCR3pFazVoR3FCU2lQMDdoemRlKytZM1AzNzI0Y1gyblAvclgvMEZoVUtvaUNvaUpBQkZRR0VjaGsvN0xjZHhURG5WZFQyTlBrdk9vckJhYit1bXJyeWJ0L01VMHpEMHBaUlNwSExOT0l5bGFNbGFwS1FVcDdzeHBSUlRtcTZUZHRiV3JvSlVGUEdqRnlkOUt0ZjgyaWwveVZrUkthRFQyek5kN3dnSUlwWW5pYUtJRmdFTk9XMjZMVE5YM3NkaG5Kb3RVWWhaa05CWjFqd2Q4eHl6Z05Jd0JFQmpyWmRTVktIa0RBZ2lxb0tvS0NMakdKaTViWnRTUkZTdHRjNWR6NkFRcjdYc1ZWWGxuSGQzZHcxQ2libXl4aHM2MnQvZm5iVUdvV205c2JqZDlpSGthYmcrcHB3WldPV3RXM2R1N2UvZE9UeWNtMnA3Y1RYMjQvNXlkMmU1VTNLUlhLd3hkVjJIRUZhcmxmZCtkM2MzRHVIaytZc1NreUZpSkpqMklZaDVDaEVIWmVacmVoelROWUJGWktyMnBsVzI2TFVHUGFma3lKU1lTSzhEY0ppSWtQU1Q4QzhBWnFNaXhGVFBsekd4cVp3cklpbm1hY1pTVkJReHhSQnpxcnd2cFpoSit5bmFqLzBVYmhoajdMYmJaamF2cW9vUXRaU2NocWs0Y040NVk5bWdxQ2hxS0VFRmtHMEJETGtRWW1Yc2lEaU9ZeGpHMmxXK3FsWFpHMk00QVdySmdxUUlTcVNzaUZOZklEcDFOMU5uSVpKcld3UEFHRVlBbXRCbkFPVFFMdHJHbW5IVmpVR2tsQndET29aNTdjUFFDeUFTcTZvSzlOMEFDb2FKdk1sU1FzaUVIRktPcFZRMUVsRUljYlB1akxFcHg1eWxhU29pbXZnRjA0dCtmSHc4bTgyMjIrM3Vjckc3bUhzeVl6OFlRZ1BDek92MW1xek5JdjBRbENoQUthVklCR3pzamIzbHplVitXdmRkTjB4NUxvZ1krcEJ6bWRTTm0zN29OcHVxcnB1bW50SmxsenRMWTR5eGRnSUJ0bTA3dFFVeFJrSUNVYlFnV3JCb0Vaa1MvQUFBSkUrL0pDSXBvTmNxaGFKYWlrS1JLWmhKRVlUSklpSXlGd0F0YWRMaE9PTmV1ZnVHU1NrYmEyS0svVEFnS0txSUtCZ21aMFdVR0laaFlHYnZYY2hoOGx0T2hmbzRqZ0JxckRYTXd6Z1Eyc21VT1k0akl4SGhWSVRHbUEwYlk3eXFocGdjYzEzWFZWVXhnRGVPQ0ExWUZTRkVnV3Y4R1RQbG5BbU5NV1pxeGlZQUhoRk81Nk1VbVR6c2t5alZzeVVnek5KWTd3amFxaHB5Mlk1REJpa2hrYmN6WDRlc2ZZck1abWZoVjVkWHFSOXRaWnd6UmsyTUpTZlZ6RVZ5eWNMTXZyWmp6cGhMSEdQS2lSbG5zMW1NYVhxNkZTa25wNmR0MjFwcmM0Z1dxUFhWb21wV3ExVXFta1ZpakVGNklDTGtPQVFRTk1ZNDl1T20vK2o5RDN6WHh4UU9kdy9hZG1aTkZXTXBPYlJ0YTR3NU96dkxPVGRWUlVTYnpUYkdPUFI5NWF1cXJweHpxbXFzWmVaUG5uR1RtdFBpZGQ4MGJUZlpYbmRWT2VmckpJbFNwalppRENNQml0TEVCMU1WMHFtbndmS3lucnVPTFJBVkJDTkppaFFvQXJuRWxITE9UZHZNMnRsMnN5MHF4alpER0txcU5zN1JRSDNmTTNFLzlLUlkxN1BOdHQvWlNkSGJrZ3VUQXVnWUFxajJZUVNBZmhnbW55NFJUYWl5NllTQ2duZU9tUzJ5OSs3eTZpS1VwTmVjVENKU1FTaWxBQk9BWE84NFFZc3FFWWxxbHBKekJqQ0d5Q0pVeEFKRmNsRkxwU0FJTHBycWhuZG42NnROTnlha2NjemVXMktraEp2TmRybmNtYzNuT2VlU2t6VithcFNqbHFLS2hNWnhYZGRadE85N0JEQ1dGV1N6MlloTUEyV2ROVFdKSUZMWGQxS0tJTDRRT1VjeVRMUFpmTlYzMiszRyt6cW5aTWhVVlYwYkQ0TE9PazBGTXhBUUdIdnYrR2JGTnFhNFhhKzk5NVh6TVlUblQ1ODJiWHZ6NkVoVlQwOVBKNWxqWGRYR21PbEFHR05LS1NHRVQ3YW0zdnZwVWs4aFRuUlhWZFdVbUdqNlk1ODhCNmQ5K0RSUnhWS21jUWdnZ21qSkNSQktVV0tlUExjQXdJd0F4VlRPeHhBSjBMR1JVb0pxR0VObC9heHBWK3ZMcnUvbWkwVUl5VG5EekNHRWZ1aVpPSWNrb2pIbDg3TnoxWFQ3K0thS2pDSGtuRU1JZ0VnOFJRT3FaUXNBWVF4SXdNekFDS2dJUU16R09hNnE4NDh2aDNFQThEckZuMCswUThSUzBpUmtMNUtRZVNxMWNITDZpaUtRZ2hoRVJuVE9wWlN5Q2dvWnRpQnFWQ3JBUklZVnR6RU9nRlZWdFkzWmJ0YmQxZFY4TVRmT3FFaGxXSTN4dmdxaGM0NUVaRklScUtobk83M2N4bkFwNWVweTdXdWVMeFpJNEpBWmlZaVZLS2M0Yk5aTjFZdzVTeWs1Smt5RlBkU3VtdGZ0ZkxiSU9RL2pRQ2d4bDlyWlYrNjljdWYyVGNmY2JiY3hSdTlkTi9SUG56NHBwZXp1N2k1M2RuSktNU1ZtTnNZQVFOTTAwNmYvR3JWanpLZnQwY3hUNnIwYWEyTk9NSTBaYzA0QWsyanRrNzVtcXZOZVlxeFJSRFFsTkJhMFFNbk1ETWdxVWtTbjRvT1VWSXNaaG42NnI2eXBobkVFa2MybVU5SEt1N3F1RWNDU0NScWZQWDlSMTlVRURLMmF4aGtYVXJDTzY5bzc1NFpoeUNtTklSaGpobUVZUTJpYUdoR2ROUWpJVENGRUxXcU04V1lLSGtBRUpRQlgrYXROcDJCcENoV0ZLUjBTU2s3SVRDcE0rcEpOTW1WcHF4WUF2Z2JaVEEyMjVrd2lRSk9XS2VjaVhUOVVyaUowZllxYjFaaERZY3F6MnUwMmRWMVZ1V1FCemFpaWlkUlV6a2tyb2hQRUY3Q0lGbkhHS2xISXFaU0NDSzQyeEpSVExFeUZERXFwQ1didFRFck9ZNmlyV2hSVlpGWTVxR2VpWUloWU1RN0RCSEpKT1JPWnhieWQrenAwUTVkalBXdGJYejE5OXZUWnM2ZjdPOHRiTjIvdTdlMU5LYkloaFBWNmpZaHQyMllwODhYY0dET2RXMlpEekV3a0lqRkdrWHhkVllocUtZREl6TlBqQllsaWlJRGdyRlZSSnBxTUFWTTBFUk9KQ3Bhc0tvWVpWQ2Y2QWhKTmU4NlNWWm5NMlBlYm9kdmRQOXliNy9BT0RDK2VibGJyTVlSWjVZaHczcmFzc05QT243OTRjWEcxdW4xOG8vWitFL3FkZGxGU2JPZlZ6bktXVW9vY2M4N0RNSVFRUkRXV1ZFSGROczA0anFXVVlleERHS2Y3cXZGMVhkWHN5RlhPSW9Ib2k0dTFvSU9TbVZHVkdNRWdSaVJGSUFETE5tWWxWa0FWTGF3ZzVUcUJabXBxR2NBVE1YTUJMYVVBU3hFb1VoYXUybStyN2ZNWFRCeFR3VXBWMUpCaFZXT2NNc2FNWTRxWUF3TzJqUXNoTVpseERDS3BkbFhKV1JXZFlUQWN3bWlackRGR0lmZURxNnE2cWduVklsYlZUTWhMVWtFZ01vQUVoa3ZLVER6R3NRU1pzQXNBR0dOY05EY2s1V0N4YWV2SGp4OC9lM1pXVmY3MjhhM2RuVVhUTk5lNVVpSTVwZWx6djFnc2tMQ0lhTTdXV2lSTXFVQVd3NlNxS1Uydm1BSkF6bWthTHpOaHlVa1ZESEhKbVlqWVVZZ0JqRUhVNlhjSVlicHZwcnhwQTFCeXlnS0VwRHhsNHdFaUk1T1p6ZG9oaHBNWEx5Q1hXVlBYZFUyMHppbGxRNVl3allGOWszTnVmWDEyY1ZsS2JwcmRMZzZiemNZNEp3S2dtRkxLeHZaOUgyTElwZlI5Mzh6YWtvdTFaSzJkSm1DQVpKaVd5eDFtTlE3YXhkejVpa0R1UDM1OHRWM2p5eUVHOHpYaWV5cENtU2dEdU4zOXZ1c2dEWVlSRUFwTndrU2FpdUtTQ3hrMmJIS09pQVFpZ0lxQU1RU0xWRnRmbTVRVVFvd0Vzcit6Z0pJMzI2MGd0SFhya0pLVW9rVUZQYkgzM2hLVWtwdTZHWWN3eHJHa1lvenhyZ2JWeHJuYWVzZGtpQ3d4VmdhemhKSWhYd01hQVhHNldSRXd4bGhFa0lseEtxN1JHVmZYZFFMOTNvOSt0TzFXYlRNN09yNWxrTTdQencxaFZWVmpDQ0dFYVpNMmE5dWRuU1VibnNiS09XY0ZRS1RackJtR1lWcW9PV2RER0QrUjJLbVdhUXJsbklzeHhwU21talRFcU5PMGVqb3J6RlBVK2JUQVV1WnlYYmRTU29tQlZiV0lzTE1wQ2YvdmYvdFhKY25sMWJtaU5tMHR1WFNiN3ZMOHdocW5DSlZ6enBtaytXclRuMTljT1dOMjJyWnBtcEp6S21VN2pHMWRNVE1xOUgyL0hycFFFbHR1NnJxcDZrOVkzR0dNQWxnMWRlUGNvbG1Bd1JpeVkyY3RmZS85SHoxK2RsSFVGQkZpVkZTazZ5VzlGRUdWWkdadi91eC9PVmg3dWI0eU9RaVRBV3lzTmNha0ZLYzZpMkRLZzRCOFRlOEdRSlFpcXNWWWwzTXFXZ1RJc3ZQT043UFpPTVF3eGdLQXlONGI3eGh5OGN5TzJTTlpKRytNTSt5ZEFWQkQxZ0xOWEdWVXVZZ2pVc2xTQ2lnVTBSQW5KUnRsMVRHbmxGUEpKWW9tVVZBdzFxbENXODhNMndwZFN1blorVWsxbTkyOSs4citjbjk5dVNxU2J4N2R1TEczUDBGaVZYVVlocHd5TTF0anBqa0VBaGhqaWlvYmxpek0vQW1PSjZVNEZSWTU1OG1oTTQwb3AyblRSTVdmdnE2N2dXbjVVb3FLRW5GS3FlUk1Vd2xTQ29GT0Nuc0FJR1pKMmVTQ1RCYkI5RU80V3ExYjc1dW1FWUt6cTh0NTZ4ZE5vNnBUL09MMExhZnZWSG0vWGEySUtPZHNyUzB4WFV2dnJWa3NGbXlNaWpoclk0d0lvTmZOcDRrcGpTVldpSkxMQmlXWStmUDFkdHZIZ3JZUTlqRmFnWXBaalNZQ25mTFZmWFUxaHBNK3RIZnVsYWNmU2h6YzlIOUdOTWJtbk0xTGpXcFZWVGtNT1djcG9pcWVXRUdaeURublN0SUNJQnBUTkpHODl6R2xrSk15NlNqenRpVkxVcEttYklpOHJZQjAyazNWMXF0eWlDbUdpRmpJMkhFWUFXWGFkSXJJS0lwRUVOSzBlclJzcHByUGU1OWlUQ2s1NzRjVVUwd1ZWY2U3aDBjSFM0M2orKy9mWDFUMWEzZGZ1WFY4dEtoOWlpSEY2Q3BmVURrR0JEU1ZuMm9MTmlhblpKMmJQRGhoSENjdlJZcXhxcnlxRHYxZ25aWHJENFZPYnhNaUF0QzB1WjN1a3VrZGxKZVREMVV0TVdhUWlVMHdxVXFaU0JGalRrUThrVTVNSEVMSzBvOWoyTWJGYkFHT0Z6czc3WHArZVhtWmtrdFJqUEVLd0V3eGhaU3pGbEhKZ3FCbDhwbmlack1oUkNBQ1FnWDFiQzJTczFaRUZLQk1XSFBVeWpGU2dxcHZEdmNYdCs2MHQyN1J2UDNOZDE1OTQ4OSs5SHUvODN2UG5qeTZkL1BnTTdkZjJaL1B1T0x6dnYrRGIzM3Y2ZG1GYmZZZlBYNUkzbkpWbmEyM3UwYXJ1aEVGSm9vdkYrN1R4NFdJdkhWanVyNkJCYUNxR2lhVGNzNWFVamVJU0E0bFFqREdWTmJuT0JTVnhyZVl5WUdUS1E0SnBHQnFuTThwU2xISFJrVjlVNDNEU0VVMUoyRGpuSitVRTlaYUF5UWlnQ1NsV0dmSldBUWdRRW1SRkl6enhyaCs2SXZxSm5YM0h6NTQ4RERPdlQxc2R6NzN5dXMzYng1NnBuN291cTRiVXl5ZzA4ZDlQcHZOcXNaUDYwWlZZMHpmOTVqTTFNY1Z5UXBpSzVzbEF3SXlDa3lGSk9TVVFnaHNHQlNtSU9ZcE5QUGFDVkN1ZDU5RVJxUk1LeW9GU0RsT1VXdzVKV0pHQkdGRlJFSTB6bG9DbzZyUG56ODcyaitZMTQweFBKdk5MaTh2eDVBM2ZiOGN3M3l4VUZCVmlTSG1uTWNVUkNURmxHTHErdzRBcDdGdDYyc2ltbGUxc1FZQWtManJWbGZib2FtcXltUEc0ZWFieDY5LzZUTzd0MTdYZW5aNThpaXVIKzN2MERkLzRYTmZlZWYySC8zejM3M1plbWQ1c2J1TGhNN2YrdHpiYi95ajMvbmRIejdmbkQzLzRPVHE5TjB2ZnJuMWpkZFJYem9jUzU3R3VlaWN5emtqQURNUmtlWUNpTWpZOTBOYk5iWDNTWExqSmphNWxKUU5tNlp1QUdBYmhrNkdDTkVpdG5WdExDbm1JaVVNT2NVb2lnSmlERmZlemFzNUk4Y1F3emlxYXVVcm1LbzU0MVFVQUF1Vmw2RzNnSWhxV0lXUXVCLzZtTkoydTEwdVdoSTZXTTQvLzhZYnQzWnZITzRzVVhTSTNUaU9LbXFzbFpScTUzUE9qdGl6S1NFV1F1YzlJbnJtcktLcXhocFF6YUlxSmVXRVJGcktPSTVGeEJvelpTR2tuRUdWQU1keG5GVDdPYWRTWkxyalk0d3g1a25HaVVqTXJDSUFGUE1rVWFpODh6RWxVYTJxaXYrYlgvbkZkamJiZHR1THF5dG1zMmhiUlBCVnRkNXVZczdHR3UrOE5UeUdjSHB4b2FLNzh6a2hkZU9RY25SVlZmbWFpWE1LenRxbWFSQ1FpSW1OTWNRRU9XVWhTaVh0Mzl6OTRsLzcybHMvODFQMXJWZWlhZm9obkh6NC92cmhCODhlM0c4c25Ueit5RzAzanF2RDE5L1l2ZlBxdGk4aEZ5ZjV0ZU9qek9iQjJjVzYyOTQrT05UVnlxTXdreU9lSkxBaTA2ZU5FYWxjVDRnaDVWU2tBQ2dUa2lJYlN6UzFjTWhrRUpBTitjb3hjODR5UFlSeUtYb2RPNGVxeUV6R1dHTU1ndVNVU293cGhCaGlVU0JqZ1FpSVhGVWhFVnlYdEtxSXlLeWlnR2lzbTZxUDliWVRnQ0xGc3JtNVdMNzd5cjB2dlA3Nkt6ZU9qL2VPREtHV1VpU0hHRVZWUkdNSUJuRTVuOWZPRzJMcnJIRnVPdTQ1cDV5U0ZJa2hwSmdJS1plY1V5cTVBS2cxbGhEWm1KeXppQ0JBQ0tFVVVZV1VzcldPMll6anFLbzVsNGxza0hKT0tVK2NjMVdkVXZkUVFVVHhXdEdESUdvdUx5K2RjOHY1akt3NTIyenVpalRHNTNFNFBqeTQvOUdEWVJoVFNxbGtMUUtBZlF3QU9QUmpRZXlHd2RVd2F4Zm5aMmNxaVkyeDFyWE9hWkdtOXFVa0VySFdOQ0o3YjczeU03LzU4MUxEK2VaS1RzL1g2eXQxOXVEMU8rSE9qZDF0Zi8vZi9NblQ5OTZia3p0TDYxVFhEeDgrZisrNzN6MjRkZEJkcnF6Q1YxNzV6UE9OdVBsUzF4ZVFlcXc5d2JRWW9LTFQ5TldBWU00WlNBMlJKU0lDVUZMRUFoQlRZVlkyaGd4UkFWQldVQ21RUzJFeTNubksrVnJmV21MTVlhSTZGVVppWkNReXBuWU9sVW9wSWpta3JDVEdNQ0NPWFRmVjI4NDZtZGdrTWkwQWdIS1dVZ0NCalVIaUFsQTV0M3V3LytydFd6ZVg4NnFxVlNhblR4bUdRUkIzZG5mR0VOaVlITWNKMDBEV0ZoQkFrRkltK0xRaGR0WVZLVGxuUXl5bFdHT3R0U21sbkRQQ3RQYVFhWWlPaUNua3FlRWZ4MUN5eEppdSszOUVNSk5UQkJFRU5DTXI2TVF0RnU5OUNwR1lWYVZvTmlsbFVQQlZSWURkT0hRNUhQQThEOEd6YmVvNmhEQ000MDEvSThXNFhxL2IyYXlVNHB5OTJtNlNvTVNVWWtDbWZodmJlZzZLdzlEdnpGdUxoZEdkWHAyZlhaMjgrYVUzdi9wTFg3cThlclQ2NlBUODhYT3N6QmhHdHY3eVliMS9jTE03N3grOTkySHU4MFhjYW9vbmwrZEtyQ0JQUHJvdll2b3dIQS81czRmMzNuLzhhSFYydHRkVWs4NTB5dUlvcVloTTQza21Jb0hyYXNzN244WnhBajRyUUJGQnhjcFZLWVdTRlJCeUJwUEJFRFRXSnpJcEpXTXdsb1NBWkV5VW5Bc1NJU015SWFJYVVrUWt0bzNscklwRXhwaWNVc3BwR3JxZ1h1dVZEUE5Mblp0QlFoRlVwQWtldXp1Yjc3U3puTE9vZGtNbkpZM2p1RjZ2c3VUTHpVcEFENWJMdmVVdUtDaGgwa0pFV1FSRkdZa05wNWk2MUUwTlBCSk1jOFdwakpoRWQwWEZHQk5DbUx5SkttcU1aV1BZbURHR0dPSWs1Q09pYWZna1JWWFVNRnR2cnFlaVJKT1dSa1F6Sk8rOHViaFlIeDBjN3U3czNMNTU4enMvZkgrNzJlcnVIaUdlWFp6UHF1cjVxcnZjYmpkZHQxd3V4eGc1aGlpbGRtMGZWNXR0dnp1ZjlkdCtQZllUaU1OWjM0MTlUREVpQVNnNmVlVXpkKys5ZS92aTh1SFRqejhpdzh1ZG5aUHp5OU9uTDN4bHprOVBYN3Q1KytyMGFoaTJxM1cvdXJ4aXg4dEZzNy9jcjl0RnllVnExWTByN01MR2E1YzJtOVo0aXhhQkxIdGhFS2FDa2lRejI0SlVTRVdFaWpJYnk0NHBGY2tLck15aTRKUU1jRzFzSnN5YXI4dDJKS01JUk94TlNoblJpQWdBV2JZNkNTVlZwVXlENTZtR0lSSlJSQkdWa2tXVTBBSkpDR25hZERQejlFOGJZMFFCbFJXaHFEQVJwTGhvNm9QZHBTZTUzSGJBSm1ycFVxREt6cmtSRlJDdDBaZ0N2cTVTeWFETWxod3htZXUxeU5TUmxaS25xZWdFS1dTMk9lZVhSaktUWXdURmZod25hV25CNHBvR2lOYmRWVXJKT1JjbGVPOGxseFFqaUJxVHE2cWFvREVnMlZvRElNYVlFS09BTWpILzFJM2R3K1Z5T1p2VmRmdmcwZVBOWm5YbjhBWUFQSG54VEJXYXBqMjl2SWhwdkhQN3p1bkZaWWpoK09oR3ltV1R5dm5GcW0xcXlYblZiVFBJckdrRnFDZ00vU2lTMGFVMzNyMzNwVzkrdmg5UFAvNzR3OEsyWGh4MFkzNys1SEczMmF5MzI3djNYbVdGTW9TVEZ4Y3ZMcSt3OFc5ODdzMjdONCtacEJ1N3Z0K0VrTElZWU1ua1I3ZGpYQTBJV1NFWFNTbHZ1cjZJQXFJU0swSVJ5VnFtV1pvaUZpZ2lCUlVRcHJrSlRwb1dZbEM2emgwMFNFeU1URERSSUJBUmdKRVlrS2JXQzZhL3lnZzZmWTdMZFpRaWZQSnVYZHN2QUZDUnBuSllkZkxwVDVmV0ZFWmZHZlBaTjk1NDllZ0lKSThwblo5ZmJydnRjbmRwbUN2bksrdU85ZzZZcVozUDlnOFBiRjBEWWlvWkRhZVlDUEY2aHdLQStES3ZUMFZFWTR6VHp4Qmp6Q214NFZ5S1RGQnpZdSs5OTM2ejJVeDJrT2tmR2NjeGxwUksxcWtpTlpSanVpYmlFNldVcm1VSkFLcHFjb0g3ang3ZnVuTjdmekUvT3RqOXpucy91UC9nd1R1dnY1bEVWZEliaDhmUFhqei80KzkrOStqZytPYU5nMjU5SlFEOU1EdzVQZG4yUGNwdXdyTGFkRTNiRGlra0xRcUZURDU0WS9mZXZiMTZoeDg5K3U2THMxTXhkYnR6Yzc2WVB6MzU3bGpDTnFTam5ZTzVxVFpYRjJjbm0zN29YV1Z2dkg3cjZ6LzMxYkk5MzF5ZW1qTzlQSTBYM2ZubFNnQkN4ZlZQL2Z4djVFeGoxME5PL1hheldxOHV6bDZzTDg2NjFZb3hXelBOZDBRUnlSb2laaUREWEtRa0ZRSWh4ZHA0RlIxTHNzVE1WR0NTN2dzS1R0SjJZMndHbkZDa0tnb0NvaUphaUpqSkFJQkFBVlVtbmpZOTlPTUVBRUZWVmNLSm0wdldtQ252U0FFVzdjeHEyYXhYZmV6ejBMZE5ZNWo3WWFpTVZXWUM5SVlWcDhtYVBEODd6VG5QWjNOUmpmMlF4MUFaNjd5WG1FS010cktmT0ljQklNWThYU3ZNTnVjU3hsQktnU0wvMzZyTzQ4ZVM2N3JENTl4VVZTOTJ6dFBUUGQzRDZlR1FIcEdpSUVHQ0pSR1ViQkdDTFVBTEx3eG80Zi9QZ0ZmZWUyTVlFcXhBbXFJWWhoek9kSDc1VmI3eGVIRWZIVmFGdDZyTnF4dSs4d3NRaUN2T09hL0xVdXVHa0dKOWFOejFxcm9CQUVUbmhYY2hkSk0wK0dDc1ExakZHZ1FnYnowNEx3NE9EdlBsN0g0eTNoMnU3Mnh0TWNtL2VQM3krUENJTVRhdjhqYllzL1BIWC96YjVSLy84dW41dzRjeXpWcm5XbXZ2cHVPTi9yQXhMUU1HSkpwR1YxVTl6THFiUi8zSDd4N3NiSGVhZGptZjM3MThjVE04dkRnL2Z6b2ZUVzZ2cnU5dWJ3RDRzNHMzdWlqbTQrbmQxZDE0TWdWeWcxN25lT2NRdWFoY20zU3pudmJrS1RBbWV2Vm90bEQ5UGUxNVRYNXRaMEFPMHIyakF5WFFXOU9XeFdJNW40ektZbEhYZFZzVXJ0V2xibzF1dGJiR2FJYU1NZktNT0VQeVhncnVHSkR6bkNFeWNFUkFuZ01uanA2SUkzSWhBb1VvemdVR0Fqa0FpeFlzakxVL0VSc3dGbGJ0SkN1YloveTR2KzNDQVVRZUFrWHhXMVFKV2FQTE1wK01KNTFNWHIyNjM5N2M2SFc3YmR0S0laUlNnaUV4VEdXcXRjNnJNc0t1QUtDTjZYYzZUQXBnbVBXNjBpVmNNRVNzNnpxYU1EZ1hUZE5JbWNUVlJJakV1allFeXhubm5MZHRDeTRnY0dOYnpoZ0JHV2RiM2JaV0N5a0ZFN1hWYUkzM0xoVktDcFFJQVlLMUxtRkpRR0tJNHVUbytPUFo1TlhMVjRNbnlmWnd1TEcyL3VyNjV0WFZyUkNxcUJ2TllIdDNiMi8zd1VkZmZJVW9zazVYTUlISWlxb2FaTDBzNjQ2bms2cHU5ZzkyV01yTzN6bDk5d2NuaThWZnBwTmJwanJYaytyNHpmZUdPMmZsY25GL2ZmbjY5YXZsTkVlVzVqalBXejBiTDBhamFVQTZmZlBaMnovNTZlSHo5eFJLWDAzSzVlenU4amIvOHM5SzN4NUlubVdEN09MNXdaT0x2WVArOWtibm96OSsvUHVQSjQ3V09CSkwwclhEM25CL2p5RUlaR1MxZDY1dDZxTEk1N1BKYUhRL0dvM2FxcXhiYlp6TnZWTW92TE1Fd0lSa0ZGTVJ5VUVnaGhnZ1BoRzVEejZPbnVMU0VLS0pPa1N0UHdQQU9MdUZsYnd1bXBtQk1jNDVqejQ4WkJDSXJOWWNHWElPUklLb2JuU2xkZVAwN29QRE5pL2JhaFpDaUhtS3JRK2RmaytieGhyYjZYYkplOEVsazN4amJXMjFRamdYbkZFcUlVQnJySE5lQ0JtSnA1UVNBSlNTR0dMUEVnb3VoSkxhV0cwTkF0ZkdDQ2tUSlZXU0xQUGNobUFDaFFBV3ZEVXVTVlRSNnFCWWhyd3ZrMGEzcmJHdDkwcEtEeVIyK3AxQnQzYy9udTd2ekkvMjlwK2NuSC94K3ZxakZ5K2VuSjBNTy8xV20xNmFIaDgvK1BkUFBncWZmLzdXMlNrU2xGVnRyRXVrd2tBdEdFTnRieUEvK05rNzIwZnBpeTkvcTVnYmwwYjFzdE8zZmhoQVhsMS9PYnU5bkkzbVY5ZTM0OG5rNHZRczFINXl1L2o2NnZMdzhZT2ZmUERqeDAvTzFIQVFwUEZHbzZUMWc4MkRzOE0zM2ptZlRNem84Njh2TDE4ZHZiWC85R0xBMExXbStONjdoM251N21hS0NXOTBXYmNtVUdESVVpNDRNbFJKbGlUWjJ2cnU4Y01MSUcxTmF4dGROYzFpWWVxbUtjdnBaRFJmTFBPNkJ1M0lhTTRKR1RMR0pCY1M0L0NNSVlzbmhwZ2c4bTJzUENKUWJMdmhBT1M5ajBQd21DaU5LODB2Q3FsQ0NJVEFBWUJRY2dIUllzUllVVFczMDNHL2t3RXdRZFJWS3U3cnpqbjBZYm5Na3l4clc4MFlEOWFsS1hWa2gzeGdnaE1pNTF4eFpZenhBRklvem4wazQ1Rjd4dEkrS2ZuS3lRS2l0cnBwZFdEb3ZXWWNsWktNY1dzc0E5VEdlR0RlZWUrY2xMSnVEUWZFMEhheklRSVRYRFhOa2lucFhVaTRGRDFKSnljUC8vRHhuei81N011czJ6dlozMzk2ZXZyWjExLzM3dExkemZYRlpGcHY3UjdzYnNwTzh2Vml1ajVkZTNEUXR0N2xWUmtDTFlycTh2cm02SFQzL1o5L1ozMVl2L3o0ZDZVVCsrZlBPcG5jUGppZDUxTmRUaWF2WDg2bSthS3hqNTYvczM1L3M4bHhkam05dkxtNWVPL3hoNzk2SDAweCt1YTNIR1ZudU1ORXhvQTd3VndtNitWMG1LV2IzOXQ3OUh5L0tOM281UjhNeU0zOUN5Rm9jMDI5ZUYwR01GbkNXY3lzWTBpQkxBVmtqQng1SCtMM1RNaXlUcitYRGNYdW9lSVNPWGp3VFYzWHkyVzV6R2ZqY1ZFdWlzV2liYlRSVGRuVXhsZ095QmpqeUJpeTFWOEZHZWNNQVRBV2RVYk5NMk93cWphSzZpUVdNK09pbVFYWXFqc3BVT0JNQkNLbDVQblp5Y25lRmllaVFGdnI2NG5rSVpCekxrMFM4bEhnVEVDZHpmVU5ad3puSEFVTElkaldxVVFGSHpoalNpcnZYQWhlQ0I1Q1pCaXRpRUVtYlJzRTAwRTdETVlGWW94UUJvWk9tK0FzQmtqVGxDRURCTTY1TjdyVkZnQ3FxcFpTS0M1U29heHpOaUpVYTRNejNhempnQW5nMkUrVHpiWGg3ZDMxemVUKy9NSHhrOFA5cSt2TDEzZjNHK3RyUGFsR2svSDJ6dDVPZitQbDZQTlpVeStMd2dJaUNrZmhaakU1ZkxqOWo3LzUrZHBBdi96cUt4Y1lUd1pGcmM3Zi9WRnJuWm1NbHN2WnN0VGFzci8rOEZlUG5sMWMvOWVmZnZmUC81S1h4ZnNmdnYvZEg3eHhmLzNwNHU3ZTFFNHcyZXZlZHpmNkVWcVVkZFhXU3dwT0R0WUd1OGVEblRNejJOL2J1bEM5THRqUnNETkJEdGV2YmpZMjFyWTJOK0xWQWhtd0VCQ1FHREdrMkE4QkFPZ3hCUElBalhjSUhwRVNtV1E3dSt2Yk93L096eEVSQXhsdHJORzZiWnE2YnVwU2E5MVc5V0kybjg5bmJWTzExcEV4TEFCRXdvR01JeVpLcllyQUdUcnk0SDNDZUpJcTNXcnJ2QkJDU2ltNWRNNUY1V21haVVHbXRydTlYcWRydkdjSUlUZ2xsUkNDTVZiVmpiZldoeUNFS1BOY2NxR2J0alBzeGNGaG5JMVpiUkRSaFFCRWtZUktxWlJLeVRwQzZIUTZ0VzVWSi9HdERwb2FHMUJseUd5ejlBbGJTUXpUTk1VRzUwVU9QbklaUXNhdEM5NmFmcGRaQ0NpNERjNDRZN3puUWlnaGhmTmhvNWZzcm5YdXgrSnVNbnQwZUxpL2Y3RFdHOXd0ODBXKzNEMCtxWW95Rll0VUpVYjdSSFdxU2srTGVwaXROM1YrL3RiMjMvN3loK2h1Yis3SzlhTTN2TFhUcGQ1NStJWUZXWlV6Wi8xZlhsdy91dmlyRDc3enZMVzJ5V2RXMTJOZGZmL0hiejk5ZHZqeTB6L05KK09tTmJZMFJsdWxWSGVTU1NWMXJYVlRvMFJMTkNqYVpsbmFLai81L29lcVA2aWFaVDM5cHBqZURJZDdwNmVuMXJSRXhBQ0pQQkd5NkliNy96WHVBQ0RVLzBtZEN6SDhmVFdGaWpOeEtiaEsrcjJORFNHRTRISEZRR2V0MW0zc2I4aG55MksrcUpaNVZWUjFVN2ROVTFucm16WVFnYmRNc0k2VTFwalY2emdIb2hoWUpUakhoR21qblhYT08wQms1RjFUcHAyTzhjRzVKdEpyS2FVVXdoakRPVS9TRkJDVmt0WkY4QUJSVEJxVkl2R0tGTThaZ1lnaEowYU5icVNVUkw2cGZka0U0aGtnVGZPcDExV3YwMCtWbEVqT3VvWWF6cm1VMHBjbUJLK05pUTFsaUt6STgzNTNNM2FWYTYxbG1saHJJUU14bmt3UGQvYmVlUFJ3Vk9TdmJ1NWZYbDI5K2VUeHMwZG4xNy85ejlmaitkWndhM05qNkpwcWR6Qk11V2pyQ2lXZjFjV2luanovN3RNUC91YmQrZmlGcjZkQmRSbld0emMzeDIrK2svUzZ4ZXorNnZwMXQ3ZjF5MS8vVTZmTEJacW15U2ZYTTJlWGYvOFBmeWZkN0xQUGZyOGNsK1c4cVZ2VDFzWnBTSHM0YjN4VDF5NDRJVGdnTU81dHBVM2Y2cVlSdy9XVEgreURzL1h0ZFRGZXRHYU5jODdTRkpBRlFBb0VBQUVaSWdvTUVNalRpbVJqekxkZnRhTWpJaU5DaHNpNDRCeENDQjZBY1VGSVFadmdmR0Q0YlVNdlNwSElZZFliaEwzOUJ3aUlQbmpydExHZVNEZU5yYXJaZkQ2ZGp1ZnpoVzVLWFpiR2h1QXNCa3FWRkNJSXBSQzVZQ2dTRnRxbUtBdVpxc2FZU2hzUG1LYUpNU1lXY1RCQUNzUVQ1WW1NMFNCWUo4dWlWY2Q1THppUFJrQUVqTGdpVXE5QUpDU1NBRVhDT2F1NHJMV2w5ZTBwaXRaVTQ4dkZGdWZkTk9HRXdkbWtsM0xHdGJNRWtwQTdiMlNhV3V1WVVONDRsWFlJQlRLbGpTYXV0QVBPUmRNNjhkVTNsOWFFcmEzTmkwZG5GSEF5WFM2bStjSDJEbGR5VXVUVDVYSTQ3QStVV2w4YnBtbGl0RTZWcEZBZlB1ais0aGZmNzNlNGJRYUx5amF6NnNXclR3NVB2cE50SEl6R0kxTzU0WER6OU1sVHhkblZGLy9oNm5HUnorZUxSU2ZMZHRhNmR5OUdrN3ZGZUZvV3ViYU5ReFF1aEx2Nys1aDlqd3c1dzBDa0JNdUZUaGYxc0o4RjhmSFc4Zk5zZlc5OGMxMVduR1FNZ1FMNjM4UGdxbTNiRVNHTDhWSkVzVUxldTNpemdCQUU1ekdIYmtVbkdBTWlINGh6L0ZaNlNKRlB4RUwxQVBnL3lBc0JrS1BzcG9xTHpxQXZHVDlDQnB3RkNtM2I2cm91NXN2RlpGYmxoYTNLcG02cWV0bTZWamNtT0xNNzdCWlYrL3JxOXVIK1hyL2ZMNHRjSW5UVHpGbGI1d1VCcEdtYWRUb3VlQ0lTcWZKaDFVd2Y4VlJSbEVvcENnUlNSTGxHWlBiUnZNU0Y4TjRiM1pZRUl5SC85ZmNmdlgzK2FPL29sRTF1dmRlSVhBakdHWmRTdHRZQ29uTk9DQUdNcGFrdzFuTEFxcTZrZ0xYdUlBQWg0NjF1TTVVd3hnUUIzTjVQNW5teHViM3g5UEhGNWRYMVlybnNadG13MTcxZkxyKzR2VHc0Mk9YOVhsWG13WHN2MEFhN3Y5UDcwWStma1orTVJzamxRRk9XTzd0K2N2YnVoNzh1RnhNdzQ2T3preXhMaXNVM2VuYXp1UHp5OVRmZjlEZldOemEyTnpjSGk4bnRjcjRvU3pOZk5tV2xtVVVrYXIycnJRVVhZaEZWSEVkSUlRSUdySFhUQnQxZWJSNS84dVo3OHVaK3NqQkhKQmtBRVFKd0JvamtWNEFoS21zQmtUTkdjUTlCSGdJUXhMUWdCQ0RKZ1ZheC9mRStHdVZQUEVJTFdCMHdlYlJCUkhkdWpPS0FlQVVCQWdBWFlsdDVpSHlkS2RWTk8vM04zYU56aG9TU3NHbmE1V3hVbDh2WmREYWYzRy8yczUzTlhtZHp2ZktPV29PQlZWVkRQbkF1RWlWOWdMWnRDQUlUa2dEUU9DUWlZSUFRaUtTU3ZXN1Bldzk4UlhJOXJRNVYzbnNnUW1USW1BOWgwZFN6VkYrK3ZGemNqbjd6d1U5NU1aTkNCT3VMdGw3cHV4Z1RRaVJKc2loeVJ5SCs1RklrU1NxbDFLYUJhRzRBME5hV1ZQdzNiWjR5aU9BQmhLa0FBQUFBU1VWT1JLNUNZSUk9Iiwic2l6ZXMiOiIxODB4MTgwIiwidHlwZSI6ImltYWdlL3BuZyIsInB1cnBvc2UiOiJhbnkifV19"

# ── Full HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<title>Weenie Wars 2026</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x1F32D;</text></svg>">
<link rel="apple-touch-icon" href="data:image/png;base64,{_ICON_B64}">
<link rel="manifest"         href="data:application/manifest+json;base64,{_MANIFEST_B64}">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#f0f4fb; color:#002868; font-family:'Segoe UI',Arial,sans-serif; padding:16px; font-size:13px; }}
  .header {{ text-align:center; margin-bottom:14px; }}
  .header h1 {{ font-size:2.8em; font-weight:900; letter-spacing:3px; line-height:1.2; }}
  .header h1 .title-text {{
    background:linear-gradient(90deg,#B22234 0%,#555 45%,#002868 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  }}
  .header h1 .title-emoji {{ -webkit-text-fill-color:initial; background:none; }}
  .header .subtitle {{ color:#7a8aaa; font-size:0.78em; margin-top:4px; letter-spacing:2px; text-transform:uppercase; }}
  .header-stripe {{ display:flex; height:3px; border-radius:2px; margin:7px auto 0; width:260px; overflow:hidden; }}
  .sr {{ flex:1; background:#B22234; }} .sw {{ flex:1; background:#ccc; }} .sb {{ flex:1; background:#002868; }}
  .banner {{
    background:#fff; border:1px solid #c8d4ea; border-top:3px solid #002868;
    border-radius:10px; padding:10px 18px; margin-bottom:12px;
    display:flex; align-items:center; gap:20px; flex-wrap:wrap;
    box-shadow:0 1px 5px rgba(0,40,104,0.07);
  }}
  .banner .label {{ color:#7a8aaa; font-size:0.7em; text-transform:uppercase; letter-spacing:1px; }}
  .banner .note  {{ color:#8a9abc; font-size:0.68em; margin-top:1px; }}
  .divider {{ width:1px; height:38px; background:#dde4f0; }}
  .mid-row {{ display:flex; gap:12px; align-items:flex-start; margin-bottom:12px; }}
  .cards-row {{ display:flex; gap:12px; align-items:stretch; margin-bottom:14px; flex-wrap:wrap; }}
  .months-wrap {{ flex:0 0 auto; align-self:flex-start; }}
  .months-row {{ display:flex; gap:8px; flex-wrap:nowrap; align-items:flex-start; }}
  .narrative-card {{
    width:100%;
    background:#fff; border:1px solid #c8d4ea; border-left:3px solid #002868;
    border-radius:9px; padding:12px 14px;
    box-shadow:0 1px 5px rgba(0,40,104,0.07);
    font-size:0.78em; line-height:1.6; color:#334466;
  }}
  .narrative-card .nt {{ font-size:0.68em; text-transform:uppercase; letter-spacing:2px; color:#7a8aaa; border-left:3px solid #B22234; padding-left:7px; margin-bottom:8px; }}
  .narrative-card p {{ margin-bottom:6px; }}
  .narrative-card p:last-child {{ margin-bottom:0; }}
  .narr-btn {{ flex:1; padding:5px 0; font-size:0.72em; font-weight:700; letter-spacing:0.5px; border:1.5px solid #002868; border-radius:5px; cursor:pointer; background:#fff; color:#002868; transition:background 0.15s,color 0.15s; }}
  .narr-btn.active {{ background:#B22234 !important; color:#fff !important; border-color:#B22234 !important; }}
  .joey-wrap {{ flex:0 0 auto; display:flex; flex-direction:column; }}
  .joey-card {{
    background:#fff; border:2px solid #B22234; border-radius:10px;
    padding:14px 16px; text-align:center; width:180px;
    box-shadow:0 2px 8px rgba(178,34,52,0.10);
    display:flex; flex-direction:column; justify-content:center;
    flex:1; text-decoration:none; color:inherit;
  }}
  .joey-card:hover {{ background:#fff5f5; }}
  .joey-card .jlabel {{ color:#8a9abc; font-size:0.68em; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }}
  .joey-card .jname  {{ font-size:0.9em; font-weight:bold; color:#002868; margin-bottom:6px; letter-spacing:1px; }}
  .joey-card .jcount {{ font-size:2.4em; font-weight:900; color:#B22234; line-height:1; }}
  .joey-card .jdogs  {{ font-size:0.72em; color:#7a8aaa; margin-top:3px; }}
  .joey-card .jyear  {{ font-size:0.65em; color:#aab4cc; margin-top:5px; letter-spacing:1px; }}
  .nathans-card {{
    background:#fff; border:2px solid #002868; border-radius:10px;
    padding:14px 16px; text-align:center; width:180px;
    box-shadow:0 2px 8px rgba(0,40,104,0.10);
    display:flex; flex-direction:column; justify-content:center;
    text-decoration:none; color:inherit; flex:1;
  }}
  .nathans-card:hover {{ background:#edf1f9; }}
  .nathans-card .nlabel {{ color:#8a9abc; font-size:0.68em; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }}
  .nathans-card .ntitle {{ font-size:0.82em; font-weight:bold; color:#002868; margin-bottom:8px; line-height:1.3; }}
  .nathans-card .ndays  {{ font-size:2.4em; font-weight:900; color:#002868; line-height:1; }}
  .nathans-card .nunit  {{ font-size:0.72em; color:#7a8aaa; margin-top:3px; }}
  .nathans-card .ndate  {{ font-size:0.65em; color:#aab4cc; margin-top:5px; letter-spacing:1px; }}
  .hours-card {{
    background: linear-gradient(135deg, #fff8f0 0%, #fff3e0 100%);
    border: 1.5px solid #e8d5b0;
    border-radius: 12px;
    padding: 16px 12px 12px;
    text-align: center;
    flex: 1;
    min-width: 140px;
  }}
  .hours-card .hlabel {{ color:#8a9abc; font-size:0.68em; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }}
  .hours-card .htitle {{ font-size:0.82em; font-weight:bold; color:#7a4a00; margin-bottom:6px; letter-spacing:1px; }}
  .hours-card .hcount {{ font-size:2.4em; font-weight:900; color:#c85000; line-height:1; }}
  .hours-card .hunit  {{ font-size:0.72em; color:#7a8aaa; margin-top:3px; }}
  .hours-card .hwhen  {{ font-size:0.65em; color:#aab4cc; margin-top:5px; letter-spacing:0.5px; }}
    .season-card {{
    background:#fff; border:2px solid #445580; border-radius:10px;
    padding:14px 16px; text-align:center; width:180px;
    box-shadow:0 2px 8px rgba(68,85,128,0.10);
    display:flex; flex-direction:column; justify-content:center; flex:1;
  }}
  .season-card .slabel {{ color:#8a9abc; font-size:0.68em; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }}
  .season-card .stitle {{ font-size:0.82em; font-weight:bold; color:#445580; margin-bottom:6px; letter-spacing:1px; }}
  .season-card .sdays  {{ font-size:2.4em; font-weight:900; color:#445580; line-height:1; }}
  .season-card .sunit  {{ font-size:0.72em; color:#7a8aaa; margin-top:3px; }}
  .season-card .send   {{ font-size:0.65em; color:#aab4cc; margin-top:5px; letter-spacing:1px; }}
  .section-title {{ font-size:0.68em; text-transform:uppercase; letter-spacing:2px; color:#7a8aaa; margin-bottom:7px; margin-top:2px; border-left:3px solid #B22234; padding-left:7px; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.93em; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 1px 6px rgba(0,40,104,0.07); }}
  thead tr {{ background:#002868; }}
  thead th {{ padding:8px 7px; text-align:center; color:#c8d4ea; font-size:0.68em; text-transform:uppercase; letter-spacing:1px; }}
  thead th:nth-child(3) {{ text-align:left; }}
  thead th.chomp-h {{ color:#FFD700; }}
  thead th.l7-h {{ color:#88ccff; }}
  thead th.odds-h {{ color:#aaffaa; }}
  thead th.p2j-h  {{ color:#ffccee; }}
  tbody tr {{ border-bottom:1px solid #edf1f9; transition:background 0.12s; }}
  tbody tr:hover {{ background:#e8f0ff!important; }}
  .legend {{ color:#7a8aaa; font-size:0.72em; margin:7px 0 5px; }}
  .stat-notes {{ display:flex; gap:8px; margin-bottom:10px; flex-wrap:wrap; }}
  .stat-note {{ font-size:0.7em; color:#8a9abc; background:#f4f7fc; border-left:2px solid #B22234; padding:4px 8px; border-radius:0 5px 5px 0; flex:1; min-width:160px; }}
  .stat-note strong {{ color:#002868; }}
  .footer {{ margin-top:12px; text-align:center; color:#aab4cc; font-size:0.68em; letter-spacing:1px; }}
  .updated-stamp {{ text-align:center; color:#8a9abc; font-size:0.78em; margin-top:10px; margin-bottom:4px; letter-spacing:0.5px; }}
  .refresh-btn {{ display:none; }}  /* hidden on desktop */
  @media (max-width:660px) {{
    .refresh-btn {{
      display:block; width:100%; margin:12px 0 4px; padding:13px;
      background:#f4f7fc; border:1.5px solid #c8d4ea; border-radius:8px;
      color:#445580; font-size:0.9em; font-weight:600; cursor:pointer;
      letter-spacing:0.5px;
    }}
    .refresh-btn:active {{ background:#dde4f2; }}
  }}
  .bottom-stripe {{ display:flex; height:3px; border-radius:2px; margin-top:10px; overflow:hidden; }}
  .bottom-stripe div {{ flex:1; }}

  /* ── Button row ───────────────────────────────────────────────────────── */
  .btn-row {{ display:flex; gap:10px; margin-bottom:12px; }}
  .btn-link {{
    display:inline-block; font-weight:bold; font-size:0.82em;
    padding:9px 18px; border-radius:6px; text-decoration:none;
    letter-spacing:0.5px; white-space:nowrap; color:#fff;
  }}
  .btn-red  {{ background:#B22234; box-shadow:0 2px 6px rgba(178,34,52,0.3); }}
  .btn-navy    {{ background:#002868; box-shadow:0 2px 6px rgba(0,40,104,0.3); }}
  .btn-install {{ display:none; background:#1a7340; box-shadow:0 2px 6px rgba(26,115,64,0.3); }}

  /* Month filter pills */
  .month-filter {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:10px; }}
  .mf-label {{ font-size:0.75em; color:#7a8aaa; text-transform:uppercase; letter-spacing:1px; flex:0 0 auto; font-weight:600; }}
  .mf-pills {{ display:flex; gap:6px; flex-wrap:wrap; }}
  .mf-pill {{
    background:#f4f7fc; border:1.5px solid #c8d4ea; border-radius:20px;
    padding:7px 16px; font-size:0.78em; font-weight:600; color:#445580;
    cursor:pointer; transition:all 0.15s;
  }}
  .mf-pill.active {{ background:#002868; border-color:#002868; color:#fff; box-shadow:0 2px 6px rgba(0,40,104,0.18); }}
  .mf-pill:hover:not(.active) {{ background:#dde4f2; }}

    /* ── Responsive / Mobile ───────────────────────────────────────────────── */
  .table-scroll {{ overflow-x:auto; -webkit-overflow-scrolling:touch; border-radius:8px; }}

  @media (max-width:660px) {{
    body {{ padding:8px; font-size:13px; }}
    .header h1 {{ font-size:1.9em; letter-spacing:1px; }}
    .header .subtitle {{ font-size:0.68em; letter-spacing:1px; }}
    .header-stripe {{ width:140px; }}

    /* Banner: 2×2 grid */
    .banner {{ display:grid; grid-template-columns:1fr 1fr; gap:10px 16px; padding:10px 12px; }}
    .divider {{ display:none; }}

    /* Buttons: full width, tall touch targets */
    .btn-row {{ flex-direction:column; gap:8px; }}
    .btn-link {{ width:100%; text-align:center; padding:13px 18px; font-size:0.9em; box-sizing:border-box; }}

    /* Month tiles: wrap 2–3 per row */
    .months-row {{ flex-wrap:wrap; gap:6px; }}
    .months-row > div {{ flex:1 1 calc(33% - 6px); min-width:90px !important; }}

    /* Cards: 3-per-row, compact */
    .cards-row {{ flex-wrap:nowrap; gap:6px; }}
    .joey-wrap {{ flex:1 1 0; min-width:0; }}
    .season-card, .joey-card, .nathans-card, .hours-card {{ width:100% !important; padding:10px 6px !important; box-sizing:border-box; }}
    .season-card .sdays, .joey-card .jcount, .nathans-card .ndays {{ font-size:1.9em; }}
    .season-card .slabel, .joey-card .jlabel, .nathans-card .nlabel {{ font-size:0.6em; }}
    .hours-card .hcount {{ font-size:1.9em; }}
    .hours-card .hlabel {{ font-size:0.6em; }}
    .season-card .stitle, .nathans-card .ntitle {{ font-size:0.72em; }}
    .joey-card .jname {{ font-size:0.78em; }}

    /* Narrative */
    .narrative-card {{ font-size:0.82em; }}

    /* Stat notes: stack vertically */
    .stat-notes {{ flex-direction:column; }}
    .stat-note {{ min-width:unset; }}

    /* Leaderboard: hide monthly cols + P2J + Odds — leaves Trend/Place/Player/Total/L7/CHOMP+ */
    #leaderboard-table th:nth-child(5),  #leaderboard-table td:nth-child(5),   /* P2J */
    #leaderboard-table th:nth-child(6),  #leaderboard-table td:nth-child(6),   /* May */
    #leaderboard-table th:nth-child(7),  #leaderboard-table td:nth-child(7),   /* June */
    #leaderboard-table th:nth-child(8),  #leaderboard-table td:nth-child(8),   /* July */
    #leaderboard-table th:nth-child(9),  #leaderboard-table td:nth-child(9),   /* Aug */
    #leaderboard-table th:nth-child(10), #leaderboard-table td:nth-child(10),  /* Sep */
    #leaderboard-table th:nth-child(13), #leaderboard-table td:nth-child(13)   /* Odds */
    {{ display:none; }}

    table {{ font-size:0.9em; }}
    thead th {{ font-size:0.65em; padding:7px 5px !important; }}
    tbody td {{ padding:8px 5px !important; }}

    .legend {{ font-size:0.68em; }}
    .section-title {{ font-size:0.65em; }}
    .footer {{ font-size:0.62em; }}

  }}
</style>
</head>
<body>

<div class="header">
  <h1><span class="title-emoji">🌭</span><span class="title-text"> WEENIE WARS 2026 </span><span class="title-emoji">🌭</span></h1>
  <div class="subtitle">Hot Dog Eating Championship &nbsp;★&nbsp; Memorial Day to Labor Day</div>
  <div class="header-stripe"><div class="sr"></div><div class="sw"></div><div class="sb"></div></div>
</div>

<div class="banner">
  <div>
    <div class="label">Leader</div>
    <div style="font-size:1.35em;font-weight:bold;color:#B8860B;line-height:1.1">🥇 {BANNER['leader_name']}</div>
    <div class="note">{BANNER['leader_total']} weenies total</div>
  </div>
  <div class="divider"></div>
  <div>
    <div class="label">🔥 Last 7 Days</div>
    <div style="font-size:1.35em;font-weight:bold;color:#002868;line-height:1.1">{BANNER['l7_leader']} &nbsp;<span style="color:#B22234">+{BANNER['l7_score']}</span></div>
    <div class="note">{BANNER['l7_note']}</div>
  </div>
  <div class="divider"></div>
  <div>
    <div class="label">Players</div>
    <div style="font-size:1.35em;font-weight:bold;color:#002868;line-height:1.1">{BANNER['players']}</div>
    <div class="note">Competing in 2026</div>
  </div>
  <div class="divider"></div>
  <div>
    <div class="label">Total Consumed</div>
    <div style="font-size:1.35em;font-weight:bold;color:#B22234;line-height:1.1">{_total_weenies} 🌭</div>
    <div class="note">{_total_lbs} lbs | {_total_ft} ft of Weenie</div>
  </div>
</div>

<div class="btn-row">
  <a href="https://docs.google.com/forms/d/e/1FAIpQLScMSUKG2thEJFaIJc4TviSwX346w8m8zJcou78Vqxdavu93kQ/viewform?usp=dialog" target="_blank" class="btn-link btn-red">
    🌭 Log Weenies Here
  </a>
  <button id="installBtn" class="btn-link btn-install" onclick="showInstallModal()" style="display:none;border:none;cursor:pointer;font-size:0.82em">
    📲 Add to Home Screen
  </button>
</div>
<div class="months-wrap" style="margin-bottom:12px;">
  <div class="section-title">Monthly Status</div>
  <div class="months-row">{month_tiles}<div id="droughtTile" style="background:#ffd700;border:2.5px solid #1a2744;border-radius:9px;padding:10px 13px;min-width:100px;text-align:center;flex-shrink:0;align-self:stretch;display:flex;flex-direction:column;justify-content:center">
    <div style="color:#1a2744;font-weight:900;font-size:0.85em;margin-bottom:5px;letter-spacing:0.5px;line-height:1.25;text-align:center">🚨 WEENIE 🚨<br>🚨 WATCH 🚨</div>
    <div style="margin-top:6px">
      <div style="font-size:0.6em;text-transform:uppercase;letter-spacing:1px;color:#1a2744;font-weight:700;margin-bottom:2px;white-space:nowrap">this group has gone</div>
      <div id="droughtMain" style="font-size:1.35em;font-weight:900;color:#cc0000;line-height:1.1;font-variant-numeric:tabular-nums;white-space:nowrap">—</div>
      <div style="font-size:0.9em;font-weight:bold;color:#1a2744;white-space:nowrap">without a 🌭</div>
    </div>
  </div></div>
</div>

<div class="cards-row">
  <div class="joey-wrap">
    <div class="section-title">Season Ends</div>
    <a href="https://tenor.com/view/hot-dog-girl-gif-12001974846064297556" target="_blank" class="season-card" style="text-decoration:none;display:block">
      <div class="slabel">⏳ Weenie Wars</div>
      <div class="stitle">Days Remaining</div>
      <div class="sdays">{SEASON_DAYS}</div>
      <div class="sunit">days left</div>
      <div class="send">★ Labor Day {SEASON_END} ★</div>
    </a>
  </div>
  <div class="joey-wrap">
    <div class="section-title">The Benchmark</div>
    <a href="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTQ4bjhncGI2YXY3Zm93OHJ1ZHZ0NzB4cGpvZHRubXkyNDF2NXJzeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/37QHg0RoCFAiEJD0oV/giphy.gif" target="_blank" class="joey-card">
      <div class="jlabel">🌭 The Man</div>
      <div class="jname">Joey Chestnut</div>
      <div class="jcount">{JOEY_COUNT}</div>
      <div class="jdogs">hot dogs in 10 min</div>
      <div class="jyear">★ 2025 RESULT ★</div>
    </a>
  </div>
  <div class="joey-wrap">
    <div class="section-title">Nathan's 2026</div>
    <a href="{NATHANS_URL}" target="_blank" class="nathans-card">
      <div class="nlabel">🌭 Contest</div>
      <div class="ntitle">Nathan's Famous Hot Dog Eating</div>
      <div class="ndays">{NATHANS_DAYS}</div>
      <div class="nunit">days away</div>
      <div class="ndate">★ {NATHANS_DATE} ★</div>
    </a>
  </div>

</div>

<div class="section-title">Recent News</div>
<div class="narrative-card" style="margin-bottom:14px;">
  <div style="display:flex;gap:6px;margin-bottom:12px;">
    <button id="nb-headlines" class="narr-btn active" onclick="switchNarrative('headlines')">📰 Headlines</button>
    <button id="nb-nick"     class="narr-btn"        onclick="switchNarrative('nick')">🔍 Nick</button>
    <button id="nb-harrison" class="narr-btn"        onclick="switchNarrative('harrison')">🕵️ Harrison</button>
  </div>
  <div id="narr-headlines">
    <div class="nt">📰 Today's Headlines</div>
    {HEADLINES_HTML}
  </div>
  <div id="narr-nick" style="display:none">
    <div class="nt">🔍 Nick Investigation Update</div>
    {NICK_LOG_HTML}
  </div>
  <div id="narr-harrison" style="display:none">
    <div class="nt">🕵️ Harrison Investigation Update</div>
    {HARRISON_LOG_HTML}
  </div>
</div>
{NARRATIVE_SWITCHER_JS}

<div class="section-title">Big Beautiful Weenies</div>
<div class="narrative-card" style="margin-bottom:14px;">
  <div style="display:flex;gap:6px;margin-bottom:12px;">
    <button id="bbw-days-btn"    class="narr-btn active" onclick="switchBBW('days')">🏆 Biggest Days</button>
    <button id="bbw-records-btn" class="narr-btn"        onclick="switchBBW('records')">🏅 Records</button>
    <button id="bbw-shots-btn"   class="narr-btn"        onclick="switchBBW('shots')">💰 Big Shot Weenies</button>
  </div>
  <div id="bbw-days">{BIG_DAYS_HTML}</div>
  <div id="bbw-records" style="display:none">{RECORDS_HTML}</div>
  <div id="bbw-shots" style="display:none">{BILLIONAIRE_CARD_HTML}</div>
</div>
<div class="section-title">Leaderboard</div>
<div class="month-filter" id="monthFilter">
  <span class="mf-label">Month:</span>
  <div class="mf-pills">
    <button class="mf-pill active" data-month="all">All</button>
    <button class="mf-pill" data-month="may"  data-col="5">May</button>
    <button class="mf-pill" data-month="june" data-col="6">Jun</button>
    <button class="mf-pill" data-month="july" data-col="7">Jul</button>
    <button class="mf-pill" data-month="aug"  data-col="8">Aug</button>
    <button class="mf-pill" data-month="sep"  data-col="9">Sep</button>
  </div>
</div>
<div class="table-scroll"><table id="leaderboard-table">
  <thead>
    <tr>
      <th data-col="0">Trend</th><th data-col="1">Place</th>
      <th data-col="2" style="text-align:left">Player</th>
      <th data-col="3">Total 🌭</th>
      <th data-col="4" class="p2j-h">P2J</th>
      <th data-col="5">May</th><th data-col="6">June</th><th data-col="7">July</th><th data-col="8">Aug</th><th data-col="9">Sep</th>
      <th data-col="10" class="l7-h">L7 Weenie Score</th>
      <th data-col="11" class="chomp-h">CHOMP+</th>
      <th data-col="12" class="odds-h">Odds</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table></div>

<div class="legend">🔥 Hot — scored most recently &nbsp;·&nbsp; 📉 Cooling — scored before, nothing lately &nbsp;·&nbsp; 🧊 Cold — no weenies yet</div>
<div class="stat-notes">
  <div class="stat-note"><strong>CHOMP+</strong> — Weighted Consumption Created Plus (wRC+ analog). League avg = 100. {STAT_CHOMP_EX}.</div>
  <div class="stat-note"><strong>P2J</strong> — % to Joey Chestnut's most recent result ({JOEY_COUNT} dogs). {STAT_P2J_EX}. Higher = closer to greatness.</div>
  <div class="stat-note"><strong>L7 Weenie Score</strong> — Weenies tracked in the last 7 days.</div>
  <div class="stat-note"><strong>Odds</strong> — American format. +300 = $100 wins $300. <span style="color:#2a7a2a">▼ shortened</span> / <span style="color:#B22234">▲ lengthened</span>.</div>
</div>

<div style="text-align:center;margin:16px 0 6px">
  <button id="wl-btn" onclick="toggleWeenielog()" style="background:#002868;color:#fff;border:none;padding:9px 24px;border-radius:6px;cursor:pointer;font-size:0.9em;font-weight:700;letter-spacing:0.4px">📋 Full Weenie Log</button>
</div>
<div id="weenie-log-panel" style="display:none;margin:0 0 18px">
  {WEENIE_LOG_HTML}
</div>

{CHART_SECTION}

<button class="refresh-btn" onclick="window.location.reload()">↻ Refresh</button>
<div class="updated-stamp">🕐 Last updated {UPDATED}</div>
<div class="footer">★ &nbsp; Odds for entertainment only &nbsp; ★ &nbsp; P2J benchmark: Joey Chestnut {JOEY_COUNT} dogs (2025) &nbsp; ★ &nbsp; CHOMP+ league avg = 1.13 weenies/player &nbsp; ★</div>
<div style="text-align:center;color:#aab4cc;font-size:0.68em;margin-top:6px;letter-spacing:0.3px;">Logged weenies may take up to 15 minutes to appear on this page.</div>
<div class="bottom-stripe">
  <div style="background:#B22234"></div><div style="background:#ddd"></div>
  <div style="background:#002868"></div><div style="background:#B22234"></div>
  <div style="background:#ddd"></div><div style="background:#002868"></div>
</div>

{PLAYER_DATA_SCRIPT}
{MOBILE_FILTER_JS}

{HOME_SCREEN_JS}
{STANDALONE_RELOAD_JS}
<script>var WW_LAST_TS={LAST_WEENIE_TS};</script>
{HOURS_SINCE_JS}
</body>
</html>"""

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "WeeniesWars_2026.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"✓ Built: {out_path}")

print(f"\u2713 Built: {out_path}")
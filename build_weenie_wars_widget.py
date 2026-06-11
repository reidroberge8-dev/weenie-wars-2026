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
    {"name":"Alex",    "place":1, "total":6,"may":5,"june":1,"july":0,"aug":0,"sep":0,"l7":1, "chomp":213,"odds":"+225","move":"▲","mc":"#B22234"},
    {"name":"Tom",     "place":2, "total":11,"may":1,"june":10,"july":0,"aug":0,"sep":0,"l7":8, "chomp":391,"odds":"+375","move":"▲","mc":"#B22234"},
    {"name":"Jake",    "place":2, "total":3,"may":3,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":107,"odds":"+800","move":"▲","mc":"#B22234"},
    {"name":"Nick",    "place":2, "total":5,"may":0,"june":5,"july":0,"aug":0,"sep":0,"l7":5, "chomp":178,"odds":"+500","move":"▼","mc":"#2a7a2a"},
    {"name":"Jess",    "place":5, "total":3,"may":2,"june":1,"july":0,"aug":0,"sep":0,"l7":1, "chomp":107,"odds":"+1500","move":"▲","mc":"#B22234"},
    {"name":"Scott",   "place":5, "total":4,"may":2,"june":2,"july":0,"aug":0,"sep":0,"l7":2, "chomp":142,"odds":"+1500","move":"▲","mc":"#B22234"},
    {"name":"Leah",    "place":5, "total":3,"may":2,"june":1,"july":0,"aug":0,"sep":0,"l7":1, "chomp":107,"odds":"+1500","move":"▲","mc":"#B22234"},
    {"name":"Jon",     "place":8, "total":4,"may":1,"june":3,"july":0,"aug":0,"sep":0,"l7":3, "chomp":142, "odds":"+4000","move":"▼","mc":"#2a7a2a"},
    {"name":"Alyssa",  "place":9, "total":0,"may":0,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":0,  "odds":"+5000","move":"▲","mc":"#B22234"},
    {"name":"Noel",    "place":9, "total":1,"may":0,"june":1,"july":0,"aug":0,"sep":0,"l7":1, "chomp":36,  "odds":"+5000","move":"▲","mc":"#B22234"},
    {"name":"Kristen", "place":9, "total":1,"may":0,"june":1,"july":0,"aug":0,"sep":0,"l7":1, "chomp":36,  "odds":"+5000","move":"▲","mc":"#B22234"},
    {"name":"Reid",    "place":9, "total":2,"may":0,"june":2,"july":0,"aug":0,"sep":0,"l7":2, "chomp":71,  "odds":"+5000","move":"▲","mc":"#B22234"},
    {"name":"Jen",     "place":9, "total":0,"may":0,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":0,  "odds":"+5000","move":"▲","mc":"#B22234"},
    {"name":"Devin",   "place":9, "total":2,"may":0,"june":2,"july":0,"aug":0,"sep":0,"l7":2, "chomp":71,  "odds":"+6000","move":"▲","mc":"#B22234"},
    {"name":"Steph",   "place":9, "total":0,"may":0,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":0,  "odds":"+5000","move":"▲","mc":"#B22234"},
    {"name":"Harrison", "place":9, "total":0,"may":0,"june":0,"july":0,"aug":0,"sep":0,"l7":0, "chomp":0,  "odds":"+5000","move":"▲","mc":"#B22234"},
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
    "leader_total":  11,
    "l7_leader":     "Tom",
    "l7_score":      8,
    "l7_note":       "3 today",
    "months_done":   1,
    "months_total":  5,
    "players":       16,
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

# ── Temporary flags ──────────────────────────────────────────────────────────
# Set to False to remove the asterisk once investigation is resolved
NICK_INVESTIGATION = True
NICK_UPDATE       = "Surveillance footage shows Nick entering a Costco at 11:58pm, purchasing 96 hot dogs, and then immediately returning them — behavior investigators call a dry run."
JOEY_COUNT    = 70.5   # Joey Chestnut's most recent result (2025) — the benchmark
BIG_DAYS      = [('Jun 6', 14), ('May 25', 12), ('Jun 11', 8), ('May 31', 3), ('Jun 5', 3)]     # auto-filled by CI: [("Jun 3", 8), ...]
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


def generate_narrative(players, joey_count):
    """Auto-generate 3-sentence analyst take from live player data."""
    active = [p for p in players if p["total"] > 0]
    if not active:
        return ("The season is underway. No weenies on the board yet — "
                "the field is completely wide open.")

    top_total = players[0]["total"]  # players already sorted by total
    leaders   = [p for p in players if p["total"] == top_total]
    l7_active = sorted([p for p in players if p["l7"] > 0], key=lambda p: -p["l7"])
    l7_leader = l7_active[0] if l7_active else None
    zeros     = [p for p in players if p["total"] == 0]

    parts = []

    # Sentence 1 — who's leading
    if len(leaders) == 1:
        ldr = leaders[0]
        p2j = round(ldr["total"] / joey_count * 100, 1)
        parts.append(
            f"{ldr['name']} leads with {ldr['total']} weenie{'s' if ldr['total'] != 1 else ''} "
            f"and a CHOMP+ of {ldr['chomp']} — {p2j}% of the way to Joey."
        )
    else:
        names = " and ".join(p["name"] for p in leaders)
        p2j = round(top_total / joey_count * 100, 1)
        parts.append(
            f"{names} are deadlocked at {top_total} weenie{'s' if top_total != 1 else ''} each "
            f"({p2j}% of Joey) — the tiebreaker is whoever logs next."
        )

    # Sentence 2 — hot hand
    if l7_leader:
        is_leader = l7_leader["name"] in [p["name"] for p in leaders]
        if is_leader:
            parts.append(
                f"{l7_leader['name']} is also the hot hand with {l7_leader['l7']} in the last 7 days, "
                f"showing no signs of slowing down."
            )
        else:
            chase = leaders[0]["total"] - l7_leader["total"]
            parts.append(
                f"{l7_leader['name']} is the hot hand with {l7_leader['l7']} in the last 7 days"
                + (f", just {chase} back from the lead." if chase > 0 else ", now tied at the top.")
            )

    # Sentence 3 — zeros or field note
    if zeros:
        znames = ", ".join(p["name"] for p in zeros[:3])
        tail   = f" and {len(zeros)-3} others" if len(zeros) > 3 else ""
        parts.append(
            f"{znames}{tail} {'have' if len(zeros) != 1 else 'has'} yet to get on the board "
            f"— the season is long."
        )
    elif len(active) >= 3:
        third = [p for p in players if p["place"] == 3]
        if third:
            parts.append(
                f"The whole field is eating — {third[0]['name']} sits third with {third[0]['total']} "
                f"and odds of {third[0]['odds']}."
            )

    return " ".join(parts)

ANALYST_TAKE = generate_narrative(PLAYERS, JOEY_COUNT)

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
    rows_html += f"""
    <tr style="background:{bg};" data-player="{p['name']}" data-chomp="{p['chomp']}" data-place="{p['place']}">
      <td style="{td};text-align:center;font-size:1em">{streak}</td>
      <td style="{td};color:{pc};font-weight:bold;text-align:center;white-space:nowrap">{icon} {p['place']}</td>
      <td style="{td};{ns}">{p['name']}{nick_badge}</td>
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
        _rbg  = "background:#f7f9fc;" if _i % 2 == 0 else ""
        _big_rows += (
            f'<tr style="{_rbg}">'
            f'<td style="padding:6px 4px;color:#334">{_date}</td>'
            f'<td style="text-align:right;padding:6px 4px;font-weight:700;color:#002868">{_cnt}</td>'
            f'<td style="text-align:right;padding:6px 4px;color:#666">{_lbs} lbs</td>'
            f'<td style="text-align:right;padding:6px 4px;color:#666">{_ft} ft</td>'
            f'</tr>'
        )
    BIG_DAYS_HTML = (
        '<div class="narrative-card" style="margin-bottom:14px;">'
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
        '</div>'
    )
else:
    BIG_DAYS_HTML = ""

# ── Compute narrative ────────────────────────────────────────────────────────

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
<link rel="apple-touch-icon" id="ati">
<script>
(function(){{
  var c=document.createElement('canvas');c.width=c.height=180;
  var x=c.getContext('2d');
  x.fillStyle='#f0f4fb';x.beginPath();x.roundRect(0,0,180,180,32);x.fill();
  x.font='115px serif';x.textAlign='center';x.textBaseline='middle';
  x.fillText('🌭',90,96);
  document.getElementById('ati').href=c.toDataURL('image/png');
}})();
</script>
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
  .btn-navy {{ background:#002868; box-shadow:0 2px 6px rgba(0,40,104,0.3); }}

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
    .season-card, .joey-card, .nathans-card {{ width:100% !important; padding:10px 6px !important; box-sizing:border-box; }}
    .season-card .sdays, .joey-card .jcount, .nathans-card .ndays {{ font-size:1.9em; }}
    .season-card .slabel, .joey-card .jlabel, .nathans-card .nlabel {{ font-size:0.6em; }}
    .season-card .stitle, .nathans-card .ntitle {{ font-size:0.72em; }}
    .joey-card .jname {{ font-size:0.78em; }}

    /* Narrative */
    .narrative-card {{ font-size:0.82em; }}

    /* Stat notes: stack vertically */
    .stat-notes {{ flex-direction:column; }}
    .stat-note {{ min-width:unset; }}

    /* Table: hide monthly cols + P2J + Odds — leaves Trend/Place/Player/Total/L7/CHOMP+ */
    table th:nth-child(5),  table td:nth-child(5),   /* P2J */
    table th:nth-child(6),  table td:nth-child(6),   /* May */
    table th:nth-child(7),  table td:nth-child(7),   /* June */
    table th:nth-child(8),  table td:nth-child(8),   /* July */
    table th:nth-child(9),  table td:nth-child(9),   /* Aug */
    table th:nth-child(10), table td:nth-child(10),  /* Sep */
    table th:nth-child(13), table td:nth-child(13)   /* Odds */
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
  <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ" target="_blank" class="btn-link btn-navy">
    🌭 Click for FREE WEENIES!
  </a>
</div>
<div class="months-wrap" style="margin-bottom:12px;">
  <div class="section-title">Monthly Status</div>
  <div class="months-row">{month_tiles}</div>
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

<div class="narrative-card" style="margin-bottom:14px;">
  <div class="nt">🔍 Nick Investigation Update</div>
  <div style="font-size:0.7em;color:#8a9abc;margin-bottom:10px;letter-spacing:0.5px">Supreme Weenie Update — {UPDATED}</div>
  <p style="margin:0;color:#334;font-size:0.92em;line-height:1.6">{NICK_UPDATE}</p>
</div>

<div class="narrative-card" style="margin-bottom:14px;">
  <div class="nt">📊 Analyst's Take</div>
  <p style="margin:0;color:#334;font-size:0.92em;line-height:1.6">{ANALYST_TAKE}</p>
</div>

{BIG_DAYS_HTML}
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

{STANDALONE_RELOAD_JS}
</body>
</html>"""

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "WeeniesWars_2026.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"✓ Built: {out_path}")

print(f"\u2713 Built: {out_path}")
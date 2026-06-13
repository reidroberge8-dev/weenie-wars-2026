#!/usr/bin/env python3
"""
Weenie Wars 2026 — CI Auto-Update Script
Fetches Google Sheet, checks if new entries exist, rebuilds + redeploys only if changed.
State tracked in last_seen.json (committed back to repo on each change).
"""
import urllib.request, csv, io, json, os, re, sys, subprocess, random, shutil, hashlib
from datetime import datetime, timedelta

ROOT         = os.path.dirname(os.path.abspath(__file__))
BUILD_SCRIPT = os.path.join(ROOT, "build_weenie_wars_widget.py")
HTML_OUT     = os.path.join(ROOT, "WeeniesWars_2026.html")
PUBLIC_HTML  = os.path.join(ROOT, "public", "index.html")
STATE_FILE   = os.path.join(ROOT, "last_seen.json")

SHEET_CSV = "https://docs.google.com/spreadsheets/d/1-NezoEWSZpeUIZem89ZMltE-kGX_P11LqKVoAwSG0gU/export?format=csv&gid=1814658863"

NICK_UPDATES = [
    "Prosecutors note that Nick spelled his own name wrong on three separate weenie logs — investigators believe this was intentional.",
    "A hot dog vendor near Nick's home has gone suspiciously silent after being subpoenaed by the Commission.",
    "DNA analysis of a suspicious frankfurter found in Nick's trash revealed it was, quote, not a real weenie by any legal definition.",
    "Nick was seen on security footage furtively rearranging hot dogs at a county fair — his attorney called it an innocent reorganization.",
    "Commission forensic accountants discovered Nick submitted 11 weenie receipts from a restaurant that does not exist.",
    "An anonymous tipster, known only as Deep Relish, has provided the Commission with a USB drive labeled DO NOT OPEN.",
    "Nick's Google search history, obtained via warrant, includes how many hot dogs does it take to be innocent and best lawyers for weenie fraud.",
    "The Weenie Commission confirmed that at least two of Nick's logged entries were submitted from coordinates located in the middle of Lake Erie.",
    "Nick filed a motion to have the word fraudulent stricken from the record on the grounds that it hurts his feelings. The motion was denied.",
    "Testimony from Nick's neighbor suggests he was seen at 2am doing something suspicious with a bun the night before entries were due.",
    "Commission investigators found a receipt for 47 hot dogs charged to a corporate card registered to a shell company called Nicky's Real Weenies LLC.",
    "Nick claimed he ate the disputed weenies in a dream — a defense the Supreme Weenie described as unprecedented and inadmissible.",
    "A forensic condiment analyst concluded that the mustard stains on Nick's submitted photos do not match any commercially available mustard.",
    "Nick's own phone autocorrects hot dog to fraud — investigators are treating this as a confession.",
    "The Commission has placed Nick's weenie scale under independent audit after discovering it was previously owned by a carnival.",
    "Witnesses testified that Nick was googling is it illegal to eat a hot dog on behalf of someone else three days before the submission deadline.",
    "Commission experts concluded that four of Nick's entry timestamps are physically impossible unless he ate hot dogs in two states simultaneously.",
    "Nick presented a character witness — his own dog — who provided no useful testimony and ate two exhibit hot dogs.",
    "A handwriting expert confirmed that Nick's weenie log entries were written with the penmanship of a man who knows he is lying.",
    "The Supreme Weenie has requested that Nick surrender his mustard privileges pending final judgement.",
    "Surveillance footage shows Nick entering a Costco at 11:58pm, purchasing 96 hot dogs, and then immediately returning them — behavior investigators call a dry run.",
    "Nick's alibi for June 3rd — I was simply existing — has been flagged as legally insufficient.",
]

HARRISON_UPDATES = [
    "FBI (Food Baby Investigations) has confirmed that Harrison, known in weenie circles as Uncle Sam the Glizzy Man, is the subject of a formal Fraudfurter inquiry — the most serious classification in weenie law.",
    "Photo forensic analysts determined that the Food Baby belly in Harrison's insurance claim was induced by burgers — a finding the FBI called deeply unpatriotic.",
    "Harrison's insurance agent confirmed receiving twelve Food Baby photos over six weeks, each captioned proudly eaten these — investigators note the caption was factually inaccurate.",
    "The FBI subpoenaed Harrison's refrigerator and found evidence consistent with repeated, premeditated burger consumption. His attorney called it seasoning research.",
    "Uncle Sam the Glizzy Man has retained legal counsel specializing in Fraudfurter defense — a niche practice the Supreme Weenie described as unfortunately necessary.",
    "Forensic dieticians testified that the curvature, density, and trajectory of Harrison's Food Baby are inconsistent with hot dog consumption under any known eating model.",
    "Harrison's insurance agent told investigators he assumed the Food Baby photos were just updates from a friend, and that he deeply regrets opening his email.",
    "FBI agents executing a search warrant at Harrison's residence discovered a freezer containing forty-seven burger patties, zero hot dogs, and a framed photo of himself eating at a fast food restaurant.",
    "The Supreme Weenie has elevated Harrison's case to a Class 1 Fraudfurter — a designation that carries mandatory mustard forfeiture upon conviction.",
    "Harrison submitted a notarized statement claiming the burgers were consumed accidentally and that he thought they were very flat hot dogs. The FBI called this the worst alibi in Food Baby law.",
    "A thermal imaging analysis of Harrison's Food Baby photos revealed a heat signature consistent with burger grease, not weenie residue — investigators say the science is damning.",
    "The insurance company's fraud unit flagged Harrison's claim after noting that his Food Baby appeared to shift positions between photos — behavior inconsistent with legitimate weenie bloat.",
    "Harrison told investigators he sent the Food Baby photos to his insurance agent by mistake and that they were meant for his mom. Neither his attorney nor his mom would comment.",
    "An FBI field agent embedded at Harrison's local cookout observed him consuming three cheeseburgers while maintaining eye contact with the security camera — behavior analysts call a power move and also a crime.",
    "Harrison's Venmo history, obtained by investigators, includes charges to contacts listed as Burger Guy, Definitely Not a Weenie, and What Harrison Owes the FBI.",
    "The Weenie Commission has formally added Harrison's case to the Fraudfurter Registry — a database the Supreme Weenie described as alarmingly full.",
    "Harrison's defense team filed a motion arguing that the Food Baby is a protected form of artistic expression. The motion was denied on the grounds that it made no sense.",
    "Forensic accountants revealed that Harrison filed a separate insurance claim for emotional distress caused by being unable to eat more weenies — a claim investigators are calling audacious.",
    "The FBI has assigned four agents to the Harrison case, two of whom have requested reassignment after reviewing the Food Baby photo evidence.",
    "Uncle Sam the Glizzy Man was photographed outside his attorney's office wearing a shirt that read I Did Not Do This — investigators seized it as evidence.",
    "A grand jury has been convened to hear testimony in the Harrison Fraudfurter case. Jurors were provided food vouchers valid for hot dogs only, which investigators call a precautionary measure.",
    "Harrison's alibi for the night in question — I was simply being a patriot — has been entered into the record as Exhibit 14: Things That Are Not Defenses.",
]

today      = datetime.now()  # defined here so cache-bust and all downstream code can use it

# ── Fetch CSV ─────────────────────────────────────────────────────────────────
print("Fetching sheet...")
raw_csv = urllib.request.urlopen(SHEET_CSV + f"&_={int(today.timestamp())}").read()  # cache-bust
csv_hash = hashlib.sha256(raw_csv).hexdigest()
rows = list(csv.DictReader(io.StringIO(raw_csv.decode("utf-8"))))
print(f"  {len(rows)} entries | hash={csv_hash[:12]}...")

# ── Change detection ──────────────────────────────────────────────────────────
last_state = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        last_state = json.load(f)

last_hash      = last_state.get("csv_hash", "")
today_date     = today.strftime("%Y-%m-%d")

scores_changed = csv_hash != last_hash
force_rebuild  = os.environ.get("FORCE_REBUILD", "false") == "true"

# Stale-script detection: compare live sheet totals to build script.
# Catches manual pushes that overwrote CI-updated scores.
with open(BUILD_SCRIPT, "r", encoding="utf-8") as _f:
    _bsrc = _f.read()
_script_totals = {m.group(1): int(m.group(2)) for m in re.finditer(r'"name":"(\w+)"[^}]*?"total":(\d+)', _bsrc)}
_live_totals = {}
for _r in rows:
    _n = _r["Name"].strip().replace("John", "Jon")
    _live_totals[_n] = _live_totals.get(_n, 0) + int(_r["Weenies Consumed"])
scores_stale = any(_script_totals.get(n, -1) != _live_totals.get(n, 0) for n in _script_totals)
if scores_stale:
    print(f"  Script scores stale ({sum(_live_totals.values())} sheet vs {sum(_script_totals.values())} script) — forcing update.")

if not scores_changed and not force_rebuild and not scores_stale:
    print("No new entries, scores current — skipping.")
    sys.exit(0)

if scores_changed:
    print(f"  Score change detected ({last_hash[:12] if last_hash else 'none'} → {csv_hash[:12]}) — full update.")
elif scores_stale:
    print("  Scores out of sync with sheet — resyncing.")
else:
    print("  No new weenies — 8am daily force-rebuild.")
    print(f"  Score change detected ({last_hash[:12] if last_hash else 'none'} → {csv_hash[:12]}) — full update.")
else:
    print("  No new weenies — 8am daily force-rebuild.")

# ── Calculate scores ──────────────────────────────────────────────────────────
l7_cutoff = today - timedelta(days=7)
totals = {}; month_scores = {5:{}, 6:{}, 7:{}, 8:{}, 9:{}}; l7 = {}

for row in rows:
    name = row["Name"].strip()
    if name == "John": name = "Jon"
    n  = int(row["Weenies Consumed"])
    dt = datetime.strptime(row["Timestamp"], "%m/%d/%Y %H:%M:%S")
    totals[name] = totals.get(name, 0) + n
    if dt.month in month_scores:
        month_scores[dt.month][name] = month_scores[dt.month].get(name, 0) + n
    if dt >= l7_cutoff:
        l7[name] = l7.get(name, 0) + n

# ── Top 5 biggest weenie days ────────────────────────────────────────────────
day_totals = {}
for row in rows:
    _dt_d = datetime.strptime(row["Timestamp"], "%m/%d/%Y %H:%M:%S")
    _dk   = f"{_dt_d.strftime('%b')} {_dt_d.day}"
    day_totals[_dk] = day_totals.get(_dk, 0) + int(row["Weenies Consumed"])
top5_days = sorted(day_totals.items(), key=lambda x: x[1], reverse=True)[:5]

# ── Fetch Forbes Real-Time Billionaires ──────────────────────────────────────
FORBES_URL   = "https://www.forbes.com/forbesapi/person/rtb/0/position/true.json?fields=personName,finalWorth,naturalId&limit=5"
WEENIE_PRICE = 5.0
bill_state   = last_state.get("bill_day_start", {})
billionaires = None
try:
    import urllib.request as _ureq
    _freq = _ureq.Request(FORBES_URL, headers={"User-Agent": "Mozilla/5.0"})
    with _ureq.urlopen(_freq, timeout=10) as _fr:
        _fdata = json.loads(_fr.read())
    bill_now = {
        p["personName"]: p["finalWorth"]
        for p in _fdata["personList"]["personsLists"][:5]
    }
    today_str  = today.strftime("%Y-%m-%d")
    bill_date  = bill_state.get("date", "")
    bill_start = bill_state.get("values", {})
    if bill_date != today_str:
        # New day — snapshot becomes the day-start baseline
        bill_start = dict(bill_now)
        bill_state = {"date": today_str, "values": bill_start}
    billionaires = []
    for i, (bname, worth_m) in enumerate(sorted(bill_now.items(), key=lambda x: -x[1])[:5]):
        delta_b = (worth_m - bill_start.get(bname, worth_m)) / 1000
        billionaires.append({
            "rank":    i + 1,
            "name":    bname,
            "worth_b": round(worth_m / 1000, 1),
            "delta_b": round(delta_b, 1),
        })
    print(f"  Forbes RTB: {[b['name'].split()[-1] for b in billionaires]}")
except Exception as _fe:
    print(f"  Forbes RTB fetch failed: {_fe}")

# ── Update build script in memory ────────────────────────────────────────────
print("Updating build script...")
with open(BUILD_SCRIPT, "r", encoding="utf-8") as f:
    src = f.read()

players_section = re.search(r'PLAYERS\s*=\s*\[(.*?)\]', src, re.DOTALL).group(1)
player_names    = re.findall(r'"name":"(\w+)"', players_section)
n_players       = len(player_names)
total_weenies   = sum(totals.get(p, 0) for p in player_names)
league_avg      = total_weenies / n_players if n_players else 1
print(f"  {n_players} players, {total_weenies} weenies, avg={league_avg:.3f}")

# Dynamic odds: parimutuel model — weight = total + 0.5 baseline per player
_odds_weights = {n: totals.get(n, 0) + 0.5 for n in player_names}
_odds_total   = sum(_odds_weights.values())
def _odds(name):
    prob = _odds_weights[name] / _odds_total
    raw  = (1 / prob - 1) * 100
    return '+' + str(max(100, round(raw / 50) * 50))

def g(d, k): return d.get(k, 0)

updated = 0
for name in player_names:
    t    = g(totals, name)
    may  = g(month_scores[5],  name)
    june = g(month_scores[6],  name)
    july = g(month_scores[7],  name)
    aug  = g(month_scores[8],  name)
    sep  = g(month_scores[9],  name)
    l7v  = g(l7, name)
    chmp  = round(t / league_avg * 100) if t > 0 else 0
    oddsv = _odds(name)
    pattern = (
        rf'("name":"{name}"[^{{}}]*?"total":)\d+'
        rf'(,"may":)\d+(,"june":)\d+(,"july":)\d+(,"aug":)\d+(,"sep":)\d+'
        rf'(,"l7":)\d+(,\s*"chomp":)\s*\d+(,\s*"odds":"[^"]*")'
    )
    repl = rf'\g<1>{t}\g<2>{may}\g<3>{june}\g<4>{july}\g<5>{aug}\g<6>{sep}\g<7>{l7v}\g<8>{chmp},"odds":"{oddsv}"'
    new_src, n = re.subn(pattern, repl, src)
    if n: src = new_src; updated += 1

if totals:
    leader = max(player_names, key=lambda p: g(totals, p))
    src = re.sub(r'"leader_name":\s*"[^"]+"',  f'"leader_name":   "{leader}"',          src)
    src = re.sub(r'"leader_total":\s*\d+',      f'"leader_total":  {g(totals, leader)}', src)
if l7:
    l7_leader = max(l7, key=l7.get)
    src = re.sub(r'"l7_leader":\s*"[^"]+"', f'"l7_leader":     "{l7_leader}"',    src)
    src = re.sub(r'"l7_score":\s*\d+',      f'"l7_score":      {l7[l7_leader]}',  src)
    # Dynamic l7_note: how many weenies l7_leader logged today (UTC date, close enough for ET)
    l7_today = sum(
        int(row["Weenies Consumed"]) for row in rows
        if (row["Name"].strip().replace("John", "Jon")) == l7_leader
        and datetime.strptime(row["Timestamp"], "%m/%d/%Y %H:%M:%S").date() == today.date()
    )
    l7_note_val = f"{l7_today} today" if l7_today > 0 else "none today"
    src = re.sub(r'"l7_note":\s*"[^"]*"', f'"l7_note":       "{l7_note_val}"', src)
    print(f"  l7_note → {l7_note_val}")
src = re.sub(r'"players":\s*\d+,',         f'"players":       {n_players},',     src)
src = re.sub(r'BIG_DAYS\s*=\s*\[[^\]]*\]', f'BIG_DAYS      = {repr(top5_days)}', src)
# UPDATED is computed dynamically at build time — no regex needed
# Nick sentence only rotates on the 8am daily force-rebuild
if force_rebuild:
    src = re.sub(r'NICK_UPDATE\s*=\s*"[^"]*"', f'NICK_UPDATE       = "{random.choice(NICK_UPDATES)}"', src)
    print("  Nick sentence rotated (8am rebuild).")
    src = re.sub(r'HARRISON_UPDATE\s*=\s*"[^"]*"', f'HARRISON_UPDATE       = "{random.choice(HARRISON_UPDATES)}"', src)
    print("  Harrison sentence rotated (8am rebuild).")

# Compute LAST_WEENIE_TS — most recent weenie entry, ET→UTC
if rows:
    last_row = max(rows, key=lambda r: datetime.strptime(r["Timestamp"], "%m/%d/%Y %H:%M:%S"))
    last_dt  = datetime.strptime(last_row["Timestamp"], "%m/%d/%Y %H:%M:%S") + timedelta(hours=4)  # ET→UTC
    last_ts_unix = int((last_dt - datetime(1970, 1, 1)).total_seconds())
    src = re.sub(r'LAST_WEENIE_TS\s*=\s*\d+', f'LAST_WEENIE_TS = {last_ts_unix}', src)
    print(f"  LAST_WEENIE_TS → {last_ts_unix} ({last_row['Timestamp']} ET)")

if billionaires is not None:
    src = re.sub(
        r'BILLIONAIRE_DATA\s*=\s*\[[^\]]*\](?:\s*#[^\n]*)?',
        f'BILLIONAIRE_DATA = {repr(billionaires)}  # auto-filled by CI',
        src
    )
    print(f"  BILLIONAIRE_DATA patched ({len(billionaires)} entries)")

with open(BUILD_SCRIPT, "w", encoding="utf-8") as f:
    f.write(src)
print(f"  {updated}/{n_players} player rows updated")

# ── Build HTML ────────────────────────────────────────────────────────────────
result = subprocess.run([sys.executable, BUILD_SCRIPT], capture_output=True, text=True, cwd=ROOT)
if result.returncode != 0:
    print("BUILD ERROR:", result.stderr); sys.exit(1)
print(result.stdout.strip())

os.makedirs(os.path.join(ROOT, "public"), exist_ok=True)
shutil.copy(HTML_OUT, PUBLIC_HTML)

# ── Deploy to Firebase ────────────────────────────────────────────────────────
print("Deploying to Firebase...")
result = subprocess.run(
    ["firebase", "deploy", "--only", "hosting", "--project", "weenie-wars-2026", "--non-interactive"],
    capture_output=True, text=True, cwd=ROOT
)
if result.returncode != 0:
    print("DEPLOY ERROR:", result.stderr); sys.exit(1)
print(f"Live: https://weenie-wars-2026.web.app  ({today.strftime('%Y-%m-%d %H:%M UTC')})")

# ── Save new state + commit ───────────────────────────────────────────────────
with open(STATE_FILE, "w") as f:
    _state_out = {"csv_hash": csv_hash, "row_count": len(rows), "updated": today.isoformat()}
    if bill_state:
        _state_out["bill_day_start"] = bill_state
    json.dump(_state_out, f, indent=2)

subprocess.run(["git", "config", "user.name",  "github-actions[bot]"], cwd=ROOT)
subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], cwd=ROOT)
subprocess.run(["git", "add", "last_seen.json", "build_weenie_wars_widget.py"], cwd=ROOT)
result = subprocess.run(["git", "commit", "-m", f"Auto-update {today.strftime('%Y-%m-%d %H:%M')} UTC"], cwd=ROOT, capture_output=True, text=True)
if result.returncode == 0:
    subprocess.run(["git", "push"], cwd=ROOT)
    print("State committed.")



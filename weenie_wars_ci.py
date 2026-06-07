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

today      = datetime.now()  # defined here so cache-bust and all downstream code can use it

# ── Fetch CSV ─────────────────────────────────────────────────────────────────
print("Fetching sheet...")
raw_csv = urllib.request.urlopen(SHEET_CSV + f"&_={int(today.timestamp())}", timeout=20).read()  # cache-bust
csv_hash = hashlib.sha256(raw_csv).hexdigest()
rows = list(csv.DictReader(io.StringIO(raw_csv.decode("utf-8"))))
print(f"  {len(rows)} entries | hash={csv_hash[:12]}...")

# ── Change detection ──────────────────────────────────────────────────────────
last_state = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        last_state = json.load(f)

last_hash       = last_state.get("csv_hash", "")
scores_changed = csv_hash != last_hash
force_rebuild  = os.environ.get("FORCE_REBUILD", "false") == "true"

if not scores_changed and not force_rebuild:
    print("No new entries and not daily rebuild — skipping.")
    sys.exit(0)

if scores_changed:
    print(f"  Score change detected ({last_hash[:12] if last_hash else 'none'} → {csv_hash[:12]}) — full update.")
elif force_rebuild:
    print("  No new weenies — 8am daily force-rebuild.")
else:
    print("  Rebuilding (unexpected path).")

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
    chmp = round(t / league_avg * 100) if t > 0 else 0
    pattern = (
        rf'("name":"{name}"[^{{}}]*?"total":)\d+'
        rf'(,"may":)\d+(,"june":)\d+(,"july":)\d+(,"aug":)\d+(,"sep":)\d+'
        rf'(,"l7":)\d+(,\s*"chomp":)\s*\d+'
    )
    repl = rf'\g<1>{t}\g<2>{may}\g<3>{june}\g<4>{july}\g<5>{aug}\g<6>{sep}\g<7>{l7v}\g<8>{chmp}'
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
src = re.sub(r'"players":\s*\d+,',         f'"players":       {n_players},',     src)
# UPDATED is computed dynamically at build time — no regex needed
if force_rebuild:
    src = re.sub(r'NICK_UPDATE\s*=\s*"[^"]*"', f'NICK_UPDATE       = "{random.choice(NICK_UPDATES)}"', src)

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
    json.dump({"csv_hash": csv_hash, "row_count": len(rows), "updated": today.isoformat()}, f, indent=2)

subprocess.run(["git", "config", "user.name",  "github-actions[bot]"], cwd=ROOT)
subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], cwd=ROOT)
subprocess.run(["git", "add", "last_seen.json", "build_weenie_wars_widget.py"], cwd=ROOT)
result = subprocess.run(["git", "commit", "-m", f"Auto-update {today.strftime('%Y-%m-%d %H:%M')} UTC"], cwd=ROOT, capture_output=True, text=True)
if result.returncode == 0:
    subprocess.run(["git", "push"], cwd=ROOT)
    print("State committed.")



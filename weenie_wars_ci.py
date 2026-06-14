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
    "The Commission's lead forensic analyst testified that Nick's submission photos contain EXIF data placing them 14 miles from any known hot dog vendor. When asked to explain, Nick said he walked. The analyst noted the timestamp was 3:17am. Nick said he is a night walker. This is being investigated separately.",
    "Commission investigators subpoenaed Nick's grocery receipts and found zero hot dog purchases since February. Nick claims he has a private supplier. The FBI has been notified. The private supplier has not been located. Nick's dog is a person of interest. The dog has retained its own attorney.",
    "Nick's fitness tracker data, obtained via court order, shows zero calories burned consistent with hot dog consumption on four of his submitted dates. His attorney argued he has a very efficient metabolism. The judge removed her glasses and rubbed her temples for forty-five seconds before responding.",
    "Surveillance footage from a 7-Eleven shows Nick entering at 2:47am, wandering the hot dog roller section for eleven minutes, purchasing nothing, and leaving while staring at the ceiling. Behavioral analysts have been studying the tape for three weeks and remain baffled and also slightly unsettled.",
    "A grocery store camera caught Nick purchasing a single hot dog bun with no hot dog at 11:52pm on a Tuesday. Investigators spent six weeks trying to understand this and filed it under the most suspicious innocent act we have ever witnessed. The bun is in cold storage and has been entered into evidence.",
    "Nick submitted a 47-page brief arguing his weenies should count double because he ate them while thinking about hot dogs very intensely. The Supreme Weenie read the first page and ordered a psychiatric evaluation. The evaluation described Nick as impressively committed and deeply unusual.",
    "Forensic accountants traced a payment of $847 from Nick to a Venmo contact labeled Not a Hot Dog Guy on the same day as his largest single-day entry. Neither Nick nor Not a Hot Dog Guy would comment. Not a Hot Dog Guy has since deleted his account. The Commission has issued a warrant for his bun.",
    "The Commission's star witness, a former hot dog cart operator, testified that Nick once asked him to sign a napkin reading I saw Nick eat these. The cart operator refused. Nick said that's fine, I have a printer at home. The napkin was later recovered from Nick's recycling bin, printed on standard inkjet paper.",
    "Nick's alibi for the disputed June entries — I was in a flow state — has been entered into the Commission record as Exhibit 44: Legally Meaningless Statements. His attorney expressed confidence. The Supreme Weenie expressed the opposite and asked everyone to please take this more seriously than Nick is.",
    "An anonymous letter signed only as A Friend of Justice claims Nick keeps a second weenie log in a shoebox under his bed. The Commission issued a search warrant. Nick immediately requested a lawyer specifically about the shoebox. The Commission noted this was not the response of an innocent person.",
    "Lab technicians analyzed Nick's fork for DNA evidence and found traces of bratwurst, kielbasa, and a substance described as aggressively not a hot dog. Nick's attorney called it contamination. The lead technician called it, quote, an open-and-shut situation, and asked to be directly quoted in the report.",
    "Nick was observed at a cookout standing next to an unlit grill for forty minutes, holding an uncooked hot dog, staring into the middle distance. When approached by an investigator he said he was marinating it with his mind. This was entered as Exhibit 67: The Mind Marination Incident.",
    "The Supreme Weenie issued a Writ of Mustard Suspicion after Nick's attorney argued that eating hot dogs with the lights off should be exempt from logging. The motion was denied, read aloud to the full Commission, framed, and hung next to the portrait of the Supreme Weenie. Nick was sent a photo of it.",
    "Prosecutors revealed Nick has filed seventeen complaints about the investigation, including one titled This Is Unfair and another labeled Please Stop. Both were denied and added to the evidence file under consciousness of guilt, which Nick spelled as conciousness in all seventeen filings.",
    "A neighbor submitted an affidavit stating Nick's apartment smells, and I mean this with the full weight of a legal document, nothing like hot dogs. Nick's attorney called it inadmissible on grounds of being rude. The Commission admitted it anyway and thanked the neighbor for their service.",
    "The Commission's technical team analyzed Nick's photo timestamps and found all 23 entries were uploaded exactly 4 seconds apart, which they described as impossible for a human eating at the claimed pace and also suspicious even if you do not know what a hot dog is. Nick said he is a fast uploader.",
    "Nick's phone had a folder labeled Logs, a folder labeled Logs (Real), and a third labeled Logs (Real) (Final) (Do Not Open). This was observed during a bathroom break. Nick's attorney moved to strike the observation. It was not stricken. All three folders were subpoenaed. The third was password protected. The password was weenie.",
    "Commission psychological profilers reviewed Nick's log entries and identified a pattern of escalating confidence in the handwriting they describe as consistent with someone who believes they have gotten away with something. Nick described this as rude and also wrong. The profilers noted this response in the profile.",
    "Nick arrived at his Commission hearing forty-five minutes late carrying a box of hot dogs he described as a peace offering. The box was immediately seized and sent to the lab. Results confirmed the hot dogs were purchased that morning specifically for the hearing. Nick said that shouldn't matter. It matters.",
    "The Commission obtained Nick's Amazon history and found three orders for the book How to Document Eating Without Actually Eating. Nick says he has never heard of this book. It was delivered to his address. He signed for all three. The delivery driver has been deposed. The book has been read into the record.",
    "A Commission investigator posing as a vendor offered Nick a complimentary hot dog at a street fair. Nick declined, said he was full, and immediately entered three hot dogs into his log for that day. The investigator documented this in real time while standing two feet away. Nick did not appear to notice.",
    "Nick's dentist submitted a deposition stating that his dental wear is inconsistent with the frequency of hot dog consumption claimed and is instead consistent with someone who eats a normal amount and then lies about it. Nick's response was to switch dentists. The new dentist has also been subpoenaed.",
    "Technical analysts confirmed the background in four of Nick's submitted photos is the same kitchen on all claimed dates. When asked how March, April, June, and July all show the same unwashed dish, Nick said he has a lot of dishes. The dish has been subpoenaed. It has been washed. This was considered obstruction.",
    "Nick attempted to submit a character reference from someone listed only as A Respected Weenie Authority. The Commission confirmed no such person exists in any database or field adjacent to weenies. Nick was asked who this person is. Nick said he would rather not say. The Commission said that is suspicious. Nick said he knows.",
    "The Supreme Weenie released a public statement calling the Nick case the most complex and deeply weird investigation in Commission history and urged the public to remain calm. Nick responded by filing a defamation complaint against the Supreme Weenie. The complaint was denied. The statement was updated to include this fact.",
]

HARRISON_UPDATES = [
    "FBI forensic dieticians calculated that Harrison's claimed weenie intake would require a jaw aperture 340% wider than the human physiological maximum. His attorney stated his client has an unusually committed bite. The judge asked the courtroom to please stop laughing. The courtroom did not stop for several minutes.",
    "Uncle Sam the Glizzy Man appeared at his deposition in a t-shirt reading Glizzy Innocent in large block letters, which his attorney had specifically told him not to wear. The shirt was confiscated as evidence. Harrison asked for it back three times during the deposition. The answer was no each time. He asked a fourth time while leaving.",
    "The FBI obtained Harrison's DoorDash history under subpoena and found 31 burger deliveries in 90 days, zero hot dog orders, and one order listed only as the usual from a restaurant that does not appear in any business registry. Investigators have been searching for six weeks. Harrison calls it a very private place.",
    "Harrison's insurance adjuster testified that upon receiving the eleventh Food Baby photo, he called his supervisor assuming it was a prank. His supervisor also assumed it was a prank. They called the next supervisor up. She also assumed a prank. All three are in therapy and have requested to not discuss this further.",
    "Forensic acoustics experts analyzed a voicemail Harrison left his attorney in which beef sizzling was identified at 14 timestamps. His attorney listened to the full recording and immediately filed a motion to withdraw. It was denied. The attorney remains on the case. He has not smiled since receiving the voicemail.",
    "The Commission's star witness, a gas station attendant, testified Harrison purchased something cylindrical in a bun on the date in question. Under cross-examination it emerged the station also sells corn dogs, taquitos, mystery rollers, and something the attendant called simply the big one. The case was reclassified as urgent.",
    "FBI surveillance photographed Harrison at a barbecue where four grills were running and none were cooking hot dogs. Harrison described it as a mistake he walked into. Investigators noted he was wearing an apron, holding tongs, wearing a chef hat that said Grill Master, and appeared to be genuinely having the time of his life.",
    "Harrison filed a counter-complaint arguing the investigation violates his constitutional right to a belly. The Commission's legal team confirmed it is not a real argument in any jurisdiction, denied it, laminated it, and hung it in the break room. They said it genuinely brightened the office and they look at it every morning.",
    "The FBI recovered a Post-it from Harrison's bin reading remember: hot dogs only, no burgers, they are watching. A second read also destroy this note. A third read I know I said destroy it but I keep forgetting. He had not destroyed any of them. All three are now in evidence. A fourth was found reading I really need to destroy these.",
    "Harrison's neighbors submitted a joint petition describing his backyard as consistently and aggressively smelling like a Wendy's throughout the competition. His attorney called it circumstantial. The Commission scheduled a press conference thanking the neighbors for their courage and presenting them with a certificate.",
    "Uncle Sam the Glizzy Man sent a Commission investigator a gift basket containing artisan mustards, a hot dog-shaped stress toy, and a card reading let's call this even, friend. The basket was logged as evidence. The stress toy was entered as Exhibit 39. It subsequently went missing from the evidence room. The search is ongoing.",
    "Harrison's defense submitted expert testimony arguing that under a sufficiently loose definition of hot dog, a burger could technically qualify if consumed with patriotic intent. The Supreme Weenie placed the testimony in a folder labeled No, locked the folder, and adjourned early out of what she described as personal frustration with the concept.",
    "A Commission wiretap captured Harrison telling an associate that the key is confidence and also receipts. The associate said why do you have receipts for this. Harrison said I made them. The associate said nothing for eleven seconds and hung up. Both are under investigation. The associate's name in Harrison's phone is Not Involved.",
    "Investigators found a folder on Harrison's phone titled Evidence (Do Not Open) containing 47 photos. A warrant was issued. The folder contained only sunsets and one blurry photo of what might be a hot dog or possibly a finger. The lead investigator filed a report that said only this was a waste of a warrant. The finger remains under analysis.",
    "Harrison was photographed at a Fourth of July cookout standing in front of a sign reading Burgers Only, Absolutely No Hot Dogs Here, which he had made and installed himself four hours earlier. When asked about the sign, Harrison said it was a tribute. Investigators asked to what. Harrison said freedom. This has been entered into evidence.",
    "The FBI's forensic accounting unit found Harrison has a separate bank account under the name H. Glizzy containing $340 in unexplained deposits made every time a burger was consumed during the competition window. His attorney said this is completely unrelated. Investigators said it is the most related thing they have ever found.",
    "Harrison submitted a notarized affidavit describing hot dog consumption at 34 locations across 6 states. The Commission spent three weeks verifying each location. Thirty-one do not serve hot dogs. Two no longer exist. One is a Wendy's, which Harrison listed as a hot dog restaurant. He underlined it. The underline did not help.",
    "A protected source inside Harrison's household tipped the Commission that Harrison has been referring to all ground beef as training hot dogs and believes this constitutes a legal loophole. The Commission reviewed all weenie law and confirmed there is no such loophole. Harrison responded by asking who the source is. This was also noted.",
    "The FBI tracked late-night calls between Harrison and a contact labeled Beef Friend to a diner 14 miles away. Surveillance observed them over a large pile of cheeseburgers. Harrison said it was a business meeting. Beef Friend said nothing and immediately left. He is also under investigation. His real name is unknown. He paid in cash.",
    "Harrison attempted to enter a 600-word essay titled Why I Am Innocent and Also a Very Good Person into the official record. The Supreme Weenie agreed to add it but noted it would be categorized under Supporting Evidence for the Prosecution. Harrison said that is not what he intended. The Supreme Weenie said she knows.",
    "A retired FBI food crimes analyst described the Harrison case after one hour as the most aggressively documented case of burger consumption she had ever encountered, adding that she did not know this level of planning was possible, and that she needed a moment. She took several moments. The investigation continues.",
    "Commission analysts discovered Harrison's phone autocorrects weenie to burger but autocorrects burger to burger (weenie). Neither Harrison nor his attorney could explain how this happened. A forensic phone examiner spent four days and filed a report that said only this did not happen by accident. It did not happen by accident.",
    "Harrison's gym records show 22 visits each lasting 8 to 12 minutes. A fitness expert testified that no meaningful workout is possible in that time and that the visits are consistent with someone who wanted to create the impression of physical activity without doing any. Harrison said he has very efficient workouts. The expert said no he does not.",
    "The Fraudfurter Division formally requested Harrison be placed on the Weenie Watch List, a designation reserved for individuals whose hot dog activity poses a systemic risk to competitive eating integrity. Harrison's attorney called it an overreach. The Division said it is the minimum appropriate response. The list now has one name on it.",
    "At the conclusion of the most recent hearing, Harrison was asked if he had anything to say to the Commission. He stood up, adjusted his jacket, said I just want everyone to know I really like hot dogs, and sat back down. The room was silent for 17 seconds. His attorney put his head on the table. It has been entered as Exhibit 91: The Statement.",
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
    _sfx  = 'th' if 11 <= _dt_d.day <= 13 else {1:'st',2:'nd',3:'rd'}.get(_dt_d.day % 10, 'th')
    _dk   = f"{_dt_d.strftime('%A %B')}{_dt_d.day}{_sfx}"
    if (_dt_d.month, _dt_d.day) in ((5, 25), (7, 4), (9, 7)): _dk += ' 🇺🇸'
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
# Nick/Harrison logs rotate on the 8am daily force-rebuild — prepend new entry, keep 3
if force_rebuild:
    today_label = today.strftime("%b %-d")  # e.g. "Jun 14"
    for _person, _pool, _var in [
        ("Nick",    NICK_UPDATES,    "NICK_LOG"),
        ("Harrison", HARRISON_UPDATES, "HARRISON_LOG"),
    ]:
        _new_text = random.choice(_pool)
        _m = re.search(rf'{_var}\\s*=\\s*(\\[.*?\\])\\s*#', src, re.DOTALL)
        if _m:
            try:
                _log = eval(_m.group(1))
            except Exception:
                _log = []
            _log = [{"date": today_label, "text": _new_text}] + _log[:2]
            src = re.sub(
                rf'{_var}\\s*=\\s*\\[.*?\\]\\s*#[^\\n]*',
                f'{_var} = {repr(_log)}  # auto-filled by CI: newest first',
                src, flags=re.DOTALL
            )
            print(f"  {_person} log rotated: {today_label}")
        else:
            print(f"  {_person} log pattern not found in build script")

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



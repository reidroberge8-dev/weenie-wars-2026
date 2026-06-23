TOM_UPDATES = [
    "Tom logged three weenies today. The Commission confirmed all three were uncooked, consumed in The Watcher between 11pm and 1am. The Epween File was updated. The archivist was notified. The archivist requested not to be told the new page count. The Commission told her anyway. She sat down.",
    "Forensic thermometer readings at Tom's residence show no hot dog cooking activity in 14 days. His microwave still has the factory protective film on the door. The Commission photographed it. The photo is in the Epween Files under Tab D: Appliances Never Used. It is the most visited tab in the archive.",
    "Commission surveillance confirmed The Watcher was in use for 41 minutes last Tuesday before Tom logged an entry. Agents deployed outside described the apartment as silent during this period except for what one filed as a very focused sound. The sound has not been classified. The sound is in the Epween Files.",
    "The Epween Files were accidentally included in a document batch sent to Tom's dentist. The dentist called the Commission. He said he had assumed the dental wear was from grinding. He now believes it is from what he described as strategic uncooked consumption. He has requested a transfer to a different state.",
    "A visiting researcher asked to see the Epween Files as part of a study on competitive eating documentation. She reviewed Volume 1 only. She emerged 40 minutes later, thanked the Commission, and submitted a formal request to have her memory cleared. It was denied. She has not returned the Commission's calls.",
    "Tom has consumed 100% of his logged weenies without cooking them. Commission dieticians confirmed this is not against the rules, is not something they expected to ever have to say, and have added a proposed amendment to competition guidelines titled simply The Tom Clause.",
    "Witnesses describe The Watcher as a single recliner positioned seven feet from a blank wall in a room with no other furniture. The wall has no artwork. There is one lamp. It faces away from the chair. Tom has denied 14 requests to photograph The Watcher. All 14 denials are in the Epween Files under Tab J: Denials.",
    "The Commission's lead analyst filed a 12-page assessment of The Watcher concluding it is, in their professional opinion, the most intentionally constructed eating environment they have encountered in 30 years. Page 12 ends with a personal note: I think he has been planning this for a long time. The note is underlined.",
    "Tom entered three weenies in a 90-minute window. Surveillance indicates he did not leave The Watcher during this period. A source close to the situation describes the post-Watcher Tom as calm, resolved, and slightly different in a way I cannot explain. The source asked that their name be withheld.",
    "The Epween Files index alone is 23 pages. Tab A: Origin. Tab B: Volume. Tab C: Methods. Tab D: Appliances Never Used. Tab E: The Watcher (preliminary). Tab F: The Watcher (confirmed). Tab G: The Watcher (classified). Tab G is sealed. Only the Supreme Weenie has clearance. She reviewed it once and has not discussed it since.",
    "Tom was asked by a reporter if he had anything to say about The Watcher. He considered this for a long time. He said: it watches back. The reporter submitted the quote and was immediately called by her editor, who asked if she was all right. She said she was fine. She does not seem fine. The quote is in the Epween Files.",
    "Commission toxicologists found that Tom's raw dog consumption style, defined in the official report as temperature-neutral direct intake, leaves no preparation evidence. No plates near a heat source. No cooking smells. The report describes the apartment as a crime scene that committed no crime.",
    "An entry flagged by the High Volume Unit showed Tom logged 11 weenies in a single day. All 11 were uncooked. All 11 were logged from The Watcher between 10pm and 2am. The Commission convened an emergency session and after 90 minutes issued a memo that said only: noted. They considered this the appropriate response.",
    "The Epween Files are now stored in their own room. The room was previously a supply closet. A sign outside reads EPWEEN ARCHIVE — ENTRY BY AUTHORIZATION ONLY. A second sign reads YES, THEY ARE ALL ABOUT ONE PERSON. A third sign below that says PLEASE DO NOT ASK FOLLOW-UP QUESTIONS.",
    "Tom applied to have The Watcher declared a historic site. The application required a description of the site's cultural significance. Tom wrote: it is where it happens. The historic preservation office forwarded it to the Commission. It is now in the Epween Files under Tab R: Things Tom Has Said.",
    "The Commission confirmed Tom does not have a system for choosing when to enter The Watcher. Sources say he simply knows. He described it as environmental awareness. A behavioral analyst reviewed this and filed a report titled The Watcher Awareness Problem, which opens with the sentence: this is not normal.",
    "Forensic analysts recreated Tom's raw dog consumption timeline across the full season and confirmed it is not only consistent but meticulous. The word meticulous appears 14 times in the forensic report. The last instance reads: we are using meticulous because precise is not sufficient and intentional feels like a legal conclusion.",
    "The Commission's thermal imaging team captured The Watcher at 1:04am. The image shows one heat signature in a chair, no heat signatures in the kitchen, and what the technician described as an absolutely still room. The Supreme Weenie reviewed the image once and has not discussed it since.",
    "Tom submitted a formal objection to the phrase raw dog as used in Commission documents, stating he prefers the term ambient temperature consumption. The Commission reviewed the objection and issued a response: they appreciate his input and will continue to use raw dog, as it more precisely describes the situation.",
    "The Epween Files gained another volume this week. Volumes 1 through 6 cover all other 16 competitors combined. Volume 7 is Tom only. Volume 7 is longer than Volumes 1 through 6 combined. The archivist has requested early retirement. The request is pending. Volume 8 has already been started.",
]

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
TIPS_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1qjL8RqvVwbeeiPoMsdeaWllLjQqkTeNbRXW6_LpVlaA/export?format=csv"

OWEN_UPDATES = [
    "Owen has been placed at the center of Chorizogate, a Commission investigation that started as a routine audit and has since expanded to include three subpoenas, two surprise interviews, and a sealed exhibit labeled simply THE SMELL. Owen has 4 weenies on the season. The Commission is not saying the two things are connected. The Commission is clearly connecting the two things.",
    "Chorizogate task force investigators canvassed Owen's neighborhood this week as part of their ongoing inquiry. Neighbors described Owen as quiet, pleasant, and someone who cooks things that do not smell like hot dogs. One neighbor volunteered this information unprompted. The investigator asked the neighbor if she would testify. She said absolutely.",
    "Owen attempted to submit a personal statement to the Chorizogate task force this week clarifying his position on chorizo. The statement was three pages long. Investigators read all three pages. A spokesperson said the statement raised more questions than it answered and specifically asked why page two was almost entirely about chorizo being culturally important.",
    "The Chorizogate task force confirmed a new working theory this week: Owen is not eating hot dogs. The theory has been 47 pages in the making. The task force released a summary. The summary is 12 pages. Page 12 ends with the sentence: we believe the chorizo situation is ongoing. Owen has not commented. His grocery app has.",
    "A forensic food analyst retained by the Commission confirmed this week that residue recovered from Owen's kitchen is inconsistent with hot dog preparation and is instead consistent with, quote, something from the pork family that made a different life choice. Owen's attorney called this inadmissible. The analyst said it is very admissible and offered to bring the residue to court.",
    "Owen filed a motion this week arguing that chorizo is spiritually adjacent to hot dogs and should count toward his total under a doctrine his attorney called meaningful pork proximity. The Commission reviewed the motion for 11 minutes. The denial was written before they finished reviewing it. The motion is now in the file under Tab C: Creative Arguments We Have Denied.",
    "Investigators confirmed Owen has searched the phrase is chorizo a hot dog legally speaking seventeen times across three devices. Owen said he was doing research. The Commission asked research for what. Owen said general curiosity. His attorney leaned over and said something in his ear. Owen said he would like to revise that to no comment.",
    "The Chorizogate investigation turned a corner this week when a source described as credible and also very enthusiastic came forward with new information. The source brought a bag. The bag contained documentation. The documentation contained a receipt, two photos, and a handwritten note that said you are going to want to see this. The Commission did want to see it.",
    "Owen attended a voluntary Commission interview Tuesday. The interview was scheduled for 30 minutes. It ran for two and a half hours. Owen left without answering the last question. The question was: what is in your freezer. Owen said he would have to check. He lives alone. He did not check.",
    "Chorizogate is now the Commission's longest active investigation not involving Nick. Investigators described this as impressive and also exhausting. Owen has logged 4 weenies in the time it has taken the Commission to write Volume 1 of his case file. Volume 1 is 63 pages. The Commission noted the ratio is troubling.",
]


# ── Tip wrapper templates by subject ─────────────────────────────────────────
TIP_WRAPPERS_GENERIC = [
    "{tip}. The Commission convened an emergency session at 9am the following morning. The session was scheduled for 30 minutes. It ran for three hours and forty minutes. A source inside the room said the first hour was mostly silence. The Commission released a statement after. The statement said only that the situation was being monitored. Two commissioners were seen in the parking lot at 6pm, still talking. Neither would comment.",
    "{tip}. When this information reached the Commission, the lead investigator stood up from his chair, walked to the window, and stood there for approximately four minutes without speaking. His assistant asked if he was okay. He said he was fine. He did not seem fine. The tip has been classified as Priority One. The Commission has not previously used Priority One. They created it for this.",
    "{tip}. Three investigators independently submitted written requests for personal leave within 24 hours of reviewing this tip. All three requests cited personal reasons. All three were denied. All three investigators are still on the case. None of them look great.",
    "{tip}. This was submitted to the Hotline at an unspecified hour by a caller who identified themselves only as someone who has been watching. The Commission attempted to follow up. The number was a gas station payphone in a state no one in the Commission has ever visited. The investigator sent to check on it filed a two-page report. Page two is a personal reflection. It has been included in the case file.",
    "{tip}. The Commission read this tip aloud at the weekly briefing. Halfway through the reading, someone at the back of the room said oh no. No one asked who said it. Everyone already felt the same way. The tip has been entered into evidence. It has also been printed and taped to the break room refrigerator. The Commission confirmed this was intentional.",
    "{tip}. Investigators described this as the single most useful tip submitted to the Hotline since its creation. When asked what made it so useful, the lead investigator said it confirmed something we suspected but could not prove and then asked that the recorder be turned off. The recorder was turned off. The conversation continued for 22 minutes.",
]
TIP_WRAPPERS_NICK = [
    "{tip}. Nick was informed that this information had been submitted to the Commission. Nick said he could explain. He was asked to explain. He said he needed a few days. He has been given no days. He is currently working on his explanation with a team he described as consultants. The Commission has subpoenaed the consultants.",
    "{tip}. The Supreme Weenie Commission added this to the Nick file, which is now the second-largest active file in Commission history. Nick's attorney reviewed the addition and filed an objection. The objection was denied. Nick's attorney filed an objection to the denial. That was also denied. The attorney asked to speak to someone more senior. She was already speaking to the most senior person. He showed her the file. She sat down.",
    "{tip}. Commission forensic analysts spent four days cross-referencing this information with existing evidence. On day three, one analyst left the building, bought a sandwich, ate it in the parking lot, and came back in. She said she just needed a moment. The cross-reference was completed on day four. The results are consistent with the Commission's worst suspicions, which were already quite bad.",
    "{tip}. Nick, when reached for comment, said that is not what happened. He was asked what did happen. He said it was complicated. He was told the Commission had time. Nick said he did not have time and had to go. He has not returned the Commission's calls. The Commission has sent twelve follow-up emails. Nick has opened all twelve of them. He has replied to none. This is now part of the investigation.",
]
TIP_WRAPPERS_HARRISON = [
    "{tip}. FBI Fraudfurter Division agents confirmed this is consistent with the bureau's working theory, which they have described as the burger thesis, and which Harrison has described as offensive and also wrong. His refrigerator, which was obtained via subpoena last Tuesday, has so far refused to support either position, though agents say its contents tell a story and that story does not involve hot dogs.",
    "{tip}. Harrison's legal team issued a statement calling the information misleading. The Fraudfurter Division issued a counter-statement calling it accurate. Harrison issued a personal statement calling the whole situation a misunderstanding. The Division issued a response to the personal statement that was eleven pages long and opened with the phrase respectfully, no. Harrison has not responded to the eleven pages. His attorney is reviewing them. She has been reviewing them for five days.",
    "{tip}. The FBI added this to the Fraudfurter dossier, which is now 61 pages. Agents describe page 61 as the most troubling page yet and note that they said the same thing about pages 14, 27, 38, 45, 52, and 58. Harrison was shown the dossier. He looked at the cover. He said he would need his glasses. His glasses were on his face. An agent pointed this out. Harrison said he would need different glasses.",
    "{tip}. A Fraudfurter Division agent described this tip as the smoking gun, paused, and then clarified that he meant the smoking grill, paused again, and said he actually meant the grill that has never been smoked on because that is the problem. The agent filed a formal report. The report is 9 pages. The pun does not appear in the report. The agent confirmed the pun was intentional.",
]
TIP_WRAPPERS_TOM = [
    "{tip}. The Epween Files archivist was notified at 8am. She read the tip. She read it again. She opened a new sub-section in the archive. She labeled it without hesitation, which colleagues described as concerning because she usually deliberates for a long time on labels. The new sub-section is cross-referenced with Tab G. Tab G remains classified. The archivist has Tab G clearance. She has not discussed Tab G since she received clearance. This was three months ago.",
    "{tip}. The High Volume Unit convened immediately and confirmed this is consistent with what they have been monitoring. A unit spokesperson said they were not surprised, which was itself surprising because the tip is extremely surprising. When asked to elaborate, the spokesperson said only that context is everything and context, in this case, is in Tab G. Tab G is still classified. The public has not seen Tab G. Several people who have seen Tab G have requested reassignment.",
    "{tip}. The Commission forwarded this to the Epween Files team with a note that read: you are going to want to see this. The team had already seen it. They had been monitoring the situation for eleven days and were waiting for someone else to notice. They said nothing when it arrived. They simply updated the index. The Epween Files index is now 31 pages. The index covers a single competitor. The Commission confirmed this is unprecedented.",
    "{tip}. Tom was informed that this information had been submitted. Tom said nothing for a long time. An investigator asked if he had anything to say. Tom said: I do what I do in The Watcher and The Watcher does not answer to the Commission. The investigator wrote this down. She wrote it down twice. She submitted it as a formal exhibit. It is Exhibit 112. The Commission held a brief ceremony to mark the 100th exhibit milestone. Tom did not attend the ceremony. This was noted.",
]
TIP_WRAPPERS_OWEN = [
    "{tip}. The Chorizogate task force received this information and immediately scheduled a briefing. The briefing was scheduled for 10am. By 9:50am, four additional investigators had joined voluntarily. By 9:55am, someone had brought donuts, which the lead investigator noted was the most festive a Chorizogate briefing had ever been. The briefing lasted two hours. The donuts were gone in fifteen minutes. Owen was not present. Owen has not been present at any briefing. Owen claims he has not been invited. He has been invited to all of them.",
    "{tip}. Owen's attorney filed an emergency motion to suppress this information on the grounds that it was obtained, quote, in a way that feels wrong. The motion was denied in eight minutes. The task force noted eight minutes was longer than they needed but they wanted to be thorough. Owen asked what his options were. His attorney said limited. Owen asked how limited. His attorney held up a very small amount of space between her index finger and thumb. Owen looked at it for a while.",
    "{tip}. The Chorizogate evidence locker is now at capacity. The task force requested a second evidence locker. The request was approved. The second locker has already been partially filled. A third locker has been pre-authorized. Owen has 4 weenies on the season. The task force has 3 lockers worth of evidence. The task force has not said these two facts are related. They have not said they are unrelated either.",
    "{tip}. Owen, when reached by phone, said he was in the middle of something. He was asked what. He said dinner. He was asked what he was having. There was a very long pause. He said chicken. The investigator noted the pause in the call log. The pause has been added to the file as Exhibit 17: The Hesitation. It is currently the most discussed exhibit among task force members. Owen has not been told about Exhibit 17. The task force agreed telling him would be, quote, too enjoyable to do professionally.",
]

def categorize_tip(tip_text):
    t = tip_text.lower()
    if "nick" in t:
        return "COMMISSION", TIP_WRAPPERS_NICK
    elif "harrison" in t or "fraudfurter" in t or "hamburger" in t or "burger" in t:
        return "FRAUDFURTER", TIP_WRAPPERS_HARRISON
    elif "tom" in t or "epween" in t or "watcher" in t or "raw dog" in t or "ambient" in t:
        return "EPWEEN FILES", TIP_WRAPPERS_TOM
    elif "owen" in t or "chorizo" in t or "chorizogate" in t:
        return "CHORIZOGATE", TIP_WRAPPERS_OWEN
    else:
        return "HOTLINE TIP", TIP_WRAPPERS_GENERIC

def categorize_tip(tip_text):
    t = tip_text.lower()
    if "nick" in t:
        return "COMMISSION", TIP_WRAPPERS_NICK
    elif "harrison" in t or "fraudfurter" in t or "hamburger" in t or "burger" in t:
        return "FRAUDFURTER", TIP_WRAPPERS_HARRISON
    elif "tom" in t or "epween" in t or "watcher" in t or "raw dog" in t or "ambient" in t:
        return "EPWEEN FILES", TIP_WRAPPERS_TOM
    elif "owen" in t or "chorizo" in t or "chorizogate" in t:
        return "CHORIZOGATE", TIP_WRAPPERS_OWEN
    else:
        return "HOTLINE TIP", TIP_WRAPPERS_GENERIC

def categorize_tip(tip_text):
    t = tip_text.lower()
    if 'nick' in t:
        return 'COMMISSION', TIP_WRAPPERS_NICK
    elif 'harrison' in t or 'fraudfurter' in t or 'hamburger' in t or 'burger' in t:
        return 'FRAUDFURTER', TIP_WRAPPERS_HARRISON
    elif 'tom' in t or 'epween' in t or 'watcher' in t or 'raw dog' in t or 'ambient' in t:
        return 'EPWEEN FILES', TIP_WRAPPERS_TOM
    elif 'owen' in t or 'chorizo' in t or 'chorizogate' in t:
        return 'CHORIZOGATE', TIP_WRAPPERS_OWEN
    else:
        return 'HOTLINE TIP', TIP_WRAPPERS_GENERIC

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
    "Nick's security camera showed him entering his kitchen at 3:42am, standing at the counter for six minutes, and returning to bed. No food was prepared. No hot dogs were near the counter. Nick's log shows an entry for 3:42am that same day. The Commission replayed the tape 14 times. The case has been reclassified as fascinating.",
    "Nick's attorney submitted a legal theory arguing that intention to eat a hot dog constitutes a weenie under the doctrine of spiritual consumption. The Commission confirmed it does not. The phrase spiritual consumption will not appear in any official Commission document again. Nick asked if he could still use it personally. The answer was no.",
    "The Commission discovered Nick has a Google Calendar event titled [private] every day at meal times. They obtained a warrant. The events read only: thinking. All 47 of them. Nick said he is a contemplative person. The Commission said this does not help his case. Nick said he knows.",
    "Nick's competitor form listed his eating style as mindful. The Commission asked what that means in the context of hot dogs. Nick said hot dog eating is about presence and intention. The Commission asked if he was eating the hot dogs. Nick said in a real sense, yes. The response was entered as Exhibit 97: Definitional Failure.",
    "The Commission deployed a hot dog proximity sensor, a device invented specifically for this investigation, near Nick's apartment for 30 days. It registered zero readings. Nick said the sensor must be broken. The Commission confirmed it was tested on 400 other apartments with 100% accuracy. Nick said his building has unusual air.",
    "Nick texted a Commission investigator at 11:16pm: I just had one in case you are wondering. The investigator asked for documentation. Nick sent a photo of his ceiling. He said it was artistic. The ceiling has been identified. It is Nick's ceiling. The investigation continues.",
    "Investigators found a receipt in Nick's name from a restaurant called The Frankly Suspicious for a meal described only as the usual. The Commission sent an agent. The address leads to a park. Nick said it is in the park. The park has been surveilled for nine days. There is no restaurant. There is a bench. The bench has been noted.",
    "Nick's therapist submitted an unsolicited letter to the Commission describing their client as preoccupied with documentation, competitive in ways that extend beyond conventional explanation, and deeply invested in being believed. She added she considers this a medical observation. The Commission printed it in 14-point font and framed it.",
    "The Commission asked Nick to consume one hot dog in front of a notary. Nick said he would but needed two weeks to prepare. The Commission said it is a hot dog. Nick said there is a process. The Commission issued a statement saying the phrase there is a process is the most alarming sentence yet spoken in a weenie investigation.",
    "A Commission investigator noted that Nick's apartment has three mirrors all positioned to face the front door and one framed print reading KEEP GOING above the kitchen counter. These observations are in the file under Tab 12: Environmental Indicators. Nick said they are motivational decorations. The investigator filed: possibly.",
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
    "Harrison submitted a sworn statement that he once ate a hot dog at a stadium and remembers it vividly. The Commission verified the stadium. It does not serve hot dogs. It has not served hot dogs since 1994. The Commission has described Harrison as either sincerely confused or a creative writer, and noted both are possible.",
    "Uncle Sam the Glizzy Man arrived at his deposition wearing a tie with a hamburger pattern. His attorney had prepared a statement about it. Harrison said it was a hot dog tie. Three forensic textile analysts confirmed it was a hamburger tie. Harrison stood by the claim for 40 minutes. He eventually said it could go either way.",
    "Harrison submitted a 17-minute voice memo titled My History with Hot Dogs. The Commission transcribed it. The word hot dog appears once, in the sentence I have always respected the hot dog. The remaining 16 minutes concern his feelings about summer, grills as a metaphor, and one extended digression about a burger he had in 2019 that changed him.",
    "Harrison's new attorney submitted a motion to suppress all burger evidence on grounds that it unfairly prejudices the jury against clients who simply, as the motion reads, really enjoy the full range of cylindrical proteins. The Commission read this and scheduled a press conference to read it aloud. Tickets sold out in four hours.",
    "The FBI placed a tracking device on Harrison's most-used spatula. In 30 days it traveled to 11 locations, two of which were hardware stores, four of which were private barbecues, and one which the GPS identified only as beef. The spatula has been named a person of interest. Harrison says that is not legal. The Commission is looking into it.",
    "Harrison's kitchen has a hot dog roller machine still in the original packaging. It was purchased on May 25th, the first day of competition, and has not been opened. Harrison says he is saving it for a special occasion. The Commission asked what occasion. Harrison said he will know when the time is right. This is also in evidence.",
    "The Commission's database entry for Harrison burger consumption spans 14 pages. The entry for all 16 other competitors combined spans two. Harrison's attorney says this is circumstantial. The Commission has given the document its own cover page, title, and table of contents. The table of contents is two pages.",
    "Harrison filed a complaint arguing the Commission is unfairly targeting him based on smell. The Commission's evidence summary includes smell in Section 1 of 47 sections. Harrison's attorney has not read past Section 1. The Commission has offered to summarize. The attorney said he will get to it. He has not gotten to it.",
    "A food safety inspector who visited Harrison's residence noted in her official report that the hot dog storage area was pristine, the burger area was extensively used, and that she found this interesting enough to mention to three different people before writing it down. All three people are now also involved in the investigation.",
    "Harrison's Fraudfurter Division file was accidentally emailed to his landlord during a clerical error. The landlord called the Commission to ask if they needed anything else. He said he had suspected something for a while. He was asked what he suspected. He said: beef. He was thanked for his time. He has been added as a witness.",
]
# ── Headline templates (4 categories, picked 1 each at 8am rebuild) ──────────
BREAKING_TEMPLATES = [
    "{leader} leads Weenie Wars at {leader_total} total — {leader_pct}% of Joey Chestnut's {joey}-dog benchmark. The gap over {second} is {gap}. The Commission describes the situation as active and developing, which is also how they describe the investigation.",
    "League-wide total: {total_weenies} weenies across {n_active} active competitors this season. Joey Chestnut has been informed. He declined to comment and ate something during the briefing. The briefing is being described as one-sided.",
    "{leader} holds first place with {leader_total} weenies, which is {leader_total} more than the {zero_count} competitors who have not logged one. The {zero_count} have been notified. Their responses are pending. The Commission is not waiting up.",
    "OFFICIAL STANDINGS: {leader} ({leader_total}), {second} ({second_total}), and {n_active} others trying. A gap of {gap} separates the top two. This gap has been named. Its name is The Chasm. It is shaped like a hot dog.",
    "{n_active} of {n_players} competitors are on the board. The {zero_count} who are not have been issued a formal reminder that the season is {season_pct}% complete and the weenies are not going to eat themselves. The Commission has confirmed that is not how weenies work.",
    "{leader} is running at {leader_pct}% of Joey Chestnut's benchmark. Joey was briefed. He asked what percentage. They told him. He nodded, said nothing, and went back to eating. The briefing is being described as inconclusive.",
    "The gap between {leader} and {second} stands at {gap} weenie{gap_plural}. The Commission's analysts have been watching this number. It has been described as stubborn, meaningful, and uncomfortable to read aloud at press conferences.",
    "First-place update: {leader} with {leader_total}. Second-place: {second} with {second_total}. The math connecting them is subtraction. The result is {gap}. The Commission reviewed this math and confirmed it is correct and also unflattering for {second}.",
    "The Weenie Wars season is {season_pct}% complete. {leader} leads with {leader_total}. Joey Chestnut's record stands at {joey}. The distance between these two numbers is large. The Commission has described it as aspirational. Players have used other words.",
    "Competitors have collectively consumed {total_weenies} weenies since Memorial Day. At the league average of {league_avg} per active player, Joey Chestnut's {joey}-dog record would require the combined efforts of the entire active field for multiple seasons. Joey was not moved by this analysis.",
]

HOT_TEMPLATES = [
    "{l7_leader} is the hot hand with {l7} weenies in the last 7 days. Extrapolated over the full season, that pace yields {l7_proj} total. {leader} has been briefed. They described the projection as alarming and asked if it could be un-briefed. It could not.",
    "Seven-day leader: {l7_leader} with {l7} entries. The grill is hot, the mustard is flowing, and the rest of the field has been observed checking their phones more than usual. The Commission has noted this pattern.",
    "{l7_leader} — {l7} weenies in seven days. If you are {second} and you are reading this, you should consider eating something. The Commission recommends a hot dog, specifically.",
    "Momentum report: {l7_leader} has the hot hand at {l7} over the last week. At this pace, the overall standings will shift by end of month. {leader}'s camp has declined to project by how much. The Commission estimates: considerably.",
    "PACE ALERT: {l7_leader} with {l7} in the last 7 days has triggered a formal pace review. The review concluded the pace is real, the weenies are documented, and the field should be concerned. Two competitors have purchased hot dogs since receiving the report.",
    "{l7_leader}'s L7 of {l7} represents the most active stretch by any competitor this week. Scientists reviewed this and confirmed it is, quote, a lot of hot dogs in a short period of time. The Commission agrees and has deployed an observer.",
    "A {l7}-weenie week from {l7_leader} has raised the competition temperature. {lagging}, currently at {lagging_total} for the season, was asked for comment. They said they are aware of the situation. They did not say what they plan to do about it.",
    "{l7_leader} with {l7} in 7 days. The projected full-season pace at this rate is {l7_proj} weenies. Joey Chestnut was shown this projection. He made no expression that any witness could describe as impressed.",
    "{l7_leader} has been the most active competitor this week at {l7} entries. The Commission has been watching. The Commission has been timing. The Commission has not said anything yet. This has been described as ominous by at least one competitor.",
    "Hot hand of the week: {l7_leader} with {l7}. {second} with {second_total} total is watching from {gap} back. The Commission released a statement saying the race is very much on. Two players asked them to stop saying that. The statement was reissued.",
]

STANDINGS_TEMPLATES = [
    "{zero_count} competitors have not logged a single weenie. The Commission sent a certified letter to each. Two were delivered. One came back with 'return to sender' written on it in what analysts believe is the handwriting of the recipient. This is being investigated separately.",
    "League average: {league_avg} weenies per active competitor. {leader} is at {leader_total}. The gap between those two numbers is doing a lot of work in this competition.",
    "{lagging} has {lagging_total} weenie{lagging_plural} on the season — a P2J of {lagging_pct}% of Joey Chestnut's benchmark. Joey Chestnut's team has no comment. They expressed no comment with great confidence.",
    "{zero_count} players have not eaten a single official weenie. Their names are on file. Their excuses are also on file. The Commission reviewed the excuses and categorized them as creative, implausible, and in one case simply the word no.",
    "Current standings: {n_active} active competitors and {zero_count} who have yet to begin. The season is {season_pct}% done. The Commission will not say it is too late. They will also not say it is not too late. Both statements are simultaneously true.",
    "The average active competitor has consumed {league_avg} weenies this season. Joey Chestnut's record is {joey} in ten minutes. The Commission is not here to make anyone feel bad about this. They are simply here to note it.",
    "ODDS MOVEMENT: {leader} remains the favorite. {second} is within {gap}. {lagging} at {lagging_total} requires significant commitment between now and Labor Day. The Commission has confirmed this is possible and also very optimistic.",
    "{second} trails {leader} by {gap}. In eating terms, that is {gap} separate events. {second}'s camp says they are not trailing. The Commission says subtraction does not care about camps. The gap is {gap}. It has been confirmed.",
    "SEASON TRACKER: {season_pct}% complete. {n_active} active. {total_weenies} logged. {remaining} more needed for {leader} to match Joey Chestnut. The Commission notes that some of these numbers are more motivating than others.",
    "Field report: of {n_players} competitors, {n_active} are active and {zero_count} have registered no weenies. The {zero_count} have been asked to explain themselves. None have explained themselves. The Commission filed this under ongoing situation.",
]

INVESTIGATION_TEMPLATES = [
    "NICK INVESTIGATION, DAY ONGOING: Nick has {nick_total} entries on file. Each has been reviewed. Each has raised questions. Not all the questions have been answered. The lead investigator describes the situation as the most thoroughly documented confusion in Commission history.",
    "The Harrison case entered a new phase after FBI analysts confirmed the smell coming from Harrison's alleged hot dog preparation area is not a hot dog smell and is instead consistent with either a hamburger or something that spent time near a hamburger and developed feelings about it.",
    "TOM ALERT: Tom's name has appeared on the Epween List, a confidential Commission registry reserved for competitors whose consumption rates exceed statistical plausibility by a margin described as eyebrow-raising. Tom currently has {tom_total} entries. The eyebrow is raised and has not come down.",
    "FOOTLONG LOGS UPDATE: Sources confirm Tom's name appears in the Footlong Logs — a classified internal document tracking single-day consumption events of unusual volume. Tom's {tom_total}-total season has generated multiple entries. Tom has declined to comment on the Footlong Logs, which the Commission notes is exactly what someone on the Footlong Logs would do.",
    "Nick's attorney filed a motion to have {nick_total} entries reviewed under a more lenient standard. The standard was not changed. The motion was denied in 11 minutes, which the Commission noted is their second-fastest denial. Nick asked what the fastest was. The Commission said it was also one of Nick's motions.",
    "Harrison's defense submitted a sworn affidavit stating he has always believed hot dogs to be cylindrical, beef-based, and served in a bun — which investigators confirmed is the definition of a hot dog and also does not explain the 31 Wendy's receipts. Harrison said the receipts are circumstantial. The Commission disagrees.",
    "The Epween List gained a notable entry this week. Tom, whose season total of {tom_total} has drawn scrutiny from the High Volume Unit, was placed under enhanced monitoring. The High Volume Unit described the placement as routine. The placement was not routine. The Commission confirmed the placement was not routine.",
    "FRAUDFURTER DIVISION QUARTERLY UPDATE: Nick — {nick_total} entries under review. Harrison — entries classified irregular. Tom — flagged for Footlong Log entries and Epween List classification. The Division requested additional staff. The request is pending. They are short-staffed and also slightly overwhelmed.",
    "The Commission confirmed Tom is subject to a Footlong Log review after single-day totals triggered an audit under Rule 47-C: Implausible Consumption Events. Tom has {tom_total} weenies on the season. Rule 47-C was written specifically for situations like this, which the Commission says is not an accusation. It is a classification.",
    "Harrison submitted new exculpatory evidence: a gas station receipt for a cylindrical food item dated during the competition window. Forensic analysts confirmed the receipt is real and the station sells both hot dogs and sausages under the same label. Harrison said he ordered the hot dog. The analyst said he cannot confirm that from a receipt. Harrison said that is the point of a receipt.",
    "An anonymous tip alleged Nick keeps a second log under the alias W. Glizzy. The Commission investigated for three weeks. W. Glizzy has not been located. Nick says he has no idea who that is. Nick paused for two seconds before saying it. The two seconds have been entered into evidence.",
    "EPWEEN LIST STATUS: Tom remains on the list. Harrison remains on a separate classification. Nick is under standard review. All three cases are active. The lead investigator described the combined caseload as unprecedented, exhausting, and honestly kind of impressive.",
    "Tom has not cooked a hot dog this season. Commission thermal imaging confirmed it. Two witnesses described watching him eat and feeling an emotion they could not name. The High Volume Unit added a new classification to their tracking system. The classification is called The Tom. It applies to one person.",
    "Sources confirm Tom enters The Watcher between one and four times per week. He has never invited anyone to The Watcher. He has never described The Watcher. The Commission has 94 pages on The Watcher. The Supreme Weenie reviewed them and issued one instruction: keep watching The Watcher.",
    "Tom's Epween File is the largest single-subject file in Commission history. It surpassed the previous record last month. The Commission would not confirm details about the previous record holder. They said only: that case was simpler. Tom's attorney said his client is honored. The Commission said that is not the right word.",
    "An anonymous tip described Tom's raw dog method as ritualistic, sequential, and conducted with the energy of someone completing a form they have filled out many times before. The tip was seven pages long. The Commission read all of it. They called the tipster and asked one question: are you OK? The tipster said yes. Their voice suggested otherwise.",
    "The Epween Files reached a new milestone this week. The Commission held a brief ceremony. There was no cake. There was a file transfer to a larger server and a moment of silence that lasted longer than intended. Tom was not informed. Tom was in The Watcher.",
]


today      = datetime.now()  # defined here so cache-bust and all downstream code can use it

# ── Fetch CSV ─────────────────────────────────────────────────────────────────
print("Fetching sheet...")
raw_csv = urllib.request.urlopen(SHEET_CSV + f"&_={int(today.timestamp())}").read()  # cache-bust
csv_hash = hashlib.sha256(raw_csv).hexdigest()
rows = list(csv.DictReader(io.StringIO(raw_csv.decode("utf-8"))))
print(f"  {len(rows)} entries | hash={csv_hash[:12]}...")

# ── Fetch tips sheet ──────────────────────────────────────────────────────────
try:
    tips_req = urllib.request.Request(TIPS_SHEET_CSV, headers={"User-Agent": "Mozilla/5.0"})
    raw_tips = urllib.request.urlopen(tips_req, timeout=15).read()
    tip_rows = list(csv.reader(io.StringIO(raw_tips.decode("utf-8"))))
    tip_data  = [r for r in tip_rows[1:] if r and r[0].strip() and len(r) >= 2]
    tips_hash = hashlib.sha256(raw_tips).hexdigest()
    print(f"  Tips sheet: {len(tip_data)} tips | hash={tips_hash[:12]}...")
except Exception as _e:
    print(f"  Tips sheet fetch failed: {_e}")
    tip_data = []
    tips_hash = last_state.get("tips_hash", "")



# ── Change detection ──────────────────────────────────────────────────────────
last_state = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        last_state = json.load(f)

last_hash      = last_state.get("csv_hash", "")
prev_odds_data = last_state.get("odds", {})  # for move direction
current_odds   = {}  # populated during player update loop
today_date     = today.strftime("%Y-%m-%d")

scores_changed = csv_hash != last_hash

last_tips_hash   = last_state.get("tips_hash", "")
last_tip_ts_str  = last_state.get("last_tip_ts", "")
last_fallback_ts_str = last_state.get("last_fallback_ts", "")
tips_changed     = tips_hash != last_tips_hash and bool(tip_data)
last_tip_dt      = datetime.fromisoformat(last_tip_ts_str) if last_tip_ts_str else None
last_fallback_dt = datetime.fromisoformat(last_fallback_ts_str) if last_fallback_ts_str else None
no_tip_24h       = (last_tip_dt is None) or ((today - last_tip_dt.replace(tzinfo=None)) > timedelta(hours=24))
no_fallback_24h  = (last_fallback_dt is None) or ((today - last_fallback_dt.replace(tzinfo=None)) > timedelta(hours=24))
need_fallback    = no_tip_24h and no_fallback_24h
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

if not scores_changed and not force_rebuild and not scores_stale and not tips_changed and not need_fallback:
    print("No new entries, scores current — skipping.")
    sys.exit(0)

if scores_changed:
    print(f"  Score change detected ({last_hash[:12] if last_hash else 'none'} → {csv_hash[:12]}) — full update.")
elif scores_stale:
    print("  Scores out of sync with sheet — resyncing.")
elif tips_changed:
    print(f"  New tips detected ({last_tips_hash[:12] if last_tips_hash else 'none'} → {tips_hash[:12]}) — headline update.")
elif need_fallback:
    print("  No tips in 24h — generating fallback story.")
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

def _odds_prob(odds_str):
    """Convert American odds string to implied probability (higher = better)."""
    try:
        o = int(str(odds_str).replace("+",""))
        return -100 / o if o < 0 else 100 / (o + 100)
    except: return 0.0


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
    current_odds[name] = oddsv
    prev_oddsv = prev_odds_data.get(name, oddsv)
    if   _odds_prob(oddsv) > _odds_prob(prev_oddsv): movev, mcv = "\u25bc", "#2a7a2a"
    elif _odds_prob(oddsv) < _odds_prob(prev_oddsv): movev, mcv = "\u25b2", "#B22234"
    else:                                             movev, mcv = "\u2014", "#7a8aaa"
    pattern = (
        rf'("name":"{name}"[^{{}}]*?"total":)\d+'
        rf'(,"may":)\d+(,"june":)\d+(,"july":)\d+(,"aug":)\d+(,"sep":)\d+'
        rf'(,"l7":)\d+(,\s*"chomp":)\s*\d+(,\s*"odds":"[^"]*")'
        r',\s*"move":"[^"]*",\s*"mc":"[^"]*"'
    )
    repl = rf'\g<1>{t}\g<2>{may}\g<3>{june}\g<4>{july}\g<5>{aug}\g<6>{sep}\g<7>{l7v}\g<8>{chmp},"odds":"{oddsv}","move":"{movev}","mc":"{mcv}"'
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
today_label = today.strftime("%b %-d")  # e.g. "Jun 14"

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

# ── Update TIPS_HEADLINES in build script ────────────────────────────────────
_tips_match = re.search(r'TIPS_HEADLINES\s*=\s*(\[.*?\])\s*#', src, re.DOTALL)
_current_tips = []
if _tips_match:
    try:
        _current_tips = eval(_tips_match.group(1))
    except Exception:
        _current_tips = []

if tips_changed and tip_data:
    # Build headline for each new tip (ones not already in current list)
    _seen_raw = {t.get("tip_raw", "") for t in _current_tips}
    _new_stories = []
    for _row in tip_data:
        _tip_ts_raw  = _row[0].strip()
        _tip_text    = _row[1].strip() if len(_row) > 1 else ""
        if not _tip_text or _tip_text in _seen_raw:
            continue
        _cat, _wrappers = categorize_tip(_tip_text)
        _story = random.choice(_wrappers).format(tip=_tip_text)
        try:
            _tip_dt    = datetime.strptime(_tip_ts_raw, "%m/%d/%Y %H:%M:%S")
            _tip_label = _tip_dt.strftime("%b %-d")
        except Exception:
            _tip_label = today_label
        _new_stories.append({"date": _tip_label, "category": _cat, "text": _story, "tip_raw": _tip_text})
        _seen_raw.add(_tip_text)
    if _new_stories:
        _current_tips = list(reversed(_new_stories)) + _current_tips
        _current_tips = _current_tips[:5]
        last_state["last_tip_ts"] = today.isoformat()
        print(f"  TIPS_HEADLINES: {len(_new_stories)} new tip story/stories added")

elif need_fallback:
    random.seed(int(hashlib.md5(today_label.encode()).hexdigest()[:8], 16))
    _fallback_subjects = [
        ("COMMISSION",   NICK_UPDATES),
        ("FRAUDFURTER",  HARRISON_UPDATES),
        ("EPWEEN FILES", TOM_UPDATES),
        ("CHORIZOGATE",  OWEN_UPDATES),
    ]
    _f_cat, _f_pool = random.choice(_fallback_subjects)
    _f_text = random.choice(_f_pool)
    _current_tips = [{"date": today_label, "category": _f_cat, "text": _f_text}] + _current_tips[:4]
    last_state["last_fallback_ts"] = today.isoformat()
    print(f"  TIPS_HEADLINES: fallback story added ({_f_cat})")

src = re.sub(
    r'TIPS_HEADLINES\s*=\s*\[.*?\]\s*#[^\n]*',
    f'TIPS_HEADLINES = {repr(_current_tips)}  # auto-filled by CI: newest first',
    src, flags=re.DOTALL
)

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
    if current_odds:
        _state_out["odds"] = current_odds
    _state_out["tips_hash"]         = tips_hash
    _state_out["tips_row_count"]    = len(tip_data)
    _state_out["last_tip_ts"]       = last_state.get("last_tip_ts", "")
    _state_out["last_fallback_ts"]  = last_state.get("last_fallback_ts", "")
    json.dump(_state_out, f, indent=2)

subprocess.run(["git", "config", "user.name",  "github-actions[bot]"], cwd=ROOT)
subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], cwd=ROOT)
subprocess.run(["git", "add", "last_seen.json", "build_weenie_wars_widget.py"], cwd=ROOT)
result = subprocess.run(["git", "commit", "-m", f"Auto-update {today.strftime('%Y-%m-%d %H:%M')} UTC"], cwd=ROOT, capture_output=True, text=True)
if result.returncode == 0:
    subprocess.run(["git", "push"], cwd=ROOT)
    print("State committed.")



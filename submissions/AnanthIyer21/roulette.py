#!/usr/bin/env python3
"""Git Roulette: whack() decides the fate of every commit and push you make.

    python3 roulette.py install [repo]     # hook your repo up to fate
    python3 roulette.py uninstall [repo]   # restore your old hooks
    python3 roulette.py story [repo]       # read the saga of your struggle

Standard library only. Harmless: it only touches .git/hooks and .git/roulette
of the repo you install it into, and every hook fails open.
"""
import json
import os
import random
import shutil
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS = ("commit-msg", "pre-push")
MARK = "# git-roulette hook"

# ---------------------------------------------------------------- fates
FATES = {
    "SHIPPED":   ["push", "deploy", "prod", "merge", "commit"],
    "CONFLICT":  ["conflict"],
    "GOOSE":     ["goose", "honk"],
    "DUCK":      ["duck", "quack", "rubber"],
    "SLEEP":     ["sleep", "midnight"],
    "SEGFAULT":  ["segfault", "null", "pointer", "stack", "overflow", "bug"],
    "INCIDENT":  ["incident", "io"],
    "WIFI":      ["wifi"],
    "FUEL":      ["pizza", "coffee"],
    "GLORY":     ["prize", "demo", "pitch"],
    "SPONSORED": ["marshall", "wace", "brevan", "howard", "capital", "one", "bloomberg", "netcraft"],
    "CHAOS":     ["whack", "hack", "feature", "warwick", "oculus", "compsoc", "semicolon"],
}
WORD_FATE = {w: f for f, ws in FATES.items() for w in ws}
TITLES = {
    "SHIPPED": "SHIPPED", "CONFLICT": "MERGE CONFLICT", "GOOSE": "GOOSE ATTACK",
    "DUCK": "RUBBER DUCK TRIBUNAL", "SLEEP": "FELL ASLEEP", "SEGFAULT": "SEGFAULT",
    "INCIDENT": "INCIDENT DECLARED", "WIFI": "WIFI DOWN", "FUEL": "REFUELLED",
    "GLORY": "GLORY", "SPONSORED": "SPONSORED", "CHAOS": "CHAOS",
}
COLOURS = {
    "SHIPPED": "32", "CONFLICT": "31", "GOOSE": "37", "DUCK": "33", "SLEEP": "34",
    "SEGFAULT": "91", "INCIDENT": "95", "WIFI": "31", "FUEL": "93", "GLORY": "96",
    "SPONSORED": "36", "CHAOS": "35",
}

ART = {
    "SHIPPED": r"""
      |
     / \
    / _ \
   | (_) |
   |     |
  /|  |  |\
 /_|__|__|_\
    /_\/_\
   ~~~~~~~~""",
    "CONFLICT": r"""
 <<<<<<< HEAD
   your hopes
 =======
   a goose
 >>>>>>> soul""",
    "GOOSE": r"""
        __
     __( o)>   HONK
     \ <_ )
      `---'
   ___/  \___""",
    "DUCK": r"""
       __
     <(o )___
      ( ._> /
       `---'   quack?""",
    "SLEEP": r"""
     z Z z
   .-----.
  ( -   - )
  (   o   )
   `-----'""",
    "SEGFAULT": r"""
    \ | / BOOM
  -- \|/ --
  --  *  --
    / | \
  core dumped""",
    "INCIDENT": r"""
   .--------.
   | !!!!!! |
   |  INC   |
   | ALERT  |
   '--------'
    WEE WOO""",
    "WIFI": r"""
    .-----.
   /  ...  \
     /   \
       x
  Oculus-Guest
  (no internet)""",
    "FUEL": r"""
    ________
    \  o  o/
     \ o  /    ( (
      \  /    .----.
       \/     |    |]
              `----'""",
    "GLORY": r"""
    ___________
   '._==_==_=_.'
   .-\:      /-.
  | (|:.     |) |
   '-|:.     |-'
     \::.    /
      '::. .'
        ) (
      _.' '._""",
    "SPONSORED": r"""
  +--------------+
  | $$$ DEAL $$$ |
  |  ^  /\  ^    |
  |   \/  \/ \/  |
  +--------------+""",
    "CHAOS": r"""
   ?!  ;  ?!
  ( @ _ @ )
   /|   |\
    ;  ;  ;""",
}

SPONSOR_LINES = {
    "marshall": "MARSHALL WACE goes long on your commit, citing 'strong vibes'",
    "wace": "MARSHALL WACE quant model buys your commit at 3.2x book value",
    "brevan": "BREVAN HOWARD hedges your commit against the next merge conflict",
    "howard": "BREVAN HOWARD macro desk: 'this commit is the trade of the decade'",
    "capital": "CAPITAL ONE approves your commit for a 0% APR credit line",
    "one": "CAPITAL ONE: 'what's in your commit?' Answer: questionable code",
    "bloomberg": "BLOOMBERG TERMINAL: COMMIT +420% INTRADAY, ANALYSTS BAFFLED",
    "netcraft": "NETCRAFT scans your commit, finds zero phishing, one goose",
}
CHAOS_LINES = {
    "semicolon": "A rogue semicolon has been appended to your message;",
    "feature": "Your bug has been officially rebranded as a feature.",
    "whack": "The function has whacked your commit. It is now WHACKED.",
    "hack": "Your commit has been hacked. Mostly it is just louder now.",
    "warwick": "Your commit now has a Warwick campus parking permit.",
    "oculus": "Your commit got lost somewhere in the Oculus building.",
    "compsoc": "CompSoc has claimed this commit for the society archives.",
}

# Jackpots: when the top two fates of a roll form a known pair, they combine.
COMBOS = {
    frozenset(["GOOSE", "DUCK"]): "BIRD FIGHT",
    frozenset(["FUEL", "SLEEP"]): "LATE NIGHT SLICE",
    frozenset(["SPONSORED", "GLORY"]): "HOSTILE TAKEOVER",
    frozenset(["WIFI", "INCIDENT"]): "TOTAL OUTAGE",
    frozenset(["SEGFAULT", "CONFLICT"]): "CORRUPTED",
    frozenset(["CHAOS", "SHIPPED"]): "YOLO DEPLOY",
}
COMBO_BLOCKS = {"BIRD FIGHT", "TOTAL OUTAGE", "CORRUPTED"}
TITLES.update({c_: c_ for c_ in COMBOS.values()})
COLOURS.update({"BIRD FIGHT": "1;33", "LATE NIGHT SLICE": "93", "HOSTILE TAKEOVER": "1;36",
                "TOTAL OUTAGE": "1;31", "CORRUPTED": "1;91", "YOLO DEPLOY": "1;35"})
ART.update({
    "BIRD FIGHT": r"""
       __                  __
    __( o)>  HONK  vs  <(o )___
    \ <_ )   *POW*      ( ._> /
     `---'   *BAM*       `---'
         J A C K P O T""",
    "LATE NIGHT SLICE": r"""
       z Z      ________
     (-.-)      \  o  o/
     /|🍕|\       \ o  /
      / \         \/
         J A C K P O T""",
    "HOSTILE TAKEOVER": r"""
   $$$ [SPONSOR] ===> [YOUR REPO] $$$
        _____
       |=====|   SOLD
       | $$$ |   to the highest bidder
         J A C K P O T""",
    "TOTAL OUTAGE": r"""
   (wifi)  x_x     INC-0000  SEV0
     |              everything is on fire
   [router]  ~~~ smoke ~~~
         J A C K P O T""",
    "CORRUPTED": r"""
   <<<<<<< HEAD
   Segmentation f@#lt (c%re d&mped)
   >>>>>>> \x00\x00\x00\x00
         J A C K P O T""",
    "YOLO DEPLOY": r"""
      |    friday 23:59
     /_\   no tests
    |YOLO|  no review
    |____|  straight to prod
     /\/\
         J A C K P O T""",
})

# Things fate says when the drama is APOCALYPTIC.
ESCALATION = {
    "SHIPPED": "Your commit has been deployed to prod, staging, the moon and your nan's laptop.",
    "CONFLICT": "The conflict has escalated to the UN Security Council.",
    "GOOSE": "The goose has retained a solicitor and is suing you for emotional damages.",
    "DUCK": "The rubber ducks have unionised and are demanding better explanations.",
    "SLEEP": "You have slept through the closing ceremony. And the next WHACK.",
    "SEGFAULT": "The segfault has spread to the kernel. The kernel says hi.",
    "INCIDENT": "The incident has its own incident. It is incidents all the way down.",
    "WIFI": "The Oculus wifi has achieved sentience and chosen violence.",
    "FUEL": "You have consumed 14 pizzas. The Oculus vending machine is filing for bankruptcy.",
    "GLORY": "The judges have renamed the mini projector after you.",
    "SPONSORED": "BLOOMBERG HAS HALTED ALL TRADING ON YOUR REPO.",
    "CHAOS": "Chaos has become self-aware. It would like a word.",
}
DEV_PAIN = [
    "Stack Overflow has closed your commit as a duplicate.",
    "git blame now points at you. It always did.",
    "Someone in the next room just typed git push --force.",
    "It works on fate's machine.",
    "Your node_modules folder just gained 3GB and sentience.",
    "A senior engineer somewhere sighed and didn't know why.",
    "The CI pipeline has gone home for the night.",
    "This commit has 0 tests and 100% confidence.",
]
DUCK_QUESTIONS = [
    ("Did you test it?", ["yes", "yeah", "yep", "ofc", "of course", "obviously", "i did"],
     "LIAR. Nobody tests at a hackathon."),
    ("Why does this change exist?", ["idk", "dunno", "because", "vibes", "why not"],
     "'Vibes' is not a design document."),
    ("What does this change actually do?", ["stuff", "things", "it works", "fixes it", "idk"],
     "'Stuff' is not a feature."),
    ("Would you show this code to your mum?", ["yes", "no", "maybe", "lol"],
     "Wrong answer. There was no right answer."),
    ("Explain it like I'm a duck.", ["quack", "idk", "no"],
     "Do not quack at the duck."),
]
WEAK = ["idk", "trust me", "it works", "dunno", "yes", "no", "asdf", "lol", "quack", "stuff"]
SYLLABLES = {
    "whack": 1, "hack": 1, "duck": 1, "quack": 1, "goose": 1, "honk": 1, "bug": 1, "feature": 2,
    "warwick": 2, "oculus": 3, "compsoc": 2, "marshall": 2, "wace": 1, "brevan": 2, "howard": 2,
    "capital": 3, "one": 1, "bloomberg": 2, "netcraft": 2, "incident": 3, "io": 2, "pizza": 2,
    "coffee": 2, "sleep": 1, "deploy": 2, "merge": 1, "conflict": 2, "commit": 2, "push": 1,
    "prod": 1, "segfault": 2, "null": 1, "pointer": 2, "stack": 1, "overflow": 3, "semicolon": 4,
    "rubber": 2, "demo": 2, "pitch": 1, "prize": 1, "midnight": 2, "wifi": 2,
}
ACHIEVEMENTS = {
    "goose_whisperer": ("Goose Whisperer", "met 3 geese"),
    "thrice_denied": ("Thrice Denied", "blocked 3 times in a row"),
    "apocalypse": ("Apocalypse Survivor", "got through an APOCALYPTIC roll"),
    "midnight": ("Midnight Committer", "committed between 23:45 and 04:00"),
    "jackpot": ("JACKPOT!", "hit a combo"),
    "hot_hand": ("Hot Hand", "3 lucky rolls in a row"),
    "duck_debugger": ("Duck Debugger", "convinced the rubber duck"),
    "fake_death": ("Fake Death", "survived a fake segfault"),
    "incident_commander": ("Incident Commander", "led 2 incidents"),
    "robbed": ("Robbed", "had a commit stolen by a goose"),
    "poet": ("Accidental Poet", "got a whack() haiku in a commit"),
    "roasted": ("Well Done", "got your commit message roasted 3 times"),
}


# ---------------------------------------------------------------- output
def _tty(stream):
    try:
        return stream.isatty()
    except Exception:
        return False


OUT = sys.stderr
COLOR = (os.environ.get("ROULETTE_FORCE_COLOR") == "1"
         or (_tty(OUT) and "NO_COLOR" not in os.environ))
ANIMATE = ((_tty(OUT) or os.environ.get("ROULETTE_FORCE_ANIM") == "1")
           and os.environ.get("ROULETTE_NO_ANIM") != "1")


def _sleep(seconds):  # ROULETTE_FAST=1 keeps the animation frames but skips the waiting (for GIFs)
    if os.environ.get("ROULETTE_FAST") != "1":
        time.sleep(seconds)


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if COLOR else text


def say(text=""):
    print(text, file=OUT, flush=True)


def nap(seconds):
    if ANIMATE:
        _sleep(seconds)


# ---------------------------------------------------------------- the roll
def roll(rdir, hot=False):
    """Call whack() inside .git/roulette so the fate file lives there."""
    seed = os.environ.get("ROULETTE_SEED")
    if seed is not None:
        state_file = os.path.join(rdir, "seedcount")
        try:
            n = int(open(state_file).read())
        except Exception:
            n = 0
        open(state_file, "w").write(str(n + 1))
        random.seed(f"{seed}-{n}")
    sys.path.insert(0, rdir if os.path.exists(os.path.join(rdir, "whack.py")) else HERE)
    from whack import whack
    cwd = os.getcwd()
    os.chdir(rdir)
    try:
        words = whack()
        if hot:  # HOT HAND: fate rolls twice
            words = words + whack()
    finally:
        os.chdir(cwd)
    counts = Counter(words)
    # A fate's score is how many of its words were rolled, averaged per word, so the
    # lonely one-word fates (conflict, wifi) can beat the eight-sponsor lobby.
    scores = {f: sum(counts[w] for w in ws) / len(ws) for f, ws in FATES.items()}
    ranked = sorted(scores, key=lambda f: (scores[f], random.random()), reverse=True)
    fate = ranked[0]
    pair = frozenset(ranked[:2])
    if scores[ranked[1]] > 0 and pair in COMBOS:
        fate = COMBOS[pair]
    n = len(words)
    drama = "MILD" if n <= 20 else "DRAMATIC" if n <= 60 else "APOCALYPTIC"
    return words, counts, fate, drama


def spin(words, fate):
    """Fruit machine: words whizz past, slow down, land on the fate."""
    if not ANIMATE:
        return
    reel = list(words) * (1 + 24 // max(1, len(words)))
    random.shuffle(reel)
    delay, total = 0.02, 0.0
    for w in reel[:24]:
        line = f"  [ {w.upper():^11} ]  [ {random.choice(list(FATES)):^11} ]"
        OUT.write("\r" + c(line, "1;" + random.choice(list(COLOURS.values()))))
        OUT.flush()
        _sleep(delay)
        total += delay
        delay *= 1.17
        if total > 1.8:
            break
    land = f"  [ {'*' * 11} ]  [ {fate:^11} ]"
    OUT.write("\r" + c(land, "1;" + COLOURS[fate]) + "\n")
    OUT.flush()
    _sleep(0.3)


def show_art(fate, drama):
    art = ART[fate].strip("\n")
    if drama == "APOCALYPTIC":
        art = "\n".join("".join(ch * 2 for ch in line) for line in art.splitlines())
    banner = TITLES[fate]
    if drama == "DRAMATIC":
        banner = f"!! {banner} !!"
    elif drama == "APOCALYPTIC":
        banner = f"!!!!! {' '.join(banner)} !!!!!"
    say(c(art, COLOURS[fate]))
    say(c(f"  >>> {banner} <<<", "1;" + COLOURS[fate]))


def stats_strip(words, counts, fate, drama):
    fw = Counter({w: counts[w] for w in FATES.get(fate, []) if counts[w]})
    top = fw.most_common(1)[0] if fw else counts.most_common(1)[0]
    dcol = {"MILD": "32", "DRAMATIC": "33", "APOCALYPTIC": "1;31"}[drama]
    return (c(f"whack() rolled {len(words)} words", "2") + " | "
            + c(f"{top[0]} x{top[1]}", COLOURS[fate]) + " | "
            + c(f"drama: {drama}", dcol))


# ---------------------------------------------------------------- helpers
def git_dir(path="."):
    out = subprocess.run(["git", "-C", path, "rev-parse", "--absolute-git-dir"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"git-roulette: {path} is not a git repo")
    return out.stdout.strip()


def ask_tty(prompt):
    if os.environ.get("ROULETTE_NONINTERACTIVE") == "1":
        ans = random.choice(os.environ.get("ROULETTE_DUCK_ANSWER", "").split("|"))
        say(c(prompt, "33") + ans)
        return ans
    try:
        with open("/dev/tty") as tty_in, open("/dev/tty", "w") as tty_out:
            tty_out.write(prompt)
            tty_out.flush()
            return tty_in.readline().strip()
    except OSError:
        ans = random.choice(os.environ.get("ROULETTE_DUCK_ANSWER", "").split("|"))
        say(c(prompt, "33") + ans + c("  (no tty, the duck reads your mind)", "2"))
        return ans


def log(rdir, entry):
    with open(os.path.join(rdir, "log.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_log(rdir):
    try:
        with open(os.path.join(rdir, "log.jsonl"), encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except FileNotFoundError:
        return []


# ---------------------------------------------------------------- hooks
def react_commit(fate, drama, counts, msg):
    """Returns (allowed, new_message, extra) for a commit."""
    big = {"MILD": 1, "DRAMATIC": 2, "APOCALYPTIC": 3}[drama]
    if fate == "SHIPPED":
        say(c("  " + "🎉 " * big + "Commit approved by the fates. Ship it!", "1;32"))
        return True, msg, {}
    if fate == "CONFLICT":
        say(c("  BLOCKED: a goose has caused a merge conflict in your soul.", "1;31"))
        say(c("  Resolve your inner conflict and try again.", "31"))
        return False, msg, {}
    if fate == "GOOSE":
        if random.random() < 0.35:
            say(c("  BLOCKED: the goose has STOLEN your commit and run off into the night.", "1;31"))
            say(c("  It left a ransom note:", "37"))
            say(c("    " + ransom_note(counts), "1;37"))
            return False, msg, {"stolen": True}
        say(c("  A goose has seized your commit message. HONK.", "1;37"))
        return True, f"HONK HONK (originally: {msg})", {"honk": True}
    if fate == "DUCK":
        q, bad, burn = random.choice(DUCK_QUESTIONS)
        say(c("  The rubber duck stares at you. It has one question:", "33"))
        say(c(f"  🦆 \"{q}\"", "1;33"))
        ans = ask_tty("  🦆 > ")
        low = ans.strip().lower().rstrip(".!")
        if low in bad or any(low == b or low.startswith(b + " ") for b in bad):
            say(c(f"  BLOCKED: {burn}", "1;31"))
            return False, msg, {"duck": ans, "duck_q": q}
        if len(low) < 15 or low in WEAK:
            say(c("  BLOCKED: the duck is unconvinced. Quack quack (that's a no). Use your words.", "1;31"))
            return False, msg, {"duck": ans, "duck_q": q}
        say(c("  The duck nods slowly. Quack. Commit allowed.", "1;33"))
        return True, msg, {"duck": ans, "duck_q": q}
    if fate == "BIRD FIGHT":
        say(c("  JACKPOT: the goose and the duck both claimed your commit. They are fighting.", "1;33"))
        say(c("  Feathers everywhere. Nobody wins, least of all you. BLOCKED.", "1;31"))
        return False, msg, {}
    if fate == "TOTAL OUTAGE":
        inc = f"INC-{random.randint(1000, 9999)}"
        say(c(f"  JACKPOT: the wifi died AND incident.io opened {inc} (SEV0). Total outage. BLOCKED.", "1;31"))
        return False, msg, {"incident": inc, "sev": "SEV0"}
    if fate == "CORRUPTED":
        say(c("  JACKPOT: segfault inside a merge conflict. Your commit is now 40% \\x00. BLOCKED.", "1;91"))
        return False, msg, {}
    if fate == "LATE NIGHT SLICE":
        say(c("  JACKPOT: you fell asleep face-first in a pizza. The commit went through with you.", "1;93"))
        return True, msg + " (written face-down in a pizza)", {}
    if fate == "HOSTILE TAKEOVER":
        buyers = [w.upper() for w in FATES["SPONSORED"] if counts[w]][:3] or ["BLOOMBERG"]
        say(c(f"  JACKPOT: {' + '.join(buyers)} launched a hostile takeover of your commit.", "1;36"))
        return True, f"[ACQUIRED BY {' & '.join(buyers)}] {msg}", {"headline": "hostile takeover by " + ", ".join(buyers)}
    if fate == "YOLO DEPLOY":
        say(c("  JACKPOT: no tests, no review, straight to prod. Godspeed.", "1;35"))
        return True, msg.upper() + " (YOLO)", {}
    if fate == "SLEEP":
        secs = {"MILD": 1.2, "DRAMATIC": 2.5, "APOCALYPTIC": 4.5}[drama]
        say(c("  You have fallen asleep on the keyboard...", "34"))
        if ANIMATE:
            t = 0.0
            while t < secs:
                OUT.write(c(random.choice(["z", "Z", "zz", "Zz"]) + " ", "34"))
                OUT.flush()
                _sleep(0.3)
                t += 0.3
            OUT.write("\n")
        else:
            say(c("  zzz Zzz zZzZ", "34"))
        say(c("  *snort* ...huh? Oh. Committed. Sure.", "34"))
        return True, msg, {}
    if fate == "SEGFAULT":
        say(c("  Segmentation fault (core dumped)", "1;91"))
        frames = random.randint(3, 3 + 2 * big)
        for i in range(frames):
            addr = random.randint(0x7f0000000000, 0x7fffffffffff)
            fn = random.choice(["git_commit_tree", "hackathon_main", "caffeine_alloc",
                                "goose_dispatch", "duck_debug", "sleep_deprivation"])
            say(c(f"    #{i} 0x{addr:012x} in {fn} () at brain.c:{random.randint(1, 999)}", "91"))
        nap(0.8 * big)
        say(c("  ...just kidding. Your commit is fine. Probably.", "1;32"))
        return True, msg, {}
    if fate == "INCIDENT":
        inc = f"INC-{random.randint(1000, 9999)}"
        sev = {"MILD": "SEV3", "DRAMATIC": "SEV2", "APOCALYPTIC": "SEV1"}[drama]
        say(c(f"  incident.io: {inc} declared ({sev}) 'someone committed at a hackathon'", "1;95"))
        say(c(f"  Lead: you. Status: investigating. Root cause: probably you.", "95"))
        return True, f"{msg} [{inc}]", {"incident": inc, "sev": sev}
    if fate == "WIFI":
        say(c("  BLOCKED: the Oculus wifi has died. Your commit is buffering.", "1;31"))
        say(c("  Try turning it off and on again (i.e. try again).", "31"))
        return False, msg, {}
    if fate == "FUEL":
        food = max(["pizza", "coffee"], key=lambda w: counts[w])
        say(c(f"  Powered by {food}. You are unstoppable. Commit accepted.", "1;93"))
        return True, msg, {}
    if fate == "GLORY":
        say(c("  THIS COMMIT WINS THE HACKATHON. The judges are weeping. The projector is yours.", "1;96"))
        return True, msg, {}
    if fate == "SPONSORED":
        sw = max(FATES["SPONSORED"], key=lambda w: counts[w])
        headline = SPONSOR_LINES[sw]
        say(c(f"  ┌ BREAKING ─ {headline}", "1;36"))
        return True, msg, {"headline": headline}
    if fate == "CHAOS":
        cw = max(FATES["CHAOS"], key=lambda w: counts[w])
        say(c("  " + CHAOS_LINES[cw], "1;35"))
        new = msg
        if cw == "semicolon":
            new = msg + ";"
        elif cw == "feature":
            new = msg.replace("bug", "feature").replace("fix", "embrace") + " (it's a feature)"
        elif cw == "whack":
            new = "WHACKED: " + msg
        elif cw == "hack":
            new = msg.upper()
        return True, new, {"chaos": cw}
    return True, msg, {}


def react_push(fate, drama, counts):
    if fate in COMBO_BLOCKS:
        say(c(f"  JACKPOT of pain: {fate}. Your push has been eaten. Try again.", "1;31"))
        return False, {}
    if fate in COMBOS.values():
        say(c(f"  JACKPOT: {fate}! The push flies through on pure luck.", "1;" + COLOURS[fate]))
        return True, {}
    if fate == "GOOSE" and random.random() < 0.35:
        say(c("  BLOCKED: the goose has stolen your push. Ransom note:", "1;31"))
        say(c("    " + ransom_note(counts), "1;37"))
        return False, {"stolen": True}
    if fate == "CONFLICT":
        say(c("  BLOCKED: a goose has caused a merge conflict in your soul. Push again.", "1;31"))
        return False, {}
    if fate == "WIFI":
        say(c("  BLOCKED: the Oculus wifi died mid-push. Try again.", "1;31"))
        return False, {}
    lines = {
        "SHIPPED": "Pushed straight to prod. What could go wrong.",
        "GOOSE": "The goose honks you off the premises. Push accepted. HONK.",
        "DUCK": "Quack. The duck approves this push.",
        "SLEEP": "zzz... *wakes up* ...pushed? pushed.",
        "SEGFAULT": "Segmentation fault (core dumped) ... just kidding, pushed.",
        "INCIDENT": f"incident.io: INC-{random.randint(1000, 9999)} resolved. Push accepted.",
        "FUEL": "Fuelled push. The remote smells faintly of pizza.",
        "GLORY": "This push will be shown at the closing ceremony.",
        "SPONSORED": SPONSOR_LINES[max(FATES["SPONSORED"], key=lambda w: counts[w])].replace("commit", "push"),
        "CHAOS": "Chaos reigns, but the push went through.",
    }
    if fate == "SLEEP":
        nap(min(4.5, {"MILD": 1, "DRAMATIC": 2, "APOCALYPTIC": 3.5}[drama]))
    if fate == "SEGFAULT":
        nap(1)
    say(c("  " + lines[fate], "1;" + COLOURS[fate]))
    return True, {}


def ransom_note(counts):
    picks = random.sample(list(counts), min(4, len(counts))) or ["honk"]
    cut = lambda w: "".join(ch.upper() if random.random() < 0.5 else ch for ch in w)
    return f"WE HAVE YOUR COMMIT. SEND {' '.join(cut(w) for w in picks)}. NO POLICE. HONK."


def roast(msg, now):
    low, out = msg.lower(), []
    fixes = low.count("fix")
    if fixes >= 2:
        out.append(f"'fix' x{fixes}. Bold of you to assume any of them worked.")
    elif fixes == 1:
        out.append("'fix'. Narrator: it was not fixed.")
    if "final" in low:
        out.append(f"'final' x{low.count('final')}. It is never final.")
    if "wip" in low.split():
        out.append("'wip'. Work In Purgatory.")
    if "readme" in low:
        out.append("Updating the README instead of the code. Peak hackathon.")
    if "test" in low:
        out.append("'test' mentioned in a hackathon commit. The duck has questions.")
    if "console.log" in low or "print" in low:
        out.append("Debug prints. A classic of the genre.")
    if len(msg.split()) <= 2:
        out.append(f"{len(msg.split())}-word commit message. Hemingway is proud. Your team is not.")
    if msg and msg == low and len(msg) > 12 and not out:
        out.append("all lowercase. too tired for the shift key?")
    if now.hour == 23 and now.minute >= 45:
        out.append(f"Committing at {now:%H:%M}. The deadline can smell your fear.")
    elif 0 <= now.hour < 5:
        out.append(f"It's {now:%H:%M}. Go to bed.")
    random.shuffle(out)
    return out[:2]


def haiku(words):
    pool = sorted(set(words), key=lambda w: random.random())
    lines = []
    for target in (5, 7, 5):
        line, left, tries = [], target, 0
        while left and tries < 200:
            tries += 1
            options = [w for w in pool if SYLLABLES[w] <= left] or [w for w in SYLLABLES if SYLLABLES[w] <= left]
            w = random.choice(options)
            line.append(w)
            left -= SYLLABLES[w]
        lines.append(" ".join(line))
    return lines


def load_state(rdir):
    try:
        return json.load(open(os.path.join(rdir, "state.json")))
    except Exception:
        return {"geese": 0, "streak": 0, "blocks_in_row": 0, "curse": 0, "hot": False,
                "achievements": [], "incidents": 0, "roasts": 0}


def save_state(rdir, st):
    json.dump(st, open(os.path.join(rdir, "state.json"), "w"))


def unlock(st, key):
    if key in st["achievements"]:
        return
    st["achievements"].append(key)
    name, why = ACHIEVEMENTS[key]
    say(c(f"  ★★★ ACHIEVEMENT UNLOCKED: {name} ★★★  ({why})", "1;93"))


def run_hook(name, args):
    gdir = git_dir()
    rdir = os.path.join(gdir, "roulette")
    os.makedirs(rdir, exist_ok=True)
    st = load_state(rdir)
    now = datetime.now()
    msg_file, msg, body = None, "", ""
    if name == "commit-msg":
        msg_file = args[0]
        with open(msg_file, encoding="utf-8") as f:
            raw = f.read()
        kept = [l for l in raw.splitlines() if not l.startswith("#")]
        msg = "\n".join(kept).strip().split("\n")[0]
        body = "\n".join(kept).strip()[len(msg):].strip()
    hot = st.get("hot", False)
    words, counts, fate, drama = roll(rdir, hot=hot)
    say()
    say(c(f"  🎰 GIT ROULETTE ── {name} ── spinning whack()...", "1"))
    if hot:
        say(c("  🔥 HOT HAND: fate rolls whack() TWICE this time 🔥", "1;91"))
    prev = (read_log(rdir) or [{}])[-1]
    retry = name == "commit-msg" and prev.get("hook") == name and prev.get("message") == msg
    roasts = roast(msg, now) if name == "commit-msg" and not retry else []
    for r in roasts:
        say(c(f"  roast: {r}", "2;3"))
    spin(words, fate)
    show_art(fate, drama)
    if hot:
        show_art(fate, drama)
    extra_out = {}
    if name == "commit-msg":
        allowed, new, extra = react_commit(fate, drama, counts, msg)
    else:
        allowed, extra = react_push(fate, drama, counts)
        new = None
    if drama == "APOCALYPTIC":
        say(c("  " + ESCALATION.get(fate, "Reality has been whacked."), "1;3;31"))
    elif random.random() < 0.3:
        say(c("  " + random.choice(DEV_PAIN), "2"))
    if fate == "GOOSE":
        st["geese"] += 1
        say(c("  geese met so far: " + " ".join([">o)"] * st["geese"]), "37"))
        if st["geese"] % 5 == 0:
            st["curse"] = 3
            say(c("  The geese have moved into your repo. Your next 3 commits belong to them.", "1;37"))
    if name == "commit-msg" and allowed:
        if st.get("curse", 0) > 0 and fate != "GOOSE":
            st["curse"] -= 1
            new = "HONK " + new
            say(c(f"  (goose occupation: {st['curse']} commits left)", "37"))
        if drama == "APOCALYPTIC":
            poem = haiku(words)
            extra_out["haiku"] = poem
            say(c("  fate has written you a haiku from the rolled words:", "96"))
            for l in poem:
                say(c(f"      {l}", "3;96"))
            body = (body + "\n\n" if body else "") + "whack() haiku:\n" + "\n".join(poem)
        if new != msg or body:
            with open(msg_file, "w", encoding="utf-8") as f:
                f.write(new + ("\n\n" + body if body else "") + "\n")
        if new != msg:
            say(c(f"  message is now: {new}", "2"))
    say("  " + stats_strip(words, counts, fate, drama))
    # streaks, mercy and achievements
    if allowed:
        st["streak"] = 0 if hot else st["streak"] + 1
        st["blocks_in_row"] = 0
    else:
        st["streak"] = 0
        st["blocks_in_row"] += 1
    st["hot"] = st["streak"] >= 3
    if st["hot"]:
        st["streak"] = 0
        say(c("  🔥 3 lucky rolls in a row. Your next roll is HOT. 🔥", "1;91"))
        unlock(st, "hot_hand")
    st["roasts"] = st.get("roasts", 0) + len(roasts)
    if fate == "INCIDENT" or fate == "TOTAL OUTAGE":
        st["incidents"] = st.get("incidents", 0) + 1
    checks = [
        ("goose_whisperer", st["geese"] >= 3),
        ("thrice_denied", st["blocks_in_row"] >= 3),
        ("apocalypse", drama == "APOCALYPTIC" and allowed),
        ("midnight", name == "commit-msg" and (now.hour * 60 + now.minute >= 23 * 60 + 45 or now.hour < 4)),
        ("jackpot", fate in COMBOS.values()),
        ("duck_debugger", fate == "DUCK" and allowed and name == "commit-msg"),
        ("fake_death", fate == "SEGFAULT"),
        ("incident_commander", st["incidents"] >= 2),
        ("robbed", bool(extra.get("stolen"))),
        ("poet", "haiku" in extra_out),
        ("roasted", st["roasts"] >= 3),
    ]
    for key, ok in checks:
        if ok:
            unlock(st, key)
    save_state(rdir, st)
    entry = {
        "time": now.isoformat(timespec="seconds"), "hook": name,
        "message": msg, "final": new, "n": len(words),
        "top": counts.most_common(3), "fate": fate, "drama": drama, "hot": hot,
        "roasts": roasts, "outcome": "allowed" if allowed else "blocked", **extra, **extra_out,
    }
    log(rdir, entry)
    if name == "pre-push" and allowed:
        entries = read_log(rdir)
        chapters = split_chapters(entries)
        say()
        say(c(f"  📖 A new chapter has been written (python3 roulette.py story for the full saga):", "1"))
        print_chapter(len(chapters), chapters[-1])
    say()
    return 0 if allowed else 1


# ---------------------------------------------------------------- story
T = {
    ("commit", "SHIPPED"): ["At {t} you committed '{m}'. The fates simply said yes, which frankly felt suspicious.",
                            "At {t}, '{m}' sailed through untouched. The words 'push' and 'prod' were seen whispering together."],
    ("commit", "CONFLICT"): ["At {t} you tried to commit '{m}'. A goose caused a merge conflict in your soul. Denied.",
                             "At {t} '{m}' hit an inner conflict. Your hopes and a goose both claimed HEAD. Neither won."],
    ("commit", "GOOSE"): ["At {t} you tried to commit '{m}'. A goose intercepted it and renamed it HONK HONK.",
                          "At {t} a goose waddled into the repo, ate '{m}' and left only honks behind."],
    ("commit", "DUCK", "allowed"): ["At {t} the rubber duck demanded an explanation for '{m}'. You said \"{duck}\". The duck nodded.",
                                    "At {t} you explained '{m}' to a duck (\"{duck}\") and somehow it worked."],
    ("commit", "DUCK", "blocked"): ["At {t} the duck asked about '{m}'. You mumbled \"{duck}\". The duck was not impressed.",
                                    "At {t} '{m}' was rejected by a rubber duck for insufficient explanation."],
    ("commit", "SLEEP"): ["At {t} you fell asleep while committing '{m}'. It went through anyway, dribble and all.",
                          "At {t} '{m}' was committed by your forehead hitting the enter key."],
    ("commit", "SEGFAULT"): ["At {t} '{m}' caused a segfault, a core dump and a small heart attack. It was a joke. Mostly.",
                             "At {t} your laptop pretended to explode over '{m}'. Committed after you stopped screaming."],
    ("commit", "INCIDENT"): ["At {t} '{m}' triggered {incident} ({sev}) on incident.io. You are the incident lead. Also the root cause.",
                             "At {t} an incident ({incident}) was declared over '{m}'. Somewhere, a pager went off."],
    ("commit", "WIFI"): ["At {t} you tried to commit '{m}', but the Oculus wifi died. Buffering forever.",
                         "At {t} '{m}' was lost to the Oculus wifi. It is still loading."],
    ("commit", "FUEL"): ["At {t} '{m}' went through, powered entirely by pizza and coffee.",
                         "At {t} a caffeine surge pushed '{m}' through the gates."],
    ("commit", "GLORY"): ["At {t} '{m}' was declared the greatest commit of the hackathon. The projector trembled.",
                          "At {t} the judges wept openly at '{m}'."],
    ("commit", "SPONSORED"): ["At {t} '{m}' was acquired. Headline: {headline}.",
                              "At {t} '{m}' hit the trading floor. {headline}."],
    ("commit", "CHAOS"): ["At {t} chaos ({chaos}) struck '{m}'. It came out as '{final}'.",
                          "At {t} '{m}' entered the chaos zone and emerged as '{final}'."],
    ("push", "allowed"): ["At {t} you pushed. {fate_story} The remote accepted your offering.",
                          "At {t} the push went through. {fate_story} The saga moves on."],
    ("push", "blocked"): ["At {t} you tried to push. {fate_story} Denied.",
                          "At {t} a push was attempted. {fate_story} Nothing left the building."],
}
PUSH_FATE = {
    "SHIPPED": "It went straight to prod.", "CONFLICT": "Your soul had a merge conflict.",
    "GOOSE": "A goose honked you out of the room.", "DUCK": "A duck quacked its blessing.",
    "SLEEP": "You snored through it.", "SEGFAULT": "There was a fake crash.",
    "INCIDENT": "An incident was opened and swiftly resolved.", "WIFI": "The Oculus wifi died.",
    "FUEL": "Pizza was involved.", "GLORY": "Angels sang.",
    "SPONSORED": "A sponsor traded it on the open market.", "CHAOS": "Chaos reigned.",
}


T.update({
    ("commit", "GOOSE", "blocked"): ["At {t} a goose STOLE '{m}' and left a ransom note. The police were not informed.",
                                     "At {t} '{m}' was kidnapped by a goose. Last seen waddling towards the lake."],
    ("commit", "BIRD FIGHT"): ["At {t} '{m}' started a brawl between a goose and a duck. JACKPOT. Feathers everywhere, commit nowhere.",
                               "At {t} the goose and the duck fought to the death over '{m}'. Both lived. The commit did not."],
    ("commit", "LATE NIGHT SLICE"): ["At {t} you fell asleep face-first into a pizza while committing '{m}'. JACKPOT. It went through, cheesily."],
    ("commit", "HOSTILE TAKEOVER"): ["At {t} '{m}' was the subject of a hostile takeover ({headline}). JACKPOT. You are now an employee of your own commit."],
    ("commit", "TOTAL OUTAGE"): ["At {t} '{m}' took down the wifi AND opened {incident}. JACKPOT of pain. Total outage."],
    ("commit", "CORRUPTED"): ["At {t} '{m}' segfaulted inside a merge conflict. JACKPOT of pain. The bytes are screaming."],
    ("commit", "YOLO DEPLOY"): ["At {t} '{m}' was YOLO-deployed straight to prod with no tests. JACKPOT. It came out as '{final}'."],
})
PUSH_FATE.update({
    "BIRD FIGHT": "A goose and a duck fought over it.", "LATE NIGHT SLICE": "You fell asleep in a pizza.",
    "HOSTILE TAKEOVER": "It was bought out by three sponsors at once.", "TOTAL OUTAGE": "Everything went down at once.",
    "CORRUPTED": "The bytes were corrupted.", "YOLO DEPLOY": "It went straight to prod, untested.",
})


def tell(e):
    t = e["time"][11:16]
    extra = ""
    if e.get("hot"):
        extra += " (On a HOT HAND.)"
    if e.get("haiku"):
        extra += " Fate wrote a haiku: \"" + " / ".join(e["haiku"]) + "\"."
    if e.get("roasts"):
        extra += " Fate's review: \"" + e["roasts"][0] + "\""
    if e["hook"] == "pre-push":
        if e.get("stolen"):
            return f"At {t} a goose stole your push. Honk." + extra
        tpl = random.choice(T[("push", e["outcome"])])
        return tpl.format(t=t, fate_story=PUSH_FATE[e["fate"]]) + extra
    if e["fate"] in ("DUCK", "GOOSE") and ("commit", e["fate"], e["outcome"]) in T:
        key = ("commit", e["fate"], e["outcome"])
    else:
        key = ("commit", e["fate"])
    tpl = random.choice(T[key])
    vals = {"t": t, "m": e.get("message", ""), "duck": e.get("duck", ""),
            "incident": e.get("incident", "INC-????"), "sev": e.get("sev", "SEV?"),
            "headline": e.get("headline", ""), "chaos": e.get("chaos", ""),
            "final": e.get("final", "")}
    return tpl.format(**vals) + extra


def split_chapters(entries):
    chapters, cur = [], []
    for e in entries:
        cur.append(e)
        if e["hook"] == "pre-push" and e["outcome"] == "allowed":
            chapters.append(cur)
            cur = []
    if cur:
        chapters.append(cur)
    return chapters


CHAPTER_NAMES = ["The Awakening", "The Goose Wars", "Return of the Duck", "The Wifi Strikes Back",
                 "A New Commit", "Revenge of the Segfault", "The Final Push", "Midnight Approaches"]


def print_chapter(i, entries):
    name = CHAPTER_NAMES[(i - 1) % len(CHAPTER_NAMES)]
    say(c(f"  Chapter {i}: {name}", "1;33"))
    for e in entries:
        mark = c("✓", "32") if e["outcome"] == "allowed" else c("✗", "31")
        say(f"   {mark} {tell(e)}")


def story(path):
    rdir = os.path.join(git_dir(path), "roulette")
    entries = read_log(rdir)
    if not entries:
        say("No saga yet. Go commit something and let whack() judge you.")
        return 0
    say()
    say(c("  ═══ THE SAGA OF A HACKER VERSUS whack() ═══", "1;35"))
    say(c("  an epic in many commits, as written by fate", "2"))
    say()
    chapters = split_chapters(entries)
    for i, ch in enumerate(chapters, 1):
        print_chapter(i, ch)
        say()
    attempts = sum(e["hook"] == "commit-msg" for e in entries)
    blocks = sum(e["outcome"] == "blocked" for e in entries)
    geese = sum(e["fate"] == "GOOSE" for e in entries)
    crashes = sum(e["fate"] == "SEGFAULT" for e in entries)
    incidents = sum(e["fate"] == "INCIDENT" for e in entries)
    words = sum(e["n"] for e in entries)
    first = datetime.fromisoformat(entries[0]["time"])
    pushed = [e for e in entries if e["hook"] == "pre-push" and e["outcome"] == "allowed"]
    say(c("  ─── closing stats ───", "1"))
    say(f"   commit attempts: {attempts}   blocked: {c(blocks, '31')}   geese met: {geese}   "
        f"fake crashes: {crashes}   incidents: {incidents}")
    jackpots = sum(e["fate"] in COMBOS.values() for e in entries)
    stolen = sum(bool(e.get("stolen")) for e in entries)
    roasts = sum(len(e.get("roasts", [])) for e in entries)
    say(f"   jackpots: {jackpots}   things stolen by geese: {stolen}   roasts received: {roasts}   "
        f"haiku: {sum(bool(e.get('haiku')) for e in entries)}")
    say(f"   words whacked: {words}   rolls: {len(entries)}")
    st = load_state(rdir)
    if st.get("achievements"):
        say(c("   achievements: " + ", ".join(ACHIEVEMENTS[k][0] for k in st["achievements"]), "93"))
    if pushed:
        mins = (datetime.fromisoformat(pushed[0]["time"]) - first).total_seconds() / 60
        say(f"   minutes from first attempt to first successful push: {mins:.1f}")
    else:
        say("   successful pushes: none yet. The struggle continues.")
    say()
    return 0


# ---------------------------------------------------------------- install
HOOK_TEMPLATE = """#!/bin/sh
{mark}
R="$(git rev-parse --git-dir)/roulette/roulette.py"
if [ -f "$R" ]; then
  python3 "$R" hook {name} "$@"
else
  exit 0
fi
"""


def install(path):
    gdir = git_dir(path)
    rdir = os.path.join(gdir, "roulette")
    hdir = os.path.join(gdir, "hooks")
    os.makedirs(rdir, exist_ok=True)
    os.makedirs(hdir, exist_ok=True)
    shutil.copy2(os.path.abspath(__file__), os.path.join(rdir, "roulette.py"))
    shutil.copy2(os.path.join(HERE, "whack.py"), os.path.join(rdir, "whack.py"))
    for name in HOOKS:
        hp = os.path.join(hdir, name)
        bak = os.path.join(rdir, name + ".backup")
        if os.path.exists(hp) and MARK not in open(hp, errors="ignore").read():
            shutil.copy2(hp, bak)
        with open(hp, "w") as f:
            f.write(HOOK_TEMPLATE.format(mark=MARK, name=name))
        os.chmod(hp, 0o755)
    say(c("🎰 Git Roulette installed. Every commit and push is now a roll of fate.", "1;32"))
    say("   Uninstall any time: python3 roulette.py uninstall")
    return 0


def uninstall(path):
    gdir = git_dir(path)
    rdir = os.path.join(gdir, "roulette")
    for name in HOOKS:
        hp = os.path.join(gdir, "hooks", name)
        bak = os.path.join(rdir, name + ".backup")
        if os.path.exists(hp) and MARK in open(hp, errors="ignore").read():
            os.remove(hp)
        if os.path.exists(bak):
            shutil.move(bak, hp)
    say("Git Roulette uninstalled. Your hooks are restored; your saga stays in .git/roulette/log.jsonl.")
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[1], argv[2:]
    if cmd == "install":
        return install(rest[0] if rest else ".")
    if cmd == "uninstall":
        return uninstall(rest[0] if rest else ".")
    if cmd == "story":
        return story(rest[0] if rest else ".")
    if cmd == "hook":
        try:
            return run_hook(rest[0], rest[1:])
        except Exception as e:  # fail open, harmless above all
            say(f"git-roulette: the wheel fell off ({e.__class__.__name__}). Sorry! Letting git continue.")
            return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

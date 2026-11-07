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


# ---------------------------------------------------------------- output
def _tty(stream):
    try:
        return stream.isatty()
    except Exception:
        return False


OUT = sys.stderr
COLOR = (os.environ.get("ROULETTE_FORCE_COLOR") == "1"
         or (_tty(OUT) and "NO_COLOR" not in os.environ))
ANIMATE = _tty(OUT) and os.environ.get("ROULETTE_NO_ANIM") != "1"


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if COLOR else text


def say(text=""):
    print(text, file=OUT, flush=True)


def nap(seconds):
    if ANIMATE:
        time.sleep(seconds)


# ---------------------------------------------------------------- the roll
def roll(rdir):
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
    finally:
        os.chdir(cwd)
    counts = Counter(words)
    # A fate's score is how many of its words were rolled, averaged per word, so the
    # lonely one-word fates (conflict, wifi) can beat the eight-sponsor lobby.
    scores = {f: sum(counts[w] for w in ws) / len(ws) for f, ws in FATES.items()}
    best = max(scores.values())
    fate = random.choice([f for f, s in scores.items() if s == best])
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
        time.sleep(delay)
        total += delay
        delay *= 1.17
        if total > 1.8:
            break
    land = f"  [ {'*' * 11} ]  [ {fate:^11} ]"
    OUT.write("\r" + c(land, "1;" + COLOURS[fate]) + "\n")
    OUT.flush()
    time.sleep(0.3)


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
    fw = Counter({w: counts[w] for w in FATES[fate] if counts[w]})
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
        ans = os.environ.get("ROULETTE_DUCK_ANSWER", "")
        say(c(prompt, "33") + ans)
        return ans
    try:
        with open("/dev/tty", "r+") as tty:
            tty.write(prompt)
            tty.flush()
            return tty.readline().strip()
    except OSError:
        ans = os.environ.get("ROULETTE_DUCK_ANSWER", "")
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
        say(c("  A goose has seized your commit message. HONK.", "1;37"))
        return True, f"HONK HONK (originally: {msg})", {"honk": True}
    if fate == "DUCK":
        say(c("  The rubber duck stares at you. Explain your change.", "33"))
        ans = ask_tty("  🦆 > ")
        if len(ans.strip()) >= 15:
            say(c("  The duck nods slowly. Quack. Commit allowed.", "1;33"))
            return True, msg, {"duck": ans}
        say(c("  BLOCKED: the duck is unconvinced. Quack quack (that's a no).", "1;31"))
        return False, msg, {"duck": ans}
    if fate == "SLEEP":
        secs = {"MILD": 1.2, "DRAMATIC": 2.5, "APOCALYPTIC": 4.5}[drama]
        say(c("  You have fallen asleep on the keyboard...", "34"))
        if ANIMATE:
            t = 0.0
            while t < secs:
                OUT.write(c(random.choice(["z", "Z", "zz", "Zz"]) + " ", "34"))
                OUT.flush()
                time.sleep(0.3)
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


def run_hook(name, args):
    gdir = git_dir()
    rdir = os.path.join(gdir, "roulette")
    os.makedirs(rdir, exist_ok=True)
    msg_file, msg = None, ""
    if name == "commit-msg":
        msg_file = args[0]
        with open(msg_file, encoding="utf-8") as f:
            raw = f.read()
        msg = "\n".join(l for l in raw.splitlines() if not l.startswith("#")).strip()
    words, counts, fate, drama = roll(rdir)
    say()
    say(c(f"  🎰 GIT ROULETTE ── {name} ── spinning whack()...", "1"))
    spin(words, fate)
    show_art(fate, drama)
    if name == "commit-msg":
        allowed, new, extra = react_commit(fate, drama, counts, msg)
        if allowed and new != msg:
            with open(msg_file, "w", encoding="utf-8") as f:
                f.write(new + "\n")
            say(c(f"  message is now: {new}", "2"))
    else:
        allowed, extra = react_push(fate, drama, counts)
        new = None
    say("  " + stats_strip(words, counts, fate, drama))
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"), "hook": name,
        "message": msg, "final": new, "n": len(words),
        "top": counts.most_common(3), "fate": fate, "drama": drama,
        "outcome": "allowed" if allowed else "blocked", **extra,
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


def tell(e):
    t = e["time"][11:16]
    if e["hook"] == "pre-push":
        tpl = random.choice(T[("push", e["outcome"])])
        return tpl.format(t=t, fate_story=PUSH_FATE[e["fate"]])
    key = ("commit", e["fate"], e["outcome"]) if e["fate"] == "DUCK" else ("commit", e["fate"])
    tpl = random.choice(T[key])
    vals = {"t": t, "m": e.get("message", ""), "duck": e.get("duck", ""),
            "incident": e.get("incident", "INC-????"), "sev": e.get("sev", "SEV?"),
            "headline": e.get("headline", ""), "chaos": e.get("chaos", ""),
            "final": e.get("final", "")}
    return tpl.format(**vals)


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
    say(f"   words whacked: {words}   rolls: {len(entries)}")
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

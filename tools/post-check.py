#!/usr/bin/env python3
"""Check a LinkedIn post draft for engagement bait, unsupported numbers, and format problems.

    python tools/post-check.py drafts/post.md --facts facts.md

ERROR findings must be fixed before the post is shown or published. WARN
findings need a look and a reason if they stay. Exits 1 when any ERROR is
found, 0 otherwise. Standard library only.
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

MAX_POST = 3000
PREVIEW = 200
MAX_HASHTAGS = 3
MAX_MENTIONS = 2
MAX_EMOJI = 3

# Asking for engagement outright. Readers spot these, and they are the
# fastest way to look like you're farming comments.
BAIT = [
    (r"\b(comment|drop|share|post|leave)\b[^.?!\n]{0,30}\b(below|in the comments)\b", "asks for comments"),
    (r"\blet me know in the comments\b", "asks for comments"),
    (r"\bsound off\b", "asks for comments"),
    (r"\btag (someone|a friend|a colleague|a coworker|your|anyone|a person)\b", "asks readers to tag people"),
    (r"\b(like|repost|share|save) (this post|this if|if you)\b", "asks for likes, reposts, or saves"),
    (r"^\s*(like|repost|share|save) this\b", "asks for likes, reposts, or saves"),
    (r"\bhit (the )?(like|follow|repost|bell)\b", "asks for likes or follows"),
    (r"\bsmash (that|the)\b", "asks for likes or follows"),
    (r"\bfollow (me )?for more\b", "asks for follows"),
    (r"\b(agree|thoughts|am i wrong|anyone else|who else|yes or no|right)\s*\?", "generic question that asks for engagement"),
    (r"\bwhat do you (all |guys )?think\s*\?", "generic question that asks for engagement"),
    (r"\bdm me\b", "asks for DMs"),
    ("♻|\U0001F447", "repost or point-down emoji used as a call to action"),
]

# Keyword giveaways: "Comment PLAYBOOK and I'll send it." Case-sensitive on
# the keyword so ordinary sentences don't trip it.
GIVEAWAY = re.compile(r"\b(?:[Cc]omment|[Tt]ype|[Rr]eply|[Dd]rop|[Ww]rite)\s+[\"']?([A-Z]{3,})[\"']?\b")

# Not forbidden, but each is a claim the user has to stand behind or a
# phrase that tells readers a stunt is coming.
RISK = [
    (r"\bunpopular opinion\b", "\"unpopular opinion\" tells readers you're performing; just state the position"),
    (r"\bhot take\b", "\"hot take\" tells readers you're performing; just state the position"),
    (r"\bcontroversial\b", "calling your own post controversial reads as bait"),
    (r"\b(nobody|no one) (talks|is talking) about\b", "false exclusivity; someone always has"),
    (r"\b(everyone|everybody|nobody|no one|always|never|guaranteed|100%)\b", "absolute claim; can you defend it against the one exception someone will post?"),
    (r"\b(i'?m|i am) (new|brand new) (to|at)\b", "tenure claim; confirm it against facts.md"),
    (r"\b(just|only just|recently) started\b", "tenure claim; confirm it against facts.md"),
    (r"\b(first|second|third|fourth|fifth|sixth|\d+(st|nd|rd|th)) (week|month|year|quarter)\b", "tenure claim; confirm it against facts.md"),
    (r"\b\d+ (weeks|months|years) (in|into)\b", "tenure claim; confirm it against facts.md"),
    (r"\ba (client|founder|ceo|cfo|friend|prospect|recruiter|manager)( of mine)? (told|said|asked)\b", "anecdote; it must be real and listed in facts.md"),
    (r"https?://|www\.", "outside link in the body; many put it in the first comment instead (unconfirmed)"),
    ("—", "em dash; reads as machine-written to many people now"),
]

THROAT_CLEARING = re.compile(
    r"^(i've been thinking|let me tell you|here's (the thing|a|what)|in today's|"
    r"so,? i|i want to (talk|share)|i wanted to share|quick (thought|story)|"
    r"a (quick|short) (post|note))",
    re.I,
)

NUMBER = re.compile(
    r"(?<![\w.])([$€£])?(\d[\d,]*(?:\.\d+)?)(?!st\b|nd\b|rd\b|th\b)(\s?(?:%|percent|k\b|K\b|m\b|M\b|x\b))?"
)


def number_value(raw, suffix):
    try:
        value = float(raw.replace(",", ""))
    except ValueError:
        return None
    suffix = (suffix or "").strip().lower()
    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000
    return round(value, 4)


def numbers_in(text):
    for m in NUMBER.finditer(text):
        value = number_value(m.group(2), m.group(3))
        if value is not None:
            yield m, value


def load_facts(path):
    text = Path(path).read_text(encoding="utf-8")
    return {value for _, value in numbers_in(text)}


def is_emoji(ch):
    cp = ord(ch)
    return 0x1F300 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF


def is_math_styled(ch):
    # Unicode "bold", "italic", and script letters used to fake formatting.
    return 0x1D400 <= ord(ch) <= 0x1D7FF


def check(text, facts):
    findings = []
    lines = text.splitlines()

    def add(level, line_no, rule, message, snippet=""):
        findings.append((level, line_no, rule, message, snippet.strip()))

    for i, line in enumerate(lines, 1):
        lower = line.lower()
        for pattern, message in BAIT:
            m = re.search(pattern, lower)
            if m:
                add("ERROR", i, "bait", message, m.group(0))
        m = GIVEAWAY.search(line)
        if m:
            add("ERROR", i, "bait", "keyword giveaway", m.group(0))
        for pattern, message in RISK:
            m = re.search(pattern, lower)
            if m:
                add("WARN", i, "risk", message, m.group(0))
        if any(is_math_styled(ch) for ch in line):
            add("ERROR", i, "format", "Unicode bold or italic letters; screen readers and search can't read them", line[:40])

        for m, value in numbers_in(line):
            token = m.group(0)
            if facts is None:
                add("ERROR", i, "number", "no facts file given, so this number can't be checked", token)
                continue
            if value in facts:
                continue
            unit = m.group(1) or (m.group(3) or "").strip()
            if not unit and 1900 <= value <= 2099 and value == int(value):
                add("WARN", i, "number", "looks like a year; make sure the date is right", token)
            elif not unit and value <= 10:
                add("WARN", i, "number", "small number not in facts.md; fine for counts, not for claims", token)
            else:
                add("ERROR", i, "number", "not in facts.md; add it there with its source or take it out", token)

    body = text.strip()
    length = len(body)
    if length > MAX_POST:
        add("ERROR", 0, "format", f"{length} characters; LinkedIn posts cap at {MAX_POST}")

    hashtags = re.findall(r"(?<!\w)#\w+", body)
    if len(hashtags) > MAX_HASHTAGS:
        add("WARN", 0, "format", f"{len(hashtags)} hashtags; more than {MAX_HASHTAGS} looks like a reach grab")

    mentions = re.findall(r"(?<![\w.])@\w+", body)
    if len(mentions) > MAX_MENTIONS:
        add("WARN", 0, "people", f"{len(mentions)} tags; tag only people who were actually involved")

    emoji = sum(1 for ch in body if is_emoji(ch))
    if emoji > MAX_EMOJI:
        add("WARN", 0, "format", f"{emoji} emoji; more than {MAX_EMOJI} reads as a template")

    first = next((l for l in lines if l.strip()), "")
    if THROAT_CLEARING.search(first.strip()):
        add("WARN", 1, "hook", "opening line clears its throat; start with the substance", first[:60])

    return findings


def preview(text):
    flat = " / ".join(l.strip() for l in text.strip().splitlines() if l.strip())
    flat = unicodedata.normalize("NFC", flat)
    return flat[:PREVIEW] + ("..." if len(flat) > PREVIEW else "")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", help="one post per file")
    parser.add_argument("--facts", help="facts.md; every number in a post must appear in it")
    parser.add_argument("--quiet", action="store_true", help="skip the above-the-cut preview")
    args = parser.parse_args()

    facts = load_facts(args.facts) if args.facts else None
    errors = 0
    for name in args.files:
        text = Path(name).read_text(encoding="utf-8")
        findings = check(text, facts)
        errors += sum(1 for f in findings if f[0] == "ERROR")
        if not args.quiet:
            print(f"{name}: {len(text.strip())} characters")
            print(f"  above the cut: {preview(text)}")
        for level, line_no, rule, message, snippet in findings:
            where = f"{name}:{line_no}" if line_no else name
            tail = f'  "{snippet}"' if snippet else ""
            print(f"{where}: {level} [{rule}] {message}{tail}")
        if not findings:
            print(f"{name}: clean")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

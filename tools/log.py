#!/usr/bin/env python3
"""Track elicitation posts, report which techniques work, and enforce cooldowns.

    python tools/log.py add --file drafts/2026-10-06-range.md --technique range
    python tools/log.py result 3 --impressions 4100 --comments 37 --reactions 88
    python tools/log.py report
    python tools/log.py suggest

The log is a CSV (default tracking/posts.csv in the current directory) so it
opens in a spreadsheet. Standard library only.
"""

import argparse
import csv
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

TECHNIQUES = ["range", "debatable", "skeptic", "insider", "learner", "give-first", "expert-callout"]
FIELDS = ["id", "posted", "technique", "file", "url", "impressions", "comments",
          "reactions", "reposts", "bait_callouts", "notes"]
MIN_SAMPLE = 3

# (max uses, window in days, minimum days between uses)
LIMITS = {
    "debatable": (2, 30, 14),
    "learner": (1, 60, 60),
}
BAIT_COOLDOWN = 60


def load(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def num(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def day(value):
    return date.fromisoformat(value)


def cmd_add(args, rows):
    next_id = max((num(r["id"]) or 0 for r in rows), default=0) + 1
    rows.append({
        "id": str(next_id),
        "posted": args.posted or date.today().isoformat(),
        "technique": args.technique,
        "file": args.file or "",
        "url": args.url or "",
        "impressions": "", "comments": "", "reactions": "", "reposts": "",
        "bait_callouts": "", "notes": args.notes or "",
    })
    print(f"logged post {next_id} ({args.technique}). Add results in a few days with:")
    print(f"  python tools/log.py result {next_id} --impressions N --comments N --reactions N")
    for warning in warnings(rows, date.today()):
        print(f"warning: {warning}")
    return rows


def cmd_result(args, rows):
    row = next((r for r in rows if r["id"] == str(args.id)), None)
    if row is None:
        sys.exit(f"no post with id {args.id}")
    for field in ["impressions", "comments", "reactions", "reposts", "bait_callouts"]:
        value = getattr(args, field)
        if value is not None:
            row[field] = str(value)
    if args.notes:
        row["notes"] = (row["notes"] + "; " if row["notes"] else "") + args.notes
    print(f"updated post {args.id}")
    if num(row["bait_callouts"]):
        print(f"{row['technique']} is now on a {BAIT_COOLDOWN}-day cooldown because someone called the post bait.")
    return rows


def warnings(rows, today):
    out = []
    dated = sorted(rows, key=lambda r: r["posted"])
    if len(dated) >= 2 and dated[-1]["technique"] == dated[-2]["technique"]:
        out.append(f"the last two posts both used {dated[-1]['technique']}; rotate")
    for tech, (max_uses, window, gap) in LIMITS.items():
        uses = [day(r["posted"]) for r in rows if r["technique"] == tech]
        recent = [d for d in uses if (today - d).days < window]
        if len(recent) > max_uses:
            out.append(f"{tech} used {len(recent)} times in {window} days; the limit is {max_uses}")
        uses.sort()
        for a, b in zip(uses, uses[1:]):
            if (b - a).days < gap and (today - b).days < window:
                out.append(f"{tech} used twice within {gap} days ({a} and {b})")
    return out


def blocked(rows, today):
    """Techniques that shouldn't be used today, with the reason."""
    out = {}
    for r in rows:
        if num(r["bait_callouts"]) and (today - day(r["posted"])).days < BAIT_COOLDOWN:
            until = day(r["posted"]) + timedelta(days=BAIT_COOLDOWN)
            out[r["technique"]] = f"called bait on post {r['id']}; rest until {until}"
    for tech, (max_uses, window, gap) in LIMITS.items():
        uses = sorted(day(r["posted"]) for r in rows if r["technique"] == tech)
        recent = [d for d in uses if (today - d).days < window]
        if len(recent) >= max_uses:
            out.setdefault(tech, f"used {len(recent)} of {max_uses} allowed in {window} days; free on {recent[0] + timedelta(days=window)}")
        elif uses and (today - uses[-1]).days < gap:
            out.setdefault(tech, f"used on {uses[-1]}; free on {uses[-1] + timedelta(days=gap)}")
    return out


def cmd_report(args, rows):
    if not rows:
        print("no posts logged yet")
        return rows
    print(f"{'technique':<16}{'posts':>6}{'scored':>8}{'median comments':>17}{'comments/1k views':>19}{'bait calls':>12}")
    for tech in TECHNIQUES:
        posts = [r for r in rows if r["technique"] == tech]
        if not posts:
            continue
        scored = [r for r in posts if num(r["comments"]) is not None]
        median = statistics.median(num(r["comments"]) for r in scored) if scored else None
        rates = [1000 * num(r["comments"]) / num(r["impressions"])
                 for r in scored if num(r["impressions"])]
        rate = statistics.median(rates) if rates else None
        bait = sum(num(r["bait_callouts"]) or 0 for r in posts)
        print(f"{tech:<16}{len(posts):>6}{len(scored):>8}"
              f"{median if median is not None else '-':>17}"
              f"{f'{rate:.1f}' if rate is not None else '-':>19}{bait:>12}")
    thin = [t for t in TECHNIQUES if 0 < sum(1 for r in rows if r["technique"] == t and num(r["comments"]) is not None) < MIN_SAMPLE]
    if thin:
        print(f"\nfewer than {MIN_SAMPLE} scored posts, too early to judge: {', '.join(thin)}")
    print("\ncomments per 1k views is the fairer comparison; raw comments mostly track how far a post traveled.")
    return rows


def cmd_suggest(args, rows):
    today = date.today()
    stop = blocked(rows, today)
    for tech, reason in stop.items():
        print(f"don't use {tech}: {reason}")
    for warning in warnings(rows, today):
        print(f"warning: {warning}")
    counts = {t: sum(1 for r in rows if r["technique"] == t) for t in TECHNIQUES}
    open_ = [t for t in TECHNIQUES if t not in stop]
    last = max(rows, key=lambda r: r["posted"])["technique"] if rows else None
    candidates = sorted((t for t in open_ if t != last), key=lambda t: counts[t])
    untested = [t for t in candidates if counts[t] < MIN_SAMPLE]
    print(f"available: {', '.join(open_)}")
    if untested:
        print(f"needs more tries before it can be judged: {', '.join(untested)}")
    if last:
        print(f"last post used {last}; pick something else")
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--log", default="tracking/posts.csv", help="CSV log path")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="record a post once it's live")
    p.add_argument("--technique", required=True, choices=TECHNIQUES)
    p.add_argument("--file")
    p.add_argument("--url")
    p.add_argument("--posted", help="YYYY-MM-DD, default today")
    p.add_argument("--notes")

    p = sub.add_parser("result", help="record how a post did")
    p.add_argument("id", type=int)
    for field in ["impressions", "comments", "reactions", "reposts"]:
        p.add_argument(f"--{field}", type=int)
    p.add_argument("--bait-callouts", dest="bait_callouts", type=int,
                   help="comments saying the post was bait or a trick")
    p.add_argument("--notes")

    sub.add_parser("report", help="results by technique")
    sub.add_parser("suggest", help="cooldowns and what to try next")

    args = parser.parse_args()
    path = Path(args.log)
    rows = load(path)
    handler = {"add": cmd_add, "result": cmd_result, "report": cmd_report, "suggest": cmd_suggest}[args.cmd]
    updated = handler(args, rows)
    if args.cmd in ("add", "result"):
        save(path, updated)
    return 0


if __name__ == "__main__":
    sys.exit(main())

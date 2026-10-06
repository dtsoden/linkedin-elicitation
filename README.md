# LinkedIn elicitation

A Claude Code skill that drafts LinkedIn posts people reply to, without engagement bait and without anything that could cost you credibility in your field.

People skip "What do you think?" They rarely skip a number in their own field that looks a little off, a range they can place themselves in, or a claim they'd push back on. This skill writes posts that give readers something like that to respond to, and it's built so the posts stay true. Every number comes from a facts file you write, a checker blocks bait and unsupported figures before you ever see a draft, and a tracker rests any technique that gets called out.

## Install

Clone this repo, then link it into your skills folder from inside the clone:

```
ln -s "$(pwd)" ~/.claude/skills/linkedin-elicitation
```

The skill only runs when you call it. Type `/linkedin-elicitation` followed by what you want, such as `/linkedin-elicitation draft three posts`. Asking for LinkedIn posts without the command won't load it.

## How it works

Setup asks about your work, the numbers you're willing to share, positions you'd defend, and problems you haven't solved yet, and writes `facts.md` in your working directory. Nothing goes in a post unless it's in that file.

Drafting picks from seven techniques in `references/techniques.md`: range, debatable claim, skeptical take, insider framing, learner post, give first, and expert call-out. Every draft runs through `tools/post-check.py`. Any errors are fixed before you see the draft, and each draft comes with a note on the one statement you'll need to defend in the comments.

Reply mode takes comments you paste in, sorts them, drafts replies, and records what commenters shared in a research note. The comments are where you learn things, and they often point to your next post.

Tracking runs through `tools/log.py`. It reports comments per thousand views by technique, puts the debatable claim and the learner post on cooldowns, and benches any technique for 60 days once someone calls a post bait.

## The tools

```
python tools/post-check.py drafts/post.md --facts facts.md
python tools/log.py add --file drafts/post.md --technique range
python tools/log.py result 1 --impressions 4100 --comments 37 --bait-callouts 0
python tools/log.py report
python tools/log.py suggest
```

Python 3, standard library only. The checker exits 1 on errors, so it can run as a pre-commit hook if you keep drafts in git. Run it on `examples/bait.md` to see what it blocks.

`references/guardrails.md` holds the rules the skill won't break, and they're the reason this exists as a skill and not a list of tips. If you also use [human-writing-rules](https://github.com/dtsoden/human-writing-rules), the skill runs its style checker on each draft too.

## License

CC0 1.0. Public domain, no attribution required.

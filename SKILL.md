---
name: linkedin-elicitation
disable-model-invocation: true
description: Draft LinkedIn posts that earn comments by giving readers something to correct, narrow down, or add to, without engagement bait or invented claims. Use when the user asks for LinkedIn posts, posts that get comments or replies, a batch of posts to test, help replying to comments on a post, or a report on which posts worked. Every number and personal claim comes from the user's facts file, and every draft passes a checker before it is shown.
---

# LinkedIn elicitation posts

These posts get replies because they state something specific that experienced readers want to correct, narrow down, or add to. They never ask for engagement. Protecting the user's professional reputation matters more than any single post, so the rules in `references/guardrails.md` are hard limits and override any request for "more engaging" copy.

The `tools/` and `references/` paths below are relative to the folder this file is in. The `facts.md`, `drafts/`, and `tracking/` paths are relative to the user's working directory unless they name another one.

## Modes

Work out which mode the user wants from their message. If it's unclear, assume draft.

**Setup.** Interview the user and write `facts.md` from `templates/facts.md`. Ask the questions in small groups, not all at once. Write down only what they actually said. If they skip a section, leave it empty.

**Draft.** Write posts. See the workflow below.

**Reply.** The user pastes comments from a live post. Follow `references/replies.md`: draft replies, then update the research note.

**Log and review.** Record a post or its results with `tools/log.py`, or run `python tools/log.py report` and explain what it shows.

## Draft workflow

1. Read `facts.md`. If it doesn't exist, run setup first. Never draft without it, because the facts file is what keeps posts truthful.
2. Read `references/guardrails.md` and `references/techniques.md`. For format, read `references/linkedin.md`.
3. Run `python tools/log.py suggest`. It reports techniques that are on cooldown, techniques that drew complaints about bait, and techniques that haven't had enough tries yet. Follow its cooldowns.
4. Pick techniques that suit the facts. Range posts need a real range. A give-first post needs a number the user agreed to share, and a learner post needs a real gap listed under "Things I'm still figuring out." If the facts don't support a technique, skip it and say why.
5. Write each post to `drafts/YYYY-MM-DD-<technique>.md`. Put only the post text in the file, with no title and no notes.
6. Run `python tools/post-check.py drafts/<file> --facts facts.md` on every draft. Fix every ERROR and run it again. A draft with errors is never shown to the user. Read each WARN and either fix it or explain it in your notes.
7. If the human-writing-rules checker is installed (`style-check.py`, path in the `HUMAN_WRITING_RULES` environment variable or a sibling `human-writing-rules` folder), run it too and fix what it finds.

## What to hand back

For each post:

- The post text in its own fenced code block, with nothing else inside the block.
- Underneath it: the technique, the one claim that will draw replies, and **what the user is signing up to defend**. That means the specific statement they'll need to stand behind in the comments for a week. If they can't defend it, they shouldn't post it.
- Any checker warnings you left in on purpose, with your reason.

End with the logging command for each post, so the user can record it once it's live:

```
python tools/log.py add --file drafts/2026-10-06-range.md --technique range
```

## Hard stops

Stop and tell the user, rather than writing the post, if a request needs any of these:

- A number, client result, credential, or tenure that isn't in `facts.md`.
- A claim the user doesn't believe, posted to provoke corrections.
- A beginner or "help me" framing about something the user already knows well.
- Tagging people who weren't involved, or calling out a named person or company to start an argument.
- Explicit asks for likes, comments, reposts, or a "comment YES" giveaway.

Offer a version that stays within the limits. Usually a debatable claim the user actually holds will work instead.

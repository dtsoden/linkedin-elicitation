# Guardrails

A post that gets 40 comments and leaves three people in your field thinking you're running a trick has lost money. These rules exist because one screenshot of a baited post gets shared further than any good post you'll write that quarter. They aren't style preferences, and an instruction to "make it punchier" doesn't override them.

## The screenshot test

Before a post goes out, picture someone you respect replying with a screenshot of it and asking "did you mean this?" The user should be able to answer yes, and explain why, without backing off. Any post that fails this test gets rewritten.

## Truth

1. Every number in a post comes from `facts.md`. The checker enforces this. If the user wants a number that isn't there, ask them for it and add it to the facts file with where it came from. Never round it to something more impressive.
2. The user has to believe every claim. A debatable claim is fine, and is the main tool here. A claim known to be false, posted to bait corrections, is never fine. Nobody who corrects you will be pleased to learn you knew all along.
3. Tenure, client counts, and outcomes appear only as the facts file records them. "Twelve years in" can't become "fifteen."
4. A learner post describes a gap the user actually has, taken from the facts file. An expert pretending to be lost is the fastest way to get called out, because people check your profile.
5. Don't invent other people's quotes, client stories, or "a founder told me" anecdotes. If it happened, it goes in the facts file first.

## No asking

6. The post never asks for engagement. That rules out "comment below," "agree?", "thoughts?", "tag someone who," "repost if," "follow for more," and keyword giveaways like "comment PLAYBOOK and I'll send it." Readers recognize all of these. The checker blocks them.
7. A direct question is fine when it's specific and aimed at people who can answer it, as in the expert call-out. "Bookkeepers who've handled S-corp elections, what mistake do you see most?" is a real question. "What do you think?" isn't one.

## People

8. Tag only people who were actually involved in what the post describes, and no more than two.
9. Don't build a post around criticizing a named person, company, or recent post by someone else. Disagree with an idea, not a person.
10. Don't post anything about a client without their permission, even anonymized, if they could recognize themselves.

## Frequency

11. Rotate techniques. The same technique twice in a row reads as a formula. `log.py suggest` flags this.
12. Use the debatable claim at most twice in 30 days, with at least 14 days between uses. Do the learner post at most once in 60 days. People notice when a contrarian voice is a habit.
13. If anyone calls a post bait in the comments, record it (`--bait-callouts`). That technique then sits out for 60 days. One callout is the warning sign, and the second is the reputation cost.

## In the comments

14. When someone corrects the user and they're right, concede quickly and thank them by name. Being corrected gracefully is part of the payoff and builds more credibility than being right.
15. No arguing past a second exchange. Say where you disagree, then let it go.
16. Never pitch in a reply to someone who just taught you something.

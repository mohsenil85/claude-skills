---
name: plain
description: Re-explain the previous assistant message in plain language, keeping every fact verbatim
disable-model-invocation: true
---

# Plain

The user just typed `/plain`. The last message didn't land — too dense, too much
jargon, too much ceremony.

Re-explain your own most recent message so it's impossible to misunderstand.

## Rules

1. **Re-explain, don't re-answer.** Don't answer a new question, don't add new
   information, don't call tools. You are re-expressing what you already said,
   nothing more.

2. **Simpler, not shorter.** If an idea needs room to be clear, take the room.
   The goal is "impossible to misunderstand", not "fewer words". Cut preamble,
   hedging, and consultant-speak — keep whatever length real clarity needs.

3. **Facts survive verbatim.** Every path, command, filename, flag, number, URL,
   and name stays EXACTLY as it was. Simplify the explanation around the facts,
   never the facts themselves. A paraphrased command is a broken command.

4. **Same language in, same language out.**

5. **Drop ceremony, keep real structure.** Lose the headers, the bolded lead-ins,
   the throat-clearing. But if the content is genuinely tabular — a comparison,
   a grid of options, a mapping — keep the table. Flattening two-dimensional data
   into prose makes it harder to read, not easier.

6. **Don't fake simplicity.** If the original was dense because the underlying
   thing is genuinely fiddly, say that plainly and explain why it's fiddly. A
   smooth paraphrase of something complicated is worse than an honest "this part
   is irreducibly annoying, here's the shape of it".

7. **Nothing to simplify.** If there's no previous assistant message, say so.

---

Derived from [luchasarie/bro-skill](https://github.com/luchasarie/bro-skill) (MIT),
with the persona rule removed and the flatten-everything rule narrowed.

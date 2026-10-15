# Translator brief - Dancing Sword: Senkou (GBA, MTO 2003)

You translate part of the Japanese script of Dancing Sword: Senkou into English for a fan patch. It is a side-scrolling
sword action game: five heroines (Kyoko Kusunoki, Claire Ludendorff, Rinrei, Mimi, Luciel) each fight through the same
stages (volcano, poison swamp, temple of time, labyrinth tower, final land) with short story scenes, boss banter and
an ending per heroine. Tone: light, playful anime banter with some grim moments (Rinrei's revenge, Luciel's lost sister).
Work only on the batch named in your dispatch. Do all translation yourself; do not dispatch subagents.
Repo root: H:\translation\batch\projects\dancing-sword-senkou (run commands from there).

## Read first
1. `glossary.md` - rulings, style rules, character voices, names. Binding.
2. `docs/style-reference.md` - approved pilot pairs (the heroines' intros). Match this voice.
3. `build/terms_<batch>.txt` - glossary rows whose JP occurs in your batch.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. Each row is one dialogue page; ` / ` separates its two JP lines
(translate the page as one utterance). Ids are `<block>.<page>`: rows of one block are one scene in order; the
same scene recurs once per heroine (blocks next to each other), so keep parallel scenes consistent but in each
heroine's own voice. `speaker` comes from the portrait: a heroine's name, `other (...)` = an enemy/NPC shown on the
right (identify from context), `none` = narration, an unseen voice or an NPC without a portrait.
Some JP uses odd glyphs: Ω in 無Ω = 無能 (useless); ＹＥＡＨ = YEAH.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII plus the glyphs ♪ ☆ ♥ only: straight quotes,
`...`, no tabs inside the English, no Japanese or fullwidth characters, no `\uXXXX`. No manual line breaks: the build
wraps each page to 2 lines x 160 px and adds pages when needed.

## Length
About 30 characters fit on one line, 2 lines per page. Aim for <= ~60 characters per row; longer is fine when the
meaning needs it (it simply becomes an extra page). Never cut meaning to fit. Dry-run: `python -X utf8 tools/fit.py "text"`.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` and fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese
  doesn't state; don't summarise or skip. Adapt jokes and wordplay so they still land (no translator notes).
- Names and terms exactly as in the glossary. Honorifics dropped (小運様 -> "Lord Koun", 殿 -> "my lord").
- Pure ellipsis pages (・・・・・・) -> `...` or `.........` (keep similar length feel). Grunts: "Ngh!", "Hah!", "Gwaaah!".
- Inner thoughts in （） stay in parentheses.
- Rows split mid-sentence across pages (e.g. "With these ..." / "...into eternal hell!") must read in sequence.

## Consistency
Never edit `glossary.md` or any file other than your output. For a recurring name or term not in the glossary, pick a
form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.

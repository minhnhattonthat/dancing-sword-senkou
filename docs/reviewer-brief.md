# Translation reviewer brief - Dancing Sword: Senkou

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, encodable characters, width) is already enforced by the check tool - judge translation quality.
Return the report as your final message.
Repo root: H:\translation\batch\projects\dancing-sword-senkou

## Inputs
- Pairs file `work/tl/<batch>.pairs.txt`: `>> id | [speaker] JP` then `EN:`; lines starting with three spaces are
  context (earlier pages of the same scene). Read ALL of it, in passes if large. Ids are `<block>.<page>`; blocks next
  to each other are usually the same scene played by each of the five heroines.
- `glossary.md` (rulings + voices at the top), `docs/style-reference.md`.
- Facts settled by the controller: Emilio is Luciel's little BROTHER (he). 白地 = "the White Land". Speaker "none"
  can be narration, an unseen voice, or an NPC; "other (portrait XX)" is an enemy/NPC on the right.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly; each heroine's voice (glossary Voices); parallel scenes across heroines.
- Things players caught that reviewers missed: jokes/wordplay losing their punch; abbreviated names; stock phrases
  that read awkwardly in English; one-letter name slips.
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, voice badly off)
#### Minor (style - deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN` (give the full suggested English for the row).
### Assessment
Approved | Needs fixes - one sentence why.

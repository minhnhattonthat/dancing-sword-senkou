# Dancing Sword - Senkou (GBA) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, here `C:/Users/Nathan/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game`; tools read the `SKILL` env var, else that path). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py build` -> build/dancing_sword_en.gba (checks the dump against `rom.sha1` first; `build.py marker` = marker build, `build.py identity` = JP rebuild == original)
- Check:    `python -X utf8 tools/check.py` (pytest + lint; the pre-commit hook runs this; `--strict` also fails untranslated)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/dancing_sword_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py SCENE [--rom build/dancing_sword_en.gba]` (scenes: `tools/debug/scenes.json`; `block:<table idx>` shows any dialogue block; never ask the user to play to a scene)
- Release:  `python -X utf8 build.py release` (BPS + README + zip in release/; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)
- Tour/QA:  `python -X utf8 tools/debug/tour.py --only NAME,..` (scenes.json); `tools/tour_text.py` checks every dialogue page's VRAM against a Python render.

## Paths
- Original ROM: `rom/Dancing Sword - Senkou (Japan).gba` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`; CRC32 E2316D47). Emulator: `tools/mesen/` (MesenCE 2.2.1, github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip + Firmware/gba_bios.bin via fetch_emu.py gba-bios; gitignored; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/NN.json` (one entry per original page; `en` is one paragraph, the build wraps to 160 px x 2 lines and adds pages). Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- Code: `asm/vwf.s` (VWF, keystone via tools/asm.py), font `tools/font_en.py`, graphics `tools/gfx.py`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Commit as minhnhattonthat with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.

# Dancing Sword - Senkou (GBA) English translation

Skill: translate-retro-game (H:\translation\batch\.claude\skills\translate-retro-game\SKILL.md). Read it before ROM, text or QA work. `$SKILL` = that dir.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py build` -> build/dancing_sword_en.gba (`build.py marker` = marker build, `build.py identity` = JP rebuild == original)
- Check:    `python -X utf8 tools/check.py` (pytest + lint; the pre-commit hook runs this; `--strict` also fails untranslated)
- Smoke:    `python -X utf8 H:/translation/batch/.claude/skills/translate-retro-game/scripts/emu.py build/dancing_sword_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py SCENE [--rom build/dancing_sword_en.gba]` (scenes: `tools/debug/scenes.json`; `block:<table idx>` shows any dialogue block; never ask the user to play to a scene)
- Release:  `python -X utf8 build.py release` (BPS + README + zip in release/; never publish)

## Paths
- Original ROM: `rom/Dancing Sword - Senkou (Japan).gba` (gitignored; CRC32 E2316D47, SHA-1 5c5f33e0453cba1a60039160564daa53a82db8aa). Emulator: `tools/mesen/` (MesenCE 2.2.1, github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip + Firmware/gba_bios.bin via fetch_emu.py gba-bios; gitignored; settings copy in `tools/emu-config/`). States: `work/states/`.
- Text: `script/NN.json` (one entry per original page; `en` is one paragraph, the build wraps to 160 px x 2 lines and adds pages). Glossary + rulings: `glossary.md`. RE notes: `docs/re/` (text.md, graphics.md).
- Code: `asm/vwf.s` (VWF, keystone via tools/asm.py), font `tools/font_en.py`, graphics `tools/gfx.py`.

## Rulings (pre-approved by the user)
- Edit source files only with the file-edit tool. Full names, no abbreviations (engine work first). Honorifics dropped; given name first. Romanization: official > earlier patch > Hepburn. Credits in English. Graphics text in scope.
- Commit as minhnhattonthat with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never push/publish/upload.

## Status
- Done: Step 0, recon, debug tool (block viewer, scene warps incl. endings via scene id 22), identity test, VWF + relocation, width gate (160 px x 2 lines, both boxes), full translation (5 batches + reviews + fixes), graphics (crawl, title, char-select names, credits card). Next: dialogue screen tour (`tools/tour_text.py`), release (`build.py release`). Open bugs: none.
- Tour/QA: `python -X utf8 tools/debug/tour.py --only NAME,..` (scenes.json); `tools/tour_text.py` checks every dialogue page's VRAM against a Python render.

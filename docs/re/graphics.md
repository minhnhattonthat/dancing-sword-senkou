# Graphics-text survey

Toured with `tools/debug/tour.py` (scenes.json) and the ending warp (scene id 22). Everything not listed was
already English in the original (menus, options, battle record, key configuration, HUD, READY, SURVIVAL card,
Combo Tips, staff roll names/roles, "Thank you for Playing").

| Screen | Scene | Layer / source | Status |
|---|---|---|---|
| Opening crawl (8 lines JP) | `intro` | BG2 4bpp pal 4; tiles raw 0x3B6C24 (430 tiles), map 0x3B9EE4 (0x800); loader 0x08035A92 | English, re-rendered (tools/gfx.py intro_image, 412 tiles), tiles+map relocated to 0x7F0000+ |
| Title logo subtitle 閃光 + katakana ruby ダンシングソード | `title` | BG3 8bpp full image, tiles raw 0x3440E4, map 0x34B864 | 閃光 -> "Senkou", ruby painted over (gfx.title_edit) |
| Character-select names (5, vertical) | `charselect` | BG1 4bpp pal 11, per heroine tiles (70 at tile 0x60) + 32x32 map; loaders 0x080344F2.. | English rotated 90 deg (gfx.charselect), new tiles+maps in 0x7F0000+ |
| Staff-roll title card "DANCING SWORD -- 閃光 --" | `ending_*` | BG0 4bpp, tiles raw 0x4D38A4 (+32*t), tiles 0x36-0x39/0x3D-0x40 | "Senkou" (gfx.credits_edit, in place) |
| "Charactor Select" sidebar | `charselect` | graphics | original English (typo kept) |

Scene machine: byte 0x0300199A indexes the init/loop table 0x0879AC64 (main loop 0x080001E0). 22 = ending init
(table[0x91 + char + 5*part], part 0x0300007A), then epilogue and staff roll. Character 0x03000016 (0-4).

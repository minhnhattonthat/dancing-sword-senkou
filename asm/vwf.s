@ Dialogue VWF. Replaces DrawString (0x08037184, r0 = line string, returns cells used for the typewriter).
@ The original converted SJIS to fixed 8x16 cells at [0x0300547C] (20 cells/line, 0x40 bytes each, OBJ 1D).
@ This renders ASCII (0x20..0x83, NUL-terminated) proportionally across those 20 cells (160 px).
@ Assembled by tools/asm.py at VWF_BASE; GLYPHS / WIDTHS words are patched in by the build (see asm.py).
.thumb
vwf_draw:
    push {r4-r7, lr}
    mov r4, r8
    mov r5, r9
    mov r6, r10
    mov r7, r11
    push {r4-r7}
    mov r8, r0
    ldr r0, lit_destp
    ldr r0, [r0]
    mov r9, r0
    movs r1, #0
    ldr r2, lit_clr
    adds r2, r0, r2
clr_loop:
    str r1, [r0]
    adds r0, #4
    cmp r0, r2
    blo clr_loop
    movs r7, #0
char_loop:
    mov r0, r8
    ldrb r1, [r0]
    cmp r1, #0
    beq done
    adds r0, #1
    mov r8, r0
    subs r1, #0x20
    blo char_loop
    cmp r1, #NGLYPH
    bhs char_loop
    ldr r2, lit_widths
    ldrb r6, [r2, r1]
    ldr r2, lit_glyphs
    lsls r1, r1, #4
    adds r5, r2, r1
    movs r4, #0
row_loop:
    ldrb r0, [r5, r4]
    mov r10, r0
    lsls r1, r0, #1
    bics r1, r0
    movs r0, r1
    movs r1, #2
    bl draw_bits
    mov r0, r10
    movs r1, #1
    bl draw_bits
    adds r4, #1
    cmp r4, #16
    blo row_loop
    adds r7, r7, r6
    b char_loop
done:
    adds r0, r7, #7
    lsrs r0, r0, #3
    cmp r0, #20
    bls ret
    movs r0, #20
ret:
    pop {r4-r7}
    mov r8, r4
    mov r9, r5
    mov r10, r6
    mov r11, r7
    pop {r4-r7}
    pop {r1}
    bx r1

@ r0 = row bits (LSB = pen x), r1 = colour; y = r4, pen = r7
draw_bits:
    push {r5, r6, lr}
    movs r5, r0
    mov r12, r1
    movs r6, r7
db_loop:
    cmp r5, #0
    beq db_end
    lsrs r5, r5, #1
    bcc db_next
    cmp r6, #160
    bhs db_next
    movs r0, r6
    mov r1, r12
    bl plot
db_next:
    adds r6, #1
    b db_loop
db_end:
    pop {r5, r6}
    pop {r0}
    bx r0

@ r0 = x, r1 = colour, r4 = y; clobbers r0-r3. VRAM takes 16-bit writes only.
plot:
    lsrs r2, r0, #3
    lsls r2, r2, #6
    lsrs r3, r4, #3
    lsls r3, r3, #5
    adds r2, r2, r3
    lsls r3, r4, #29
    lsrs r3, r3, #27
    adds r2, r2, r3
    lsls r3, r0, #29
    lsrs r3, r3, #29
    lsrs r0, r3, #2
    lsls r0, r0, #1
    adds r2, r2, r0
    add r2, r9
    lsls r3, r3, #30
    lsrs r3, r3, #28
    lsls r1, r3
    movs r0, #15
    lsls r0, r3
    ldrh r3, [r2]
    bics r3, r0
    orrs r3, r1
    strh r3, [r2]
    bx lr

.align 2
lit_destp:  .word 0x0300547C
lit_clr:    .word 0x500
lit_glyphs: .word GLYPHS
lit_widths: .word WIDTHS

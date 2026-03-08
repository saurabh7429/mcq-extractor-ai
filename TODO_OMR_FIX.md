# OMR Layout Fix Plan - COMPLETED

## Issues Fixed in `export_omr_separate_pdf`:

1. ✅ **Bubble spacing**: Changed from 20 to 18px
2. ✅ **Bubble radius**: Set to 6px (12px diameter)
3. ✅ **Row spacing**: Changed from 24 to 22px
4. ✅ **Option letter position**: Draw BEFORE bubble (A ○ B ○ C ○ D ○)
5. ✅ **Question number alignment**: Aligned with first bubble horizontally
6. ✅ **No overlap**: Proper spacing calculations (radius*2 + spacing = 12 + 18 = 30px per bubble)
7. ✅ **Margins**: Kept at 40px (MARGIN = 40*mm)
8. ✅ **Dynamic layout**: Layout generates based on number of questions

## Implementation Details:

### Fixed `_draw_omr_bubbles_grid` method:
- BUBBLE_RADIUS = 6 (12px diameter)
- BUBBLE_SPACING = 18 (between bubbles)
- ROW_SPACING = 22 (between rows)
- Option letter drawn BEFORE bubble using `c.drawString(..., opt_label)`
- Question number aligned with bubble row


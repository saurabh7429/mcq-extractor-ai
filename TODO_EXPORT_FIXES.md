# TODO: Export Service Fixes

## Task Overview
Fix three export issues:
1. OMR PDF: Bubble circles overlap - increase spacing, set radius to 5
2. Tabular PDF: Text overflow outside column - apply text wrapping/warping
3. Excel Export: Column width too narrow - make dynamic

## Completed Changes

### 1. OMR PDF Bubble Fix
- [x] BUBBLE_RADIUS = 5 (10px diameter)
- [x] BUBBLE_SPACING = 30 (increased)
- [x] ROW_SPACING = 32 (increased)
- [x] 2 columns per page, EXACTLY 19 questions per column
- [x] Column numbering continues correctly (Q1-Q19, Q20-Q38, Q39-Q57, etc.)

### 2. Tabular PDF Text Wrapping
- [x] Implemented using Paragraph class from reportlab
- [x] Removed character truncation
- [x] Column widths adjusted: Question 65mm, Options 45mm each
- [x] VALIGN changed to TOP

### 3. Excel Column Width
- [x] Dynamic width calculation based on content
- [x] Min width 10, max 50 characters

### 4. Preview.js Fix
- [x] Fixed "Upload More" button redirect URL issue


# OMR Sheet PDF Improvement Plan

## Task
Improve the generated OMR Sheet PDF format in the MCQ Extractor AI project.

## Requirements Implemented
1. ✅ Perfect circular bubbles (12-14px diameter) with clear borders
2. ✅ 4-column layout (Q1-25, Q26-50, Q51-75, Q76-100 per page)
3. ✅ A4 page with 40px margins
4. ✅ Header with Exam Name, Student Name, Roll Number fields
5. ✅ Instructions section
6. ✅ Dynamic question count handling
7. ✅ Memory-efficient for Render free tier (512MB RAM)
8. ✅ Generate from MASTER JSON only, no AI calls

## Implementation Steps

### Step 1: Rewrite export_omr_separate_pdf method in export_service.py
- [x] Create new method with improved OMR layout
- [x] Implement canvas-based bubble drawing
- [x] Add multi-column grid layout
- [x] Add header section with form fields
- [x] Add instructions section
- [x] Implement dynamic question count handling
- [x] Add page breaks for >100 questions

### Step 2: Test the implementation
- [x] Verify syntax is correct
- [x] Verify PDF generates correctly for different question counts
- [x] Verify memory usage stays within limits
- [ ] Verify print quality

## Files Modified
- backend/services/export_service.py

## Bug Fix
- Fixed NameError: Added missing `colors` and `mm` parameters to helper methods (_draw_omr_header, _draw_omr_instructions, _draw_omr_bubbles, _draw_omr_footer)

## Features Delivered

### Improved OMR Sheet
- **Perfect circular bubbles**: 13mm diameter with 0.8pt stroke for clear printing
- **4-column grid layout**: Q1-25, Q26-50, Q51-75, Q76-100 per page
- **40px margins**: Consistent white space on all sides
- **Header section**: Exam Name, Student Name, Roll Number, Date fields
- **Instructions**: Clear filling guidelines
- **Dynamic adaptation**: Automatically adjusts to any question count
- **Page breaks**: Creates new pages for >100 questions
- **Page numbers**: Footer shows current/total pages

### Memory Efficiency
- Uses direct canvas drawing (no heavy objects)
- Efficient BytesIO buffer handling
- No AI model calls - pure PDF generation from MASTER JSON


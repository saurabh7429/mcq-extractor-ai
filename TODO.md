# TODO: Print-Ready Export Formats Implementation

## Task
Extend the export system with print-ready formats using lightweight libraries (reportlab, python-docx)

## New Formats Implemented
- [x] 1. Question Paper PDF (questions + MCQs only)
- [x] 2. Answer Key PDF (question IDs + answers)
- [x] 3. OMR Sheet PDF (questions + OMR sheet at end)
- [x] 4. Tabular PDF (7 columns: Q#, Question, Opt1-4, Answer)
- [x] 5. DOCX Question Paper

## Implementation Steps Completed
- [x] 1. Update requirements.txt - Added reportlab, python-docx
- [x] 2. Update backend/services/export_service.py - Added 5 new export methods
- [x] 3. Update backend/routes/download.py - Added route handlers and MIME types
- [x] 4. Update frontend/js/preview.js - Added format definitions and dropdown handling
- [x] 5. Update frontend/preview.html - Added Print Formats dropdown button

## Installation Required
Run the following to install new dependencies:
```
pip install reportlab python-docx
```

## Memory Considerations
- Uses streaming/incremental PDF generation with reportlab
- Process MCQs in batches
- Compatible with Render free tier (512MB RAM)


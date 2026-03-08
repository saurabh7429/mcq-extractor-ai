# TODO: File Upload Security Improvements

## Task List

### Step 1: Update Configuration (backend/config.py)
- [x] Change MAX_CONTENT_LENGTH from 10MB to 20MB

### Step 2: Update File Validator (backend/utils/file_validator.py)
- [x] Change MAX_FILE_SIZE from 10MB to 20MB
- [x] Add MAX_PAGES = 50 constant
- [x] Add validate_page_count() method

### Step 3: Implement Rate Limiting (backend/routes/upload.py)
- [x] Add in-memory rate limiter using Flask-Limiter or custom implementation
- [x] Configure: 15 uploads per minute per IP

### Step 4: Update Upload Route (backend/routes/upload.py)
- [x] Add page count validation after PDF is read
- [x] Add temporary file cleanup after processing
- [x] Standardize error responses to {"success": false, "message": "..."}
- [x] Wrap all code in proper error handling

### Step 5: Add Cleanup Utility
- [x] Create cleanup function to delete files older than 1 hour

## Status: COMPLETED


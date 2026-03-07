"""
Unit tests for PDF Reader service.
"""
import unittest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.pdf_reader import PDFReader, PDFReadError, PDFNoTextError


class TestPDFReader(unittest.TestCase):
    """Test cases for PDFReader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = PDFReader()
        self.test_data_dir = Path(__file__).parent.parent / 'tests' / 'data'
        self.test_data_dir.mkdir(exist_ok=True)
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        # Test multiple spaces
        text_with_spaces = "This   has    multiple   spaces"
        result = self.reader._clean_text(text_with_spaces)
        self.assertEqual(result, "This has multiple spaces")
        
        # Test multiple newlines
        text_with_newlines = "Line 1\n\n\nLine 2\n\n\nLine 3"
        result = self.reader._clean_text(text_with_newlines)
        self.assertEqual(result, "Line 1\nLine 2\nLine 3")
        
        # Test leading/trailing whitespace
        text_with_whitespace = "  Hello World  \n  Test  "
        result = self.reader._clean_text(text_with_whitespace)
        self.assertEqual(result, "Hello World\nTest")
        
        # Test empty lines removal
        text_with_empty_lines = "Line 1\n\n\n\nLine 2"
        result = self.reader._clean_text(text_with_empty_lines)
        self.assertEqual(result, "Line 1\nLine 2")
    
    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        result = self.reader._clean_text("")
        self.assertEqual(result, "")
        
        result = self.reader._clean_text(None)
        self.assertEqual(result, "")
    
    def test_clean_text_mixed(self):
        """Test cleaning text with mixed whitespace."""
        text = "  This   is   a    test  \n\n  with   multiple   newlines  \n\n\n"
        result = self.reader._clean_text(text)
        self.assertEqual(result, "This is a test\nwith multiple newlines")
    
    def test_pdf_read_error_exception(self):
        """Test PDFReadError exception."""
        error = PDFReadError("Test error message")
        self.assertEqual(str(error), "Test error message")
    
    def test_pdf_no_text_error_exception(self):
        """Test PDFNoTextError exception."""
        error = PDFNoTextError("No text found")
        self.assertEqual(str(error), "No text found")
    
    def test_get_page_count_nonexistent_file(self):
        """Test get_page_count with nonexistent file."""
        result = self.reader.get_page_count("/nonexistent/file.pdf")
        self.assertEqual(result, 0)
    
    def test_read_pdf_nonexistent_file(self):
        """Test read_pdf with nonexistent file."""
        with self.assertRaises(PDFReadError):
            self.reader.read_pdf("/nonexistent/file.pdf")
    
    def test_extract_page_text_nonexistent_file(self):
        """Test extract_page_text with nonexistent file."""
        with self.assertRaises(PDFReadError):
            self.reader.extract_page_text("/nonexistent/file.pdf", 1)
    
    def test_is_scanned_nonexistent_file(self):
        """Test is_scanned with nonexistent file."""
        # Should handle error gracefully
        result = self.reader.is_scanned("/nonexistent/file.pdf")
        self.assertTrue(result)  # Returns True on error
    
    def test_read_pdf_from_storage_invalid_id(self):
        """Test read_pdf_from_storage with invalid file_id."""
        with self.assertRaises(PDFReadError):
            self.reader.read_pdf_from_storage("invalid-file-id-123")


class TestPDFReaderIntegration(unittest.TestCase):
    """Integration tests for PDFReader (requires actual PDF file)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = PDFReader()
        self.test_data_dir = Path(__file__).parent.parent / 'tests' / 'data'
        self.test_data_dir.mkdir(exist_ok=True)
    
    def test_extract_text_page_by_page_empty_pdf(self):
        """Test page by page extraction with mock PDF."""
        # Since we can't easily create a real PDF in tests,
        # we test the method signatures exist
        self.assertTrue(hasattr(self.reader, '_extract_text_by_page'))
        self.assertTrue(hasattr(self.reader, 'read_pdf'))
        self.assertTrue(hasattr(self.reader, 'read_pdf_from_storage'))


if __name__ == '__main__':
    unittest.main()

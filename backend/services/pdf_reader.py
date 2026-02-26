"""
PDF Reader service - handles reading PDF files.
"""
import logging
import re
from typing import Any, List, Tuple
from pathlib import Path
from io import BytesIO

# Create logger
logger = logging.getLogger(__name__)


class PDFReadError(Exception):
    """Custom exception for PDF reading errors."""
    pass


class PDFNoTextError(Exception):
    """Custom exception raised when no text is found in PDF."""
    pass


class PDFReader:
    """Handles reading and extracting text from PDF files."""
    
    def __init__(self):
        """Initialize PDF reader."""
        logger.info("PDF Reader initialized")
    
    def read_pdf(self, file_or_path) -> str:
        """
        Read text content from a PDF file using pdfplumber.
        
        Args:
            file_or_path: Either a file path (str/Path) or file object (FileStorage)
        
        Returns:
            Extracted text content as clean string
        
        Raises:
            PDFReadError: If PDF cannot be read
            PDFNoTextError: If no text is found in PDF
        """
        try:
            import pdfplumber
        except ImportError:
            logger.error("pdfplumber is not installed")
            raise PDFReadError("PDF processing library not available. Please install pdfplumber: pip install pdfplumber")
        
        try:
            # Check if it's a file path or file object
            if hasattr(file_or_path, 'read'):
                return self._read_pdf_from_file_object(file_or_path)
            else:
                return self._read_pdf_from_path(file_or_path)
                
        except (PDFNoTextError, FileNotFoundError):
            raise
        except Exception as e:
            logger.exception(f"Error reading PDF: {str(e)}")
            raise PDFReadError(f"Failed to read PDF: {str(e)}")
    
    def _read_pdf_from_path(self, file_path: str) -> str:
        """Read PDF from file path."""
        import pdfplumber
        
        with pdfplumber.open(file_path) as pdf:
            logger.info(f"Opened PDF with {len(pdf.pages)} pages")
            text_content = self._extract_text_by_page(pdf)
            
            if not text_content:
                logger.warning("PDF appears to be empty, trying OCR...")
                ocr_text = self._extract_text_using_ocr(file_path)
                if ocr_text:
                    logger.info(f"OCR extracted {len(ocr_text)} characters from PDF")
                    return self._clean_text(ocr_text)
                
                # Detailed error message for user
                ocr_available = self._check_ocr_available()
                if not ocr_available:
                    raise PDFNoTextError(
                        "No text found in PDF. The PDF appears to be scanned/image-based. "
                        "OCR support is not installed. Please install: pip install pytesseract pdf2image "
                        "And also install Tesseract OCR on your system."
                    )
                else:
                    raise PDFNoTextError(
                        "No text found in PDF. The PDF appears to be scanned/image-based. "
                        "OCR extraction failed. Please ensure Tesseract OCR is installed on your system."
                    )
            
            full_text = '\n'.join(text_content)
            clean_text = self._clean_text(full_text)
            logger.info(f"Extracted {len(clean_text)} characters from PDF")
            return clean_text
    
    def _read_pdf_from_file_object(self, file) -> str:
        """Read PDF from file object."""
        import pdfplumber
        
        file_content = file.read()
        pdf_file = BytesIO(file_content)
        
        with pdfplumber.open(pdf_file) as pdf:
            logger.info(f"Opened PDF with {len(pdf.pages)} pages")
            text_content = self._extract_text_by_page(pdf)
            
            if not text_content:
                logger.warning("PDF appears to be empty, trying OCR...")
                ocr_text = self._extract_text_using_ocr_from_bytes(file_content)
                if ocr_text:
                    logger.info(f"OCR extracted {len(ocr_text)} characters from PDF")
                    return self._clean_text(ocr_text)
                
                # Detailed error message for user
                ocr_available = self._check_ocr_available()
                if not ocr_available:
                    raise PDFNoTextError(
                        "No text found in PDF. The PDF appears to be scanned/image-based. "
                        "OCR support is not installed. Please install: pip install pytesseract pdf2image "
                        "And also install Tesseract OCR on your system."
                    )
                else:
                    raise PDFNoTextError(
                        "No text found in PDF. The PDF appears to be scanned/image-based. "
                        "OCR extraction failed. Please ensure Tesseract OCR is installed on your system."
                    )
            
            full_text = '\n'.join(text_content)
            clean_text = self._clean_text(full_text)
            logger.info(f"Extracted {len(clean_text)} characters from PDF")
            return clean_text
    
    def _extract_text_by_page(self, pdf) -> List[str]:
        """Extract text from PDF page by page."""
        text_pages = []
        
        for page_num, page in enumerate(pdf.pages, start=1):
            try:
                text = page.extract_text()
                if text and text.strip():
                    text_pages.append(text)
                    logger.debug(f"Extracted {len(text)} chars from page {page_num}")
                else:
                    logger.warning(f"Page {page_num} contains no extractable text")
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                continue
        
        return text_pages
    
    def _check_ocr_available(self) -> bool:
        """Check if OCR (pytesseract) is available."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            logger.info("OCR (pytesseract) is available")
            return True
        except ImportError:
            logger.warning("pytesseract is not installed. Run: pip install pytesseract")
            return False
        except Exception as e:
            logger.warning(f"OCR not available: {str(e)}")
            return False
    
    def _extract_text_using_ocr(self, file_path: str) -> str:
        """Extract text from image-based PDF using OCR."""
        if not self._check_ocr_available():
            logger.warning("OCR not available, cannot process scanned PDF")
            return ""
        
        try:
            import pytesseract
            from pdf2image import convert_from_path
            logger.info("Starting OCR process for scanned PDF...")
            
            images = convert_from_path(file_path)
            
            text_pages = []
            for page_num, image in enumerate(images, start=1):
                logger.info(f"Processing page {page_num} with OCR...")
                text = pytesseract.image_to_string(image, lang='eng')
                if text and text.strip():
                    text_pages.append(text)
            
            if text_pages:
                full_text = '\n'.join(text_pages)
                logger.info(f"OCR extracted text from {len(text_pages)} pages")
                return full_text
            
            return ""
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            return ""
    
    def _extract_text_using_ocr_from_bytes(self, file_content: bytes) -> str:
        """Extract text from image-based PDF (bytes) using OCR."""
        if not self._check_ocr_available():
            logger.warning("OCR not available, cannot process scanned PDF")
            return ""
        
        try:
            import pytesseract
            from pdf2image import convert_from_bytes
            logger.info("Starting OCR process for scanned PDF (from bytes)...")
            
            images = convert_from_bytes(file_content)
            
            text_pages = []
            for page_num, image in enumerate(images, start=1):
                logger.info(f"Processing page {page_num} with OCR...")
                text = pytesseract.image_to_string(image, lang='eng')
                if text and text.strip():
                    text_pages.append(text)
            
            if text_pages:
                full_text = '\n'.join(text_pages)
                logger.info(f"OCR extracted text from {len(text_pages)} pages")
                return full_text
            
            return ""
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace from text."""
        if not text:
            return ""
        
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        return '\n'.join(lines)
    
    def extract_page_text(self, file_path: str, page_num: int) -> str:
        """Extract text from a specific page."""
        try:
            import pdfplumber
        except ImportError:
            raise PDFReadError("PDF processing library not available")
        
        try:
            with pdfplumber.open(file_path) as pdf:
                if page_num < 1 or page_num > len(pdf.pages):
                    raise PDFReadError(f"Page {page_num} does not exist. PDF has {len(pdf.pages)} pages.")
                
                page = pdf.pages[page_num - 1]
                text = page.extract_text()
                
                if not text or not text.strip():
                    raise PDFNoTextError(f"Page {page_num} contains no text.")
                
                return self._clean_text(text)
                
        except (PDFReadError, PDFNoTextError):
            raise
        except Exception as e:
            logger.exception(f"Error extracting page text: {str(e)}")
            raise PDFReadError(f"Failed to extract page text: {str(e)}")
    
    def get_page_count(self, file_path: str) -> int:
        """Get the number of pages in a PDF."""
        try:
            import pdfplumber
            
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                logger.info(f"PDF has {page_count} pages")
                return page_count
                
        except Exception as e:
            logger.error(f"Error getting page count: {str(e)}")
            return 0
    
    def is_scanned(self, file_path: str) -> bool:
        """Check if PDF is scanned (image-based)."""
        try:
            import pdfplumber
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages[:3]:
                    if page.extract_text() and page.extract_text().strip():
                        return False
                
                for page in pdf.pages[:3]:
                    if page.images:
                        return True
                
                return True
                
        except Exception as e:
            logger.error(f"Error checking if PDF is scanned: {str(e)}")
            return True
    
    def read_pdf_from_storage(self, file_id: str) -> Tuple[str, int]:
        """Read a stored PDF by file_id and extract text."""
        from backend.models.database import get_pdf_by_file_id
        
        pdf_file = get_pdf_by_file_id(file_id)
        
        if not pdf_file:
            logger.error(f"PDF file not found in database: {file_id}")
            raise PDFReadError(f"PDF file not found in database: {file_id}")
        
        file_path = Path(pdf_file.file_path)
        
        if not file_path.exists():
            logger.error(f"PDF file not found on disk: {file_path}")
            raise PDFReadError(f"PDF file not found on disk: {file_path}")
        
        page_count = self.get_page_count(str(file_path))
        text = self.read_pdf(str(file_path))
        
        return text, page_count

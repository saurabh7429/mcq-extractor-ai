"""Create a minimal test PDF file for testing upload."""
from PyPDF2 import PdfWriter
import io

# Create a minimal PDF
pdf_writer = PdfWriter()
pdf_writer.add_blank_page(width=200, height=200)

# Save to file
with open('test_sample.pdf', 'wb') as f:
    pdf_writer.write(f)

print("Test PDF created: test_sample.pdf")

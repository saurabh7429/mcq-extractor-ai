"""
Models package for database models.
"""
from backend.models.pdf_model import PDFFile
from backend.models.mcq_model import MCQ
from backend.models.database import (
    init_db,
    get_session,
    close_session,
    create_tables,
    create_pdf,
    get_pdf_by_id,
    get_all_pdfs,
    delete_pdf,
    create_mcq,
    create_mcqs_bulk,
    get_mcqs_by_pdf_id,
    get_mcq_by_id,
    delete_mcq
)

__all__ = [
    'PDFFile',
    'MCQ',
    'init_db',
    'get_session',
    'close_session',
    'create_tables',
    'create_pdf',
    'get_pdf_by_id',
    'get_all_pdfs',
    'delete_pdf',
    'create_mcq',
    'create_mcqs_bulk',
    'get_mcqs_by_pdf_id',
    'get_mcq_by_id',
    'delete_mcq'
]

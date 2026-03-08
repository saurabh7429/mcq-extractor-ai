"""
Export Service - handles exporting MCQ data to various formats locally.
No AI calls - all conversions done with Python logic.
"""
import json
import csv
import io
import logging
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)
OPTION_LETTERS = ['A', 'B', 'C', 'D']

class ExportService:
    def __init__(self):
        logger.info("Export Service initialized")
    
    def load_master_json(self, file_id: str) -> List[Dict[str, Any]]:
        from backend.services.storage_service import StorageService
        storage = StorageService()
        json_content = storage.get_json_by_uuid(file_id)
        if not json_content:
            raise ValueError(f"No JSON found for file_id: {file_id}")
        try:
            mcqs = json.loads(json_content)
            logger.info(f"Loaded {len(mcqs)} MCQs from MASTER JSON")
            return mcqs
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    
    def _ensure_four_options(self, options: List[str]) -> List[str]:
        while len(options) < 4:
            options.append('')
        return options[:4]
    
    def _get_correct_letter(self, correct_idx: int) -> str:
        return OPTION_LETTERS[correct_idx] if 0 <= correct_idx < 4 else 'A'
    
    # JSON
    def export_json(self, mcqs: List[Dict[str, Any]], pretty: bool = True) -> str:
        return json.dumps(mcqs, indent=2, ensure_ascii=False) if pretty else json.dumps(mcqs, ensure_ascii=False)
    
    # CSV
    def export_csv(self, mcqs: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer'])
        for mcq in mcqs:
            options = self._ensure_four_options(mcq.get('options', []))
            correct_idx = mcq.get('correct_answer', 0)
            writer.writerow([mcq.get('id', ''), mcq.get('question', ''), options[0], options[1], options[2], options[3], self._get_correct_letter(correct_idx)])
        return output.getvalue()
    
    # TXT
    def export_txt(self, mcqs: List[Dict[str, Any]]) -> str:
        lines = []
        for mcq in mcqs:
            options = self._ensure_four_options(mcq.get('options', []))
            correct_idx = mcq.get('correct_answer', 0)
            lines.append(f"Q{mcq.get('id', '')}: {mcq.get('question', '')}")
            for idx, option in enumerate(options):
                marker = " [CORRECT]" if idx == correct_idx else ""
                lines.append(f"   {OPTION_LETTERS[idx]}) {option}{marker}")
            lines.append("")
        return '\n'.join(lines)
    
    # Markdown
    def export_markdown(self, mcqs: List[Dict[str, Any]]) -> str:
        lines = ["# MCQ Questions", ""]
        for mcq in mcqs:
            options = self._ensure_four_options(mcq.get('options', []))
            correct_idx = mcq.get('correct_answer', 0)
            lines.append(f"## Question {mcq.get('id', '')}\n**{mcq.get('question', '')}**\n")
            for idx, option in enumerate(options):
                lines.append(f"- **{OPTION_LETTERS[idx]}) {option}** ✅" if idx == correct_idx else f"- {OPTION_LETTERS[idx]}) {option}")
            lines.append(f"\n*Answer: {self._get_correct_letter(correct_idx)}*\n---\n")
        return '\n'.join(lines)
    
    # HTML
    def export_html(self, mcqs: List[Dict[str, Any]]) -> str:
        html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>MCQ Questions</title></head><body><h1>MCQ Questions</h1>"
        for mcq in mcqs:
            options = self._ensure_four_options(mcq.get('options', []))
            correct_idx = mcq.get('correct_answer', 0)
            html += f"<div class='mcq'><h3>Q{mcq.get('id', '')}: {mcq.get('question', '')}</h3><ul>"
            for idx, option in enumerate(options):
                html += f"<li>{OPTION_LETTERS[idx]}) {option}</li>"
            html += f"</ul><p><strong>Answer: {self._get_correct_letter(correct_idx)}</strong></p></div>"
        return html + "</body></html>"
    
    # Excel (XLSX)
    def export_excel(self, mcqs: List[Dict[str, Any]]) -> bytes:
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill
            from io import BytesIO
            wb = Workbook()
            ws = wb.active
            ws.title = "MCQ Questions"
            headers = ['ID', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer']
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            for row_idx, mcq in enumerate(mcqs, 2):
                options = self._ensure_four_options(mcq.get('options', []))
                correct_idx = mcq.get('correct_answer', 0)
                for col_idx, val in enumerate([mcq.get('id', ''), mcq.get('question', '')] + options + [self._get_correct_letter(correct_idx)], 1):
                    ws.cell(row=row_idx, column=col_idx, value=val)
            output = BytesIO()
            wb.save(output)
            return output.getvalue()
        except ImportError:
            raise ValueError("Excel export requires openpyxl. Install with: pip install openpyxl")
    
    # XML
    def export_xml(self, mcqs: List[Dict[str, Any]]) -> str:
        lines = ['<?xml version="1.0" encoding="UTF-8"?><mcqs>']
        for mcq in mcqs:
            options = self._ensure_four_options(mcq.get('options', []))
            correct_idx = mcq.get('correct_answer', 0)
            lines.append(f"<mcq><id>{mcq.get('id', '')}</id><question>{mcq.get('question', '')}</question><options>")
            for idx, opt in enumerate(options):
                is_correct = 'true' if idx == correct_idx else 'false'
                lines.append(f"<option letter='{OPTION_LETTERS[idx]}' correct='{is_correct}'>{opt}</option>")
            lines.append("</options></mcq>")
        lines.append("</mcqs>")
        return '\n'.join(lines)
    
    # YAML
    def export_yaml(self, mcqs: List[Dict[str, Any]]) -> str:
        lines = ["# MCQ Questions Export", ""]
        for mcq in mcqs:
            options = self._ensure_four_options(mcq.get('options', []))
            correct_idx = mcq.get('correct_answer', 0)
            lines.append(f"- id: {mcq.get('id', '')}")
            lines.append(f'  question: "{mcq.get("question", "")}"')
            lines.append("  options:")
            lines.append(f'    A: "{options[0]}"')
            lines.append(f'    B: "{options[1]}"')
            lines.append(f'    C: "{options[2]}"')
            lines.append(f'    D: "{options[3]}"')
            lines.append(f"  answer: {self._get_correct_letter(correct_idx)}")
            lines.append("")
        return '\n'.join(lines)
    
    # SQL Insert Script
    def export_sql(self, mcqs: List[Dict[str, Any]], table_name: str = 'mcqs') -> str:
        lines = [
            "-- MCQ Questions SQL Insert Statements",
            "-- Generated by MCQ Extractor AI",
            "",
            f"CREATE TABLE IF NOT EXISTS {table_name} (",
            "    id INTEGER PRIMARY KEY,",
            "    question TEXT NOT NULL,",
            "    option_a TEXT NOT NULL,",
            "    option_b TEXT NOT NULL,",
            "    option_c TEXT NOT NULL,",
            "    option_d TEXT NOT NULL,",
            "    correct_answer CHAR(1) NOT NULL",
            ");",
            ""
        ]
        for mcq in mcqs:
            options = self._ensure_four_options(mcq.get('options', []))
            correct_idx = mcq.get('correct_answer', 0)
            q = mcq.get('question', '').replace("'", "''")
            opts = [opt.replace("'", "''") for opt in options]
            lines.append(f"INSERT INTO {table_name} (id, question, option_a, option_b, option_c, option_d, correct_answer) VALUES ({mcq.get('id', 0)}, '{q}', '{opts[0]}', '{opts[1]}', '{opts[2]}', '{opts[3]}', '{self._get_correct_letter(correct_idx)}');")
        return '\n'.join(lines)
    
    # Aiken Format
    def export_aiken(self, mcqs: List[Dict[str, Any]]) -> str:
        lines = []
        for mcq in mcqs:
            options = self._ensure_four_options(mcq.get('options', []))
            correct_idx = mcq.get('correct_answer', 0)
            lines.append(mcq.get('question', ''))
            for idx, option in enumerate(options):
                lines.append(f"{OPTION_LETTERS[idx]}) {option}")
            lines.append(f"ANSWER: {self._get_correct_letter(correct_idx)}")
            lines.append("")
        return '\n'.join(lines)
    
    # GIFT Format
    def export_gift(self, mcqs: List[Dict[str, Any]]) -> str:
        lines = ["// GIFT Format Export", "// Generated by MCQ Extractor AI", ""]
        for mcq in mcqs:
            options = self._ensure_four_options(mcq.get('options', []))
            correct_idx = mcq.get('correct_answer', 0)
            lines.append(f"::{mcq.get('id', '')}::{mcq.get('question', '')}{{")
            for idx, option in enumerate(options):
                prefix = '=' if idx == correct_idx else '~'
                lines.append(f"    {prefix}{option}")
            lines.append("}")
            lines.append("")
        return '\n'.join(lines)
    
    # ==================== NEW PRINT-READY FORMATS ====================
    
    # Question Paper PDF (questions + MCQs only, no answers)
    def export_question_pdf(self, mcqs: List[Dict[str, Any]]) -> bytes:
        """Export question paper as PDF without answers."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER
            from io import BytesIO
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=20*mm, rightMargin=20*mm)
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18,
                                        alignment=TA_CENTER, spaceAfter=20)
            question_style = ParagraphStyle('Question', parent=styles['Normal'], fontSize=11,
                                           spaceBefore=10, spaceAfter=5)
            option_style = ParagraphStyle('Option', parent=styles['Normal'], fontSize=10,
                                          leftIndent=20)
            
            story = []
            story.append(Paragraph("Question Paper", title_style))
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Total Questions: {len(mcqs)}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            for idx, mcq in enumerate(mcqs, 1):
                options = self._ensure_four_options(mcq.get('options', []))
                q_text = f"<b>Q{idx}.</b> {mcq.get('question', '')}"
                story.append(Paragraph(q_text, question_style))
                
                for opt_idx, option in enumerate(options):
                    opt_text = f"{OPTION_LETTERS[opt_idx]}) {option}"
                    story.append(Paragraph(opt_text, option_style))
                
                story.append(Spacer(1, 10))
                
                if idx % 25 == 0:
                    story.append(PageBreak())
            
            doc.build(story)
            return buffer.getvalue()
        except ImportError:
            raise ValueError("PDF export requires reportlab. Install with: pip install reportlab")
    
    # Answer Key PDF (only answers with question IDs)
    def export_answer_key_pdf(self, mcqs: List[Dict[str, Any]]) -> bytes:
        """Export answer key as PDF."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.enums import TA_CENTER
            from io import BytesIO
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=20*mm, rightMargin=20*mm)
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18,
                                        alignment=TA_CENTER, spaceAfter=20)
            
            story = []
            story.append(Paragraph("Answer Key", title_style))
            story.append(Spacer(1, 20))
            
            data = [['Q.No.', 'Answer']]
            for mcq in mcqs:
                q_id = mcq.get('id', '')
                correct_idx = mcq.get('correct_answer', 0)
                answer = self._get_correct_letter(correct_idx)
                data.append([str(q_id), answer])
            
            table = Table(data, colWidths=[50*mm, 30*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(table)
            doc.build(story)
            return buffer.getvalue()
        except ImportError:
            raise ValueError("PDF export requires reportlab. Install with: pip install reportlab")
    
    # OMR Integrated PDF - Type 2 (questions first, OMR sheet at end)
    def export_omr_separate_pdf(self, mcqs: List[Dict[str, Any]]) -> bytes:
        """Export PDF with questions first, then OMR sheet at the end."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.enums import TA_CENTER
            from io import BytesIO
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16,
                                        alignment=TA_CENTER, spaceAfter=10)
            
            story = []
            story.append(Paragraph("Question Paper", title_style))
            story.append(Spacer(1, 10))
            
            for idx, mcq in enumerate(mcqs, 1):
                options = self._ensure_four_options(mcq.get('options', []))
                q_text = f"<b>Q{idx}.</b> {mcq.get('question', '')}"
                story.append(Paragraph(q_text, styles['Normal']))
                story.append(Spacer(1, 3))
                
                for opt_idx, option in enumerate(options):
                    opt_text = f"{OPTION_LETTERS[opt_idx]}) {option}"
                    story.append(Paragraph(f"   {opt_text}", styles['Normal']))
                
                story.append(Spacer(1, 8))
                
                if idx % 25 == 0:
                    story.append(PageBreak())
            
            story.append(PageBreak())
            story.append(Paragraph("OMR Answer Sheet", title_style))
            story.append(Spacer(1, 20))
            
            omr_data = [['Q.No.', 'A', 'B', 'C', 'D']]
            rows = []
            for i in range(1, min(len(mcqs) + 1, 101)):
                rows.append([str(i), '( )', '( )', '( )', '( )'])
            
            while len(rows) < 25:
                rows.append(['', '', '', '', ''])
            
            omr_data.extend(rows)
            
            omr_table = Table(omr_data, colWidths=[30*mm, 25*mm, 25*mm, 25*mm, 25*mm])
            omr_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(omr_table)
            doc.build(story)
            return buffer.getvalue()
        except ImportError:
            raise ValueError("PDF export requires reportlab. Install with: pip install reportlab")
    
    # Tabular PDF (6 columns: Q#, Question, Opt1-4, Answer)
    def export_tabular_pdf(self, mcqs: List[Dict[str, Any]]) -> bytes:
        """Export MCQs in tabular format PDF."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from io import BytesIO
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=10*mm, 
                                   bottomMargin=10*mm, leftMargin=10*mm, rightMargin=10*mm)
            
            data = [['Q.No.', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Answer']]
            
            for mcq in mcqs:
                q_id = str(mcq.get('id', ''))
                question = mcq.get('question', '')[:80]
                options = self._ensure_four_options(mcq.get('options', []))
                correct_idx = mcq.get('correct_answer', 0)
                answer = self._get_correct_letter(correct_idx)
                
                data.append([
                    q_id,
                    question,
                    options[0][:40] if options[0] else '',
                    options[1][:40] if options[1] else '',
                    options[2][:40] if options[2] else '',
                    options[3][:40] if options[3] else '',
                    answer
                ])
            
            table = Table(data, colWidths=[20*mm, 50*mm, 40*mm, 40*mm, 40*mm, 40*mm, 20*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            doc.build([table])
            return buffer.getvalue()
        except ImportError:
            raise ValueError("PDF export requires reportlab. Install with: pip install reportlab")
    
    # DOCX Question Paper
    def export_docx(self, mcqs: List[Dict[str, Any]]) -> bytes:
        """Export question paper as DOCX."""
        try:
            from docx import Document
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from io import BytesIO
            
            doc = Document()
            
            title = doc.add_heading('Question Paper', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph(f'Total Questions: {len(mcqs)}')
            doc.add_paragraph()
            
            for idx, mcq in enumerate(mcqs, 1):
                options = self._ensure_four_options(mcq.get('options', []))
                
                q_para = doc.add_paragraph()
                q_run = q_para.add_run(f'Q{idx}. {mcq.get("question", "")}')
                q_run.bold = True
                
                for opt_idx, option in enumerate(options):
                    opt_para = doc.add_paragraph(f'   {OPTION_LETTERS[opt_idx]}) {option}')
                
                doc.add_paragraph()
            
            buffer = BytesIO()
            doc.save(buffer)
            return buffer.getvalue()
        except ImportError:
            raise ValueError("DOCX export requires python-docx. Install with: pip install python-docx")
    
    # Main export method
    def export(self, file_id: str, format: str) -> Union[str, bytes]:
        mcqs = self.load_master_json(file_id)
        if not mcqs:
            raise ValueError("No MCQs found in the file")
        
        fmt = format.lower()
        
        if fmt == 'json':
            return self.export_json(mcqs)
        elif fmt == 'csv':
            return self.export_csv(mcqs)
        elif fmt == 'txt':
            return self.export_txt(mcqs)
        elif fmt == 'markdown':
            return self.export_markdown(mcqs)
        elif fmt == 'html':
            return self.export_html(mcqs)
        elif fmt == 'xml':
            return self.export_xml(mcqs)
        elif fmt == 'yaml':
            return self.export_yaml(mcqs)
        elif fmt == 'sql':
            return self.export_sql(mcqs)
        elif fmt == 'aiken':
            return self.export_aiken(mcqs)
        elif fmt == 'gift':
            return self.export_gift(mcqs)
        elif fmt == 'excel':
            return self.export_excel(mcqs)
        # New print-ready formats
        elif fmt == 'question_pdf':
            return self.export_question_pdf(mcqs)
        elif fmt == 'answer_key_pdf':
            return self.export_answer_key_pdf(mcqs)
        elif fmt == 'omr_pdf':
            return self.export_omr_separate_pdf(mcqs)
        elif fmt == 'tabular_pdf':
            return self.export_tabular_pdf(mcqs)
        elif fmt == 'docx':
            return self.export_docx(mcqs)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_supported_formats(self) -> List[str]:
        return ['json', 'csv', 'txt', 'markdown', 'html', 'xml', 'yaml', 'sql', 'aiken', 'gift', 'excel',
                'question_pdf', 'answer_key_pdf', 'omr_pdf', 'tabular_pdf', 'docx']


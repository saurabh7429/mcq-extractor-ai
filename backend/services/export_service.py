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
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_supported_formats(self) -> List[str]:
        return ['json', 'csv', 'txt', 'markdown', 'html', 'xml', 'yaml', 'sql', 'aiken', 'gift', 'excel']

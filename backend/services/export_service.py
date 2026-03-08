"""
Export Service - handles exporting MCQ data to various formats locally.
No AI calls - all conversions done with Python logic.
"""
import json
import csv
import io
import logging
from typing import List, Dict, Any
from pathlib import Path

# Create logger
logger = logging.getLogger(__name__)

# Letter mapping for options
OPTION_LETTERS = ['A', 'B', 'C', 'D']


class ExportService:
    """Handles exporting MCQ data to various formats."""
    
    def __init__(self):
        """Initialize export service."""
        logger.info("Export Service initialized")
    
    def load_master_json(self, file_id: str) -> List[Dict[str, Any]]:
        """
        Load MASTER JSON from storage.
        
        Args:
            file_id: The UUID of the file
            
        Returns:
            List of MCQ dictionaries
        """
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
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
    
    # ==================== JSON Export ====================
    
    def export_json(self, mcqs: List[Dict[str, Any]], pretty: bool = True) -> str:
        """
        Export MCQs to JSON format.
        
        Args:
            mcqs: List of MCQ dictionaries
            pretty: Whether to pretty-print the JSON
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(mcqs, indent=2, ensure_ascii=False)
        return json.dumps(mcqs, ensure_ascii=False)
    
    # ==================== CSV Export ====================
    
    def export_csv(self, mcqs: List[Dict[str, Any]]) -> str:
        """
        Export MCQs to CSV format.
        
        Args:
            mcqs: List of MCQ dictionaries
            
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer'])
        
        # Write MCQs
        for mcq in mcqs:
            question = mcq.get('question', '')
            options = mcq.get('options', [])
            correct_idx = mcq.get('correct_answer', 0)
            
            # Ensure we have 4 options
            while len(options) < 4:
                options.append('')
            options = options[:4]
            
            # Get correct answer letter
            correct_letter = OPTION_LETTERS[correct_idx] if 0 <= correct_idx < 4 else 'A'
            
            writer.writerow([
                mcq.get('id', ''),
                question,
                options[0] if len(options) > 0 else '',
                options[1] if len(options) > 1 else '',
                options[2] if len(options) > 2 else '',
                options[3] if len(options) > 3 else '',
                correct_letter
            ])
        
        return output.getvalue()
    
    # ==================== TXT Export ====================
    
    def export_txt(self, mcqs: List[Dict[str, Any]]) -> str:
        """
        Export MCQs to plain text format.
        
        Args:
            mcqs: List of MCQ dictionaries
            
        Returns:
            TXT string
        """
        lines = []
        
        for mcq in mcqs:
            question = mcq.get('question', '')
            options = mcq.get('options', [])
            correct_idx = mcq.get('correct_answer', 0)
            
            # Ensure we have 4 options
            while len(options) < 4:
                options.append('')
            options = options[:4]
            
            lines.append(f"Q{mcq.get('id', '')}: {question}")
            
            for idx, option in enumerate(options):
                letter = OPTION_LETTERS[idx]
                marker = " [CORRECT]" if idx == correct_idx else ""
                lines.append(f"   {letter}) {option}{marker}")
            
            lines.append("")  # Empty line between questions
        
        return '\n'.join(lines)
    
    # ==================== Markdown Export ====================
    
    def export_markdown(self, mcqs: List[Dict[str, Any]]) -> str:
        """
        Export MCQs to Markdown format.
        
        Args:
            mcqs: List of MCQ dictionaries
            
        Returns:
            Markdown string
        """
        lines = []
        lines.append("# MCQ Questions")
        lines.append("")
        
        for mcq in mcqs:
            question = mcq.get('question', '')
            options = mcq.get('options', [])
            correct_idx = mcq.get('correct_answer', 0)
            
            # Ensure we have 4 options
            while len(options) < 4:
                options.append('')
            options = options[:4]
            
            lines.append(f"## Question {mcq.get('id', '')}")
            lines.append("")
            lines.append(f"**{question}**")
            lines.append("")
            
            for idx, option in enumerate(options):
                letter = OPTION_LETTERS[idx]
                if idx == correct_idx:
                    lines.append(f"- **{letter}) {option}** ✅")
                else:
                    lines.append(f"- {letter}) {option}")
            
            lines.append("")
            lines.append(f"*Answer: {OPTION_LETTERS[correct_idx]}*")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return '\n'.join(lines)
    
    # ==================== HTML Export ====================
    
    def export_html(self, mcqs: List[Dict[str, Any]]) -> str:
        """
        Export MCQs to HTML format.
        
        Args:
            mcqs: List of MCQ dictionaries
            
        Returns:
            HTML string
        """
        html_parts = []
        
        # HTML header
        html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCQ Questions</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .mcq {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: #f9f9f9;
        }
        .question {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .options {
            list-style: none;
            padding: 0;
        }
        .options li {
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 4px;
            border: 1px solid #eee;
        }
        .options li.correct {
            background: #d4edda;
            border-color: #c3e6cb;
            font-weight: bold;
        }
        .answer {
            margin-top: 10px;
            font-size: 14px;
            color: #28a745;
        }
    </style>
</head>
<body>
    <h1>MCQ Questions</h1>
""")
        
        # MCQs
        for mcq in mcqs:
            question = mcq.get('question', '')
            options = mcq.get('options', [])
            correct_idx = mcq.get('correct_answer', 0)
            
            # Ensure we have 4 options
            while len(options) < 4:
                options.append('')
            options = options[:4]
            
            html_parts.append(f'    <div class="mcq">')
            html_parts.append(f'        <div class="question">Q{mcq.get("id", "")}: {self._escape_html(question)}</div>')
            html_parts.append('        <ul class="options">')
            
            for idx, option in enumerate(options):
                letter = OPTION_LETTERS[idx]
                correct_class = ' correct' if idx == correct_idx else ''
                html_parts.append(f'            <li class="{letter.lower()}{correct_class}">{letter}) {self._escape_html(option)}</li>')
            
            html_parts.append('        </ul>')
            html_parts.append(f'        <div class="answer">✅ Correct Answer: {OPTION_LETTERS[correct_idx]}</div>')
            html_parts.append('    </div>')
        
        # HTML footer
        html_parts.append("""
</body>
</html>
""")
        
        return '\n'.join(html_parts)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '<')
                .replace('>', '>')
                .replace('"', '"')
                .replace("'", '&#39;'))
    
    # ==================== Main Export Function ====================
    
    def export(self, file_id: str, format: str) -> str:
        """
        Export MCQs to specified format.
        
        Args:
            file_id: The UUID of the file
            format: Export format (json, csv, txt, markdown, html)
            
        Returns:
            Exported content as string
            
        Raises:
            ValueError: If format is not supported
        """
        # Load MASTER JSON
        mcqs = self.load_master_json(file_id)
        
        if not mcqs:
            raise ValueError("No MCQs found in the file")
        
        # Export to requested format
        format_lower = format.lower()
        
        if format_lower == 'json':
            return self.export_json(mcqs)
        elif format_lower == 'csv':
            return self.export_csv(mcqs)
        elif format_lower == 'txt':
            return self.export_txt(mcqs)
        elif format_lower == 'markdown':
            return self.export_markdown(mcqs)
        elif format_lower == 'html':
            return self.export_html(mcqs)
        else:
            raise ValueError(f"Unsupported export format: {format}. Supported: json, csv, txt, markdown, html")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return ['json', 'csv', 'txt', 'markdown', 'html']


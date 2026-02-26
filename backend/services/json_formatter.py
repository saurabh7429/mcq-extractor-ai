"""
JSON Formatter service - handles formatting MCQ data to JSON.
"""
import logging
import json
from typing import List, Dict, Any
from pathlib import Path

# Create logger
logger = logging.getLogger(__name__)


class JSONFormatter:
    """Handles formatting and saving MCQ data to JSON."""
    
    def __init__(self):
        """Initialize JSON formatter."""
        logger.info("JSON Formatter initialized")
    
    def format_mcq(self, mcqs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format MCQ data to standard structure.
        
        Args:
            mcqs: List of raw MCQ dictionaries
        
        Returns:
            List of formatted MCQ dictionaries with schema:
            {
                "id": int,
                "question": str,
                "options": list of 4 strings,
                "answer": str
            }
        """
        formatted_mcqs = []
        seen_questions = set()
        next_id = 1
        
        for mcq in mcqs:
            try:
                # Parse the MCQ
                question = self._clean_text(mcq.get('question', ''))
                options = [self._clean_text(str(opt)) for opt in mcq.get('options', [])]
                
                # Get correct answer - can be index or string
                correct_answer = mcq.get('correct_answer')
                if isinstance(correct_answer, int) and 0 <= correct_answer < len(options):
                    answer = options[correct_answer]
                elif isinstance(correct_answer, str):
                    answer = self._clean_text(correct_answer)
                else:
                    logger.warning(f"Invalid correct_answer, skipping MCQ")
                    continue
                
                # Check for duplicates
                question_key = question.lower().strip()
                if question_key in seen_questions:
                    logger.debug(f"Duplicate question found: {question[:50]}...")
                    continue
                seen_questions.add(question_key)
                
                # Validate: must have exactly 4 options
                if len(options) != 4:
                    logger.warning(f"MCQ does not have exactly 4 options, skipping")
                    continue
                
                # Validate: answer must exist in options
                if answer not in options:
                    logger.warning(f"Answer '{answer}' not found in options, skipping")
                    continue
                
                # Create formatted MCQ
                formatted = {
                    'id': next_id,
                    'question': question,
                    'options': options,
                    'answer': answer
                }
                
                formatted_mcqs.append(formatted)
                next_id += 1
                    
            except Exception as e:
                logger.error(f"Error formatting MCQ: {str(e)}")
                continue
        
        logger.info(f"Formatted {len(formatted_mcqs)} MCQs (filtered {len(mcqs) - len(formatted_mcqs)} invalid/duplicates)")
        return formatted_mcqs
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove common artifacts
        text = text.replace('\n', ' ').replace('\r', '')
        return text.strip()
    
    def save_to_file(self, mcqs: List[Dict[str, Any]], filename: str, output_dir: Path) -> Path:
        """Save MCQs to a JSON file."""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            file_path = output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(mcqs, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(mcqs)} MCQs to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving JSON: {str(e)}")
            raise
    
    def load_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load MCQs from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                mcqs = json.load(f)
            
            if isinstance(mcqs, dict) and 'mcqs' in mcqs:
                mcqs = mcqs['mcqs']
            
            logger.info(f"Loaded {len(mcqs)} MCQs from {file_path}")
            return mcqs
            
        except Exception as e:
            logger.error(f"Error loading JSON: {str(e)}")
            raise

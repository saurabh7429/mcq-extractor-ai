"""
JSON Formatter service - handles formatting MCQ data to JSON.
"""
import logging
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

# Create logger
logger = logging.getLogger(__name__)

# Regex patterns for matching option labels
OPTION_PATTERNS = [
    # (A) Option, (a) Option
    r'^\s*\([a-dA-D]\)\s*',
    # A) Option, a) Option
    r'^\s*[a-dA-D]\)\s*',
    # A. Option, a. Option
    r'^\s*[a-dA-D]\.\s*',
    # A Option (no separator), a Option
    r'^\s*[a-dA-D]\s+',
]

# Letter-only options that indicate AI failed to extract full text
LETTER_ONLY_OPTIONS = {
    'a', 'b', 'c', 'd', 
    'a.', 'b.', 'c.', 'd.',
    '(a)', '(b)', '(c)', '(d)',
    'a)', 'b)', 'c)', 'd)',
    'A', 'B', 'C', 'D',
    'A.', 'B.', 'C.', 'D.',
    '(A)', '(B)', '(C)', '(D)',
    'A)', 'B)', 'C)', 'D)'
}


class JSONFormatter:
    """Handles formatting and saving MCQ data to JSON."""
    
    def __init__(self):
        """Initialize JSON formatter."""
        logger.info("JSON Formatter initialized")
    
    def _normalize_option(self, option: str) -> str:
        """
        Normalize option text by removing labels and extracting full text.
        
        Handles formats like:
        - (A) Paris -> Paris
        - A) Paris -> Paris
        - A. Paris -> Paris
        - A Paris -> Paris
        
        Args:
            option: Raw option text from AI or PDF
            
        Returns:
            Cleaned option text without the label
        """
        if not option:
            return ""
        
        option = str(option).strip()
        
        # Try each pattern
        for pattern in OPTION_PATTERNS:
            # Check if option starts with a label matching the pattern
            match = re.match(pattern, option, re.IGNORECASE)
            if match:
                # Remove the label and return the rest
                cleaned = option[match.end():].strip()
                if cleaned:
                    return cleaned
        
        # If no pattern matched, return original (it might already be clean)
        return option
    
    def _is_letter_only_option(self, option: str) -> bool:
        """Check if option is just a letter (A, B, C, D) without full text."""
        if not option:
            return True
        return str(option).strip().lower() in LETTER_ONLY_OPTIONS
    
    def _infer_correct_answer(self, question: str, options: List[str]) -> Optional[int]:
        """
        Intelligently infer the correct answer using basic knowledge reasoning.
        
        Args:
            question: The MCQ question text
            options: List of 4 options
            
        Returns:
            Index of the inferred correct answer (0-3), or None if cannot infer
        """
        question_lower = question.lower()
        options_lower = [str(opt).lower() for opt in options]
        
        # Common patterns for correct answer indicators
        # These patterns suggest the answer is explicitly mentioned in the question
        correct_indicators = [
            r'correct\s+answer\s+is\s+(\w+)',
            r'answer\s*:\s*(\w+)',
            r'answer\s+(\w+)',
            r'\*(\w+)\*',
            r'✓(\w+)',
            r'→(\w+)',
        ]
        
        # Try to find explicit answer in question
        for pattern in correct_indicators:
            match = re.search(pattern, question_lower)
            if match:
                answer_text = match.group(1).strip()
                # Find matching option
                for idx, opt in enumerate(options_lower):
                    if answer_text in opt or opt in answer_text:
                        logger.info(f"Inferred correct answer from question: index {idx}")
                        return idx
        
        # If we cannot infer, return None
        logger.warning(f"Could not infer correct answer for question: {question[:50]}...")
        return None
    
    def _parse_inline_options(self, text: str) -> List[str]:
        """
        Parse inline MCQ format like:
        (A) Paris (B) London (C) Berlin (D) Madrid
        
        Args:
            text: Text containing inline options
            
        Returns:
            List of options (empty if not inline format detected)
        """
        # Pattern for inline options: (A) text (B) text (C) text (D) text
        inline_pattern = r'\(([A-Da-d])\)\s*([^(]+?)(?=\s*\([A-Da-d]\)|$)'
        
        matches = re.findall(inline_pattern, text)
        
        if len(matches) >= 4:
            # Found inline format
            options = []
            for label, option_text in matches[:4]:
                option_text = option_text.strip()
                if option_text:
                    options.append(option_text)
            
            if len(options) == 4:
                return options
        
        return []
    
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
                "correct_answer": int (0-3)
            }
        """
        formatted_mcqs = []
        seen_questions = set()
        next_id = 1
        
        for mcq in mcqs:
            try:
                # Parse the MCQ
                question = self._clean_text(mcq.get('question', ''))
                raw_options = mcq.get('options', [])
                
                # Normalize each option - remove labels like (A), A), A., etc.
                options = []
                for opt in raw_options:
                    normalized = self._normalize_option(str(opt))
                    if normalized:
                        options.append(normalized)
                
                # Get correct answer as index (0-3)
                correct_answer = mcq.get('correct_answer')
                
                # Handle both int index and string answer
                if isinstance(correct_answer, int) and 0 <= correct_answer < len(options):
                    correct_index = correct_answer
                elif isinstance(correct_answer, str):
                    # Try to find the answer in options and get its index
                    answer_text = self._clean_text(correct_answer).lower()
                    correct_index = None
                    for idx, opt in enumerate(options):
                        if self._clean_text(str(opt)).lower() == answer_text:
                            correct_index = idx
                            break
                    if correct_index is None:
                        # Try normalized match
                        for idx, opt in enumerate(options):
                            if answer_text in self._clean_text(str(opt)).lower():
                                correct_index = idx
                                break
                    if correct_index is None:
                        logger.warning(f"Answer '{correct_answer}' not found in options, skipping MCQ")
                        continue
                elif correct_answer is None:
                    # Try to infer the correct answer
                    logger.info(f"No correct_answer provided, attempting to infer for: {question[:50]}...")
                    correct_index = self._infer_correct_answer(question, options)
                    if correct_index is None:
                        logger.warning(f"Could not infer correct answer, skipping MCQ")
                        continue
                else:
                    logger.warning(f"Invalid correct_answer value: {correct_answer}, skipping MCQ")
                    continue
                
                # Check for duplicates
                question_key = question.lower().strip()
                if question_key in seen_questions:
                    logger.debug(f"Duplicate question found: {question[:50]}...")
                    continue
                seen_questions.add(question_key)
                
                # Validate: must have exactly 4 options
                if len(options) != 4:
                    logger.warning(f"MCQ does not have exactly 4 options (found {len(options)}), skipping")
                    continue
                
                # Check if options are just letters (A, B, C, D) - this indicates AI failed to extract full text
                if all(self._is_letter_only_option(opt) for opt in options):
                    logger.warning(f"Options appear to be just letters, not full text: {options}")
                    # Skip these MCQs as they don't have proper option text
                    logger.warning(f"Skipping MCQ with letter-only options: {question[:50]}...")
                    continue
                
                # Remove empty options
                options = [opt for opt in options if opt and opt.strip()]
                if len(options) != 4:
                    logger.warning(f"After removing empty options, found {len(options)} instead of 4, skipping")
                    continue
                
                # Remove duplicates in options
                unique_options = []
                seen_opts = set()
                for opt in options:
                    opt_lower = opt.lower().strip()
                    if opt_lower not in seen_opts:
                        seen_opts.add(opt_lower)
                        unique_options.append(opt)
                options = unique_options
                
                if len(options) != 4:
                    logger.warning(f"After removing duplicate options, found {len(options)} instead of 4, skipping")
                    continue
                
                # Create formatted MCQ with correct_answer as index
                formatted = {
                    'id': next_id,
                    'question': question,
                    'options': options,
                    'correct_answer': correct_index
                }
                
                formatted_mcqs.append(formatted)
                next_id += 1
                    
            except Exception as e:
                logger.error(f"Error formatting MCQ: {str(e)}")
                continue
        
        logger.info(f"Formatted {len(formatted_mcqs)} MCQs (filtered {len(mcqs) - len(formatted_mcqs)} invalid/duplicates)")
        return formatted_mcqs
    
    def _clean_text(self, text: str) -> str:
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


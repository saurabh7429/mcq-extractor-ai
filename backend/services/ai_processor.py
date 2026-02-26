"""
AI Processor service - handles MCQ extraction using Gemini API.
"""
import logging
import os
import json
from typing import List, Dict, Any

# Create logger
logger = logging.getLogger(__name__)

# Chunk size for large texts
CHUNK_SIZE = 10000
MAX_RETRIES = 3


class AIProcessor:
    """Handles AI-powered MCQ extraction from text."""
    
    def __init__(self):
        """Initialize AI processor with Gemini API."""
        from backend.config import Config
        self.api_key = Config.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY', '')
        self.model_name = 'gemini-2.5-flash'  # Updated to latest model
        logger.info("AI Processor initialized with model: %s", self.model_name)
    
    def extract_mcq(self, text: str) -> List[Dict[str, Any]]:
        """Extract MCQs from text using Gemini API."""
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY found, using mock data")
            return self._get_mock_mcqs()
        
        if len(text) > CHUNK_SIZE:
            logger.info("Text too large, splitting into chunks")
            return self._extract_from_chunks(text)
        
        return self._extract_from_text(text)
    
    def _extract_from_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Extract MCQs from large text by chunking."""
        chunks = self._split_text_into_chunks(text)
        all_mcqs = []
        
        for i, chunk in enumerate(chunks):
            mcqs = self._extract_from_text(chunk, i)
            all_mcqs.extend(mcqs)
        
        return self._merge_mcqs(all_mcqs)
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into manageable chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunks.append(text[start:end].strip())
            start = end
        return chunks
    
    def _extract_from_text(self, text: str, chunk_index: int = 0) -> List[Dict[str, Any]]:
        """Extract MCQs with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                mcqs = self._call_gemini_api(text, chunk_index)
                if self._validate_mcqs(mcqs):
                    return mcqs
            except Exception as e:
                logger.warning("Attempt %d failed: %s", attempt + 1, str(e))
        return []
    
    def _call_gemini_api(self, text: str, chunk_index: int = 0) -> List[Dict[str, Any]]:
        """Call Gemini API and parse response."""
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)
        prompt = self._create_extraction_prompt(text)
        response = model.generate_content(prompt)
        return self._parse_response(response.text)
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create structured prompt for MCQ extraction."""
        return f"""Extract all MCQs from the text as JSON array. Requirements:
- Exactly 4 options per question
- correct_answer must be index 0-3
- Output ONLY valid JSON, no other text

Format:
[{{"question": "Q?", "options": ["A", "B", "C", "D"], "correct_answer": 0, "explanation": "..."}}]

Text: {text}"""
    
    def _parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI response to extract MCQs."""
        try:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start == -1:
                return []
            json_str = response_text[start:end]
            mcqs = json.loads(json_str)
            return [self._clean_mcq(m) for m in mcqs if self._clean_mcq(m)]
        except Exception as e:
            logger.error("Parse error: %s", str(e))
            return []
    
    def _clean_mcq(self, mcq: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate a single MCQ."""
        if not isinstance(mcq, dict):
            return None
        question = mcq.get('question', '')
        options = mcq.get('options', [])
        correct_answer = mcq.get('correct_answer')
        
        if not question or not isinstance(options, list) or len(options) != 4:
            return None
        if not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer > 3:
            return None
        
        return {
            'question': str(question).strip(),
            'options': [str(opt) for opt in options],
            'correct_answer': correct_answer,
            'explanation': str(mcq.get('explanation', 'No explanation'))
        }
    
    def _validate_mcqs(self, mcqs: List[Dict[str, Any]]) -> bool:
        """Validate MCQs meet requirements."""
        if not isinstance(mcqs, list):
            return False
        for mcq in mcqs:
            if not isinstance(mcq, dict):
                return False
            opts = mcq.get('options', [])
            correct = mcq.get('correct_answer')
            if len(opts) != 4 or not isinstance(correct, int) or correct < 0 or correct > 3:
                return False
        return True
    
    def _merge_mcqs(self, mcqs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate MCQs."""
        seen = set()
        unique = []
        for mcq in mcqs:
            key = mcq.get('question', '').lower().strip()
            if key and key not in seen:
                seen.add(key)
                unique.append(mcq)
        return unique
    
    def _get_mock_mcqs(self) -> List[Dict[str, Any]]:
        """Return mock MCQs for testing."""
        return [
            {"question": "What is the capital of France?", "options": ["London", "Paris", "Berlin", "Madrid"], "correct_answer": 1, "explanation": "Paris is the capital of France."},
            {"question": "Which planet is the Red Planet?", "options": ["Venus", "Mars", "Jupiter", "Saturn"], "correct_answer": 1, "explanation": "Mars appears red due to iron oxide."},
            {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "correct_answer": 1, "explanation": "2 + 2 equals 4."}
        ]

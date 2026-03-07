"""
AI Processor service - handles MCQ extraction using GROQ API.
"""
import logging
import os
import json
import re
from typing import List, Dict, Any, Optional

# Create logger
logger = logging.getLogger(__name__)

# Chunk size for optimal LLM processing - 1500-2500 characters
# This reduces token usage while ensuring MCQs aren't split
MIN_CHUNK_SIZE = 1500
MAX_CHUNK_SIZE = 2500
MAX_RETRIES = 2
RATE_LIMIT_WAIT_TIME = 30  # seconds to wait when rate limited


class AIProcessor:
    """Handles AI-powered MCQ extraction from text."""
    
    def __init__(self):
        """Initialize AI processor with GROQ API."""
        from backend.config import Config
        from flask import current_app
        
        # Get GROQ API key from config
        self.api_key = Config.GROQ_API_KEY or os.getenv('GROQ_API_KEY', '')
        
        # Use llama-3.1-8b-instant for all environments (more quota available)
        self.model_name = 'llama-3.1-8b-instant'
        
        logger.info("AI Processor initialized with model: %s", self.model_name)
        logger.info("Chunk size: %d-%d characters", MIN_CHUNK_SIZE, MAX_CHUNK_SIZE)
    
    def extract_mcq(self, text: str) -> List[Dict[str, Any]]:
        """Extract MCQs from text using GROQ API with intelligent chunking."""
        if not self.api_key:
            logger.warning("No GROQ_API_KEY found, using mock data")
            return self._get_mock_mcqs()
        
        # Split text into intelligent chunks (1500-2500 chars)
        chunks = self._split_text_intelligently(text)
        logger.info("Split text into %d chunks for processing", len(chunks))
        
        if not chunks:
            return []
        
        # Process each chunk and collect MCQs
        all_mcqs = []
        for i, chunk in enumerate(chunks):
            logger.info("Processing chunk %d/%d (%d chars)", i+1, len(chunks), len(chunk))
            mcqs = self._extract_from_text(chunk, i)
            if mcqs:
                logger.info("Extracted %d MCQs from chunk %d", len(mcqs), i+1)
                all_mcqs.extend(mcqs)
        
        # Merge and deduplicate MCQs while maintaining order
        merged_mcqs = self._merge_and_deduplicate_mcqs(all_mcqs)
        logger.info("Final MCQ count after deduplication: %d", len(merged_mcqs))
        
        return merged_mcqs
    
    def _split_text_intelligently(self, text: str) -> List[str]:
        """
        Split text into chunks of 1500-2500 characters.
        Splits at natural boundaries (newlines, question marks) to avoid splitting MCQs.
        """
        if not text or len(text) <= MAX_CHUNK_SIZE:
            return [text.strip()] if text else []
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        # Split by paragraphs first to preserve structure
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            paragraph_length = len(paragraph)
            
            # If single paragraph is larger than MAX_CHUNK_SIZE, split it further
            if paragraph_length > MAX_CHUNK_SIZE:
                # Save current accumulated content
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # Split large paragraph at sentences or question marks
                sub_chunks = self._split_large_paragraph(paragraph)
                chunks.extend(sub_chunks)
                continue
            
            # Check if adding this paragraph would exceed MAX_CHUNK_SIZE
            if current_length + paragraph_length + 1 > MAX_CHUNK_SIZE:
                # Save current chunk if it meets minimum size
                if current_length >= MIN_CHUNK_SIZE:
                    chunks.append(' '.join(current_chunk))
                else:
                    # Add to next chunk if current is too small
                    if current_chunk:
                        current_chunk.append(paragraph)
                        current_length += paragraph_length + 1
                        continue
                
                # Start new chunk
                current_chunk = [paragraph]
                current_length = paragraph_length
            else:
                current_chunk.append(paragraph)
                current_length += paragraph_length + 1
        
        # Don't forget the last chunk
        if current_chunk and current_length > 0:
            chunks.append(' '.join(current_chunk))
        
        # Filter out empty chunks and strip whitespace
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        
        logger.debug("Created %d chunks from %d characters", len(chunks), len(text))
        return chunks
    
    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """Split a large paragraph (>2500 chars) at natural boundaries."""
        chunks = []
        
        # Try to split at question marks first (MCQ boundaries)
        sentences = re.split(r'(\?)', paragraph)
        
        current_chunk = []
        current_length = 0
        
        for i, part in enumerate(sentences):
            part_length = len(part)
            
            # Check if adding this part would exceed limit
            if current_length + part_length > MAX_CHUNK_SIZE:
                # Save current chunk if it has content
                if current_chunk:
                    chunk_text = ''.join(current_chunk)
                    if chunk_text.strip():
                        chunks.append(chunk_text.strip())
                    current_chunk = []
                    current_length = 0
                
                # If single part is still too large, split by words
                if part_length > MAX_CHUNK_SIZE:
                    word_chunks = self._split_by_words(part)
                    chunks.extend(word_chunks)
                    continue
            
            current_chunk.append(part)
            current_length += part_length
        
        # Add remaining content
        if current_chunk:
            chunk_text = ''.join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
        
        return chunks
    
    def _split_by_words(self, text: str) -> List[str]:
        """Split text by words when it's too large for character-based splitting."""
        words = text.split()
        chunks = []
        current_words = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length > MAX_CHUNK_SIZE:
                if current_words:
                    chunks.append(' '.join(current_words))
                current_words = [word]
                current_length = word_length
            else:
                current_words.append(word)
                current_length += word_length
        
        if current_words:
            chunks.append(' '.join(current_words))
        
        return chunks
    
    def _extract_from_text(self, text: str, chunk_index: int = 0) -> List[Dict[str, Any]]:
        """Extract MCQs with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                mcqs = self._call_groq_api(text, chunk_index)
                if mcqs and len(mcqs) > 0:
                    # Add chunk index to help with ordering
                    for mcq in mcqs:
                        mcq['_chunk_index'] = chunk_index
                    return mcqs
            except Exception as e:
                logger.warning("Attempt %d failed for chunk %d: %s", attempt + 1, chunk_index, str(e))
                if "rate limit" in str(e).lower():
                    break  # Don't retry on rate limit
        return []
    
    def _call_groq_api(self, text: str, chunk_index: int = 0) -> List[Dict[str, Any]]:
        """Call GROQ API and parse response."""
        from groq import Groq
        import httpx
        
        client = Groq(api_key=self.api_key)
        
        prompt = self._create_extraction_prompt(text)
        
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            
            return self._parse_response(response.choices[0].message.content)
            
        except httpx.HTTPStatusError as e:
            # Check for rate limit (429)
            if e.response.status_code == 429:
                # Try to extract wait time from response
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', '')
                
                # Raise a clear rate limit error
                raise Exception(f"GROQ API Rate Limit Exceeded: {error_msg}")
            else:
                raise
        
        except httpx.ConnectError:
            raise Exception("Unable to connect to GROQ API. Please check your internet connection.")
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create structured prompt for MCQ extraction."""
        return f"""Extract all MCQs from the text as a JSON array.

IMPORTANT REQUIREMENTS - READ CAREFULLY:

1. EACH OPTION MUST CONTAIN THE FULL ANSWER TEXT, NEVER JUST LETTERS:
   - WRONG: "options": ["A", "B", "C", "D"]
   - RIGHT: "options": ["Paris", "London", "Berlin", "Madrid"]
   
2. REMOVE OPTION LABELS from option text:
   - Input: "A) Paris" → Output: "Paris"
   - Input: "(B) London" → Output: "London"  
   - Input: "C. Berlin" → Output: "Berlin"
   - Input: "(D) Madrid" → Output: "Madrid"

3. SUPPORTED MCQ FORMATS:
   - Standard: "1. Question? A) Apple B) Banana C) Cherry D) Date"
   - Inline: "(A) Apple (B) Banana (C) Cherry (D) Date"
   - Table: Extract all rows as options
   - Multiline: Each option on new line

4. CORRECT ANSWER - MUST be an integer index (0-3):
   - Index mapping: 0=A, 1=B, 2=C, 3=D
   - If correct answer text is given (e.g., "Answer: B" or "*B" or "Answer: Paris"), find which option it matches and use its index
   - If NO explicit correct answer is given, INFER it using basic knowledge reasoning

5. WHEN INFERENCING CORRECT ANSWER:
   - Use logical reasoning to determine the most likely correct answer
   - Example: "What is 2+2?" options: ["3", "4", "5", "6"] → correct_answer: 1 (index of "4")

6. ALWAYS RETURN EXACTLY 4 OPTIONS per question

7. If you cannot determine the correct answer, you may set correct_answer to null but still include the MCQ

Format (STRICTLY follow this JSON structure):
[{{"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin", "Madrid"], "correct_answer": 0}}]

IMPORTANT: Output ONLY valid JSON array, no additional text.

Text to extract from:
{text}"""
    
    def _parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI response to extract MCQs."""
        try:
            # Find JSON array in response
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            
            if start == -1:
                # Try parsing as JSON object with 'mcqs' or similar key
                data = json.loads(response_text)
                # Find the array in the object
                for key in data.values():
                    if isinstance(key, list):
                        mcqs = key
                        return [self._clean_mcq(m) for m in mcqs if self._clean_mcq(m)]
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
        
        # Skip only if question is empty or options are less than 4
        if not question or not isinstance(options, list) or len(options) < 4:
            return None
        
        # Normalize options - remove labels like (A), A), A., etc.
        option_patterns = [
            r'^\s*\([a-dA-D]\)\s*',  # (A) Option
            r'^\s*[a-dA-D]\)\s*',    # A) Option
            r'^\s*[a-dA-D]\.\s*',    # A. Option
            r'^\s*[a-dA-D]\s+',      # A Option
        ]
        
        normalized_options = []
        for opt in options:
            opt_str = str(opt).strip()
            # Try each pattern to remove labels
            for pattern in option_patterns:
                match = re.match(pattern, opt_str, re.IGNORECASE)
                if match:
                    opt_str = opt_str[match.end():].strip()
                    break
            normalized_options.append(opt_str)
        
        options = normalized_options
        
        # Ensure we have exactly 4 options (pad with empty if needed, or truncate)
        while len(options) < 4:
            options.append("")
        if len(options) > 4:
            options = options[:4]
        
        # If correct_answer is a string (text or letter), convert it to index
        if isinstance(correct_answer, str):
            answer_text = correct_answer.strip().lower()
            
            # Handle letter answers like "A", "B", "C", "D"
            letter_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
            if answer_text in letter_map:
                correct_answer = letter_map[answer_text]
            else:
                # Try to find matching option
                for idx, opt in enumerate(options):
                    if str(opt).strip().lower() == answer_text:
                        correct_answer = idx
                        break
                else:
                    # If no match found, try partial match
                    for idx, opt in enumerate(options):
                        if answer_text in str(opt).strip().lower():
                            correct_answer = idx
                            break
                    else:
                        # Cannot determine from string - will infer below
                        correct_answer = None
        
        # If correct_answer is still None or invalid, infer it using reasoning
        if correct_answer is None or not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer > 3:
            correct_answer = self._infer_correct_answer(question, options)
        
        # Final validation - if still can't determine, default to 0
        if correct_answer is None or not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer > 3:
            correct_answer = 0  # Default to first option if cannot infer
            logger.info(f"Could not infer correct answer for question, defaulting to 0: {question[:50]}...")
        
        return {
            'question': str(question).strip(),
            'options': [str(opt) for opt in options],
            'correct_answer': correct_answer,
            'explanation': str(mcq.get('explanation', 'No explanation'))
        }
    
    def _infer_correct_answer(self, question: str, options: List[str]) -> Optional[int]:
        """
        Intelligently infer the correct answer using basic knowledge reasoning.
        
        Args:
            question: The MCQ question text
            options: List of 4 options
            
        Returns:
            Index of the inferred correct answer (0-3), or None if cannot infer
        """
        if not options or len(options) < 4:
            return None
            
        question_lower = question.lower()
        
        # Check for explicit answer indicators in the question
        correct_indicators = [
            (r'answer\s+is\s+([a-dA-D])', True),  # "Answer is A"
            (r'correct\s+answer\s+:\s*([a-dA-D])', True),  # "Correct answer: A"
            (r'\*([a-dA-D])\*', True),  # "*A*"
            (r'\(([a-dA-D])\)', True),  # "(A)"
            (r'answer\s+is\s+(\w+)', False),  # "Answer is Paris"
            (r'correct\s+answer\s+:\s*(\w+)', False),  # "Correct answer: Paris"
        ]
        
        for pattern, is_letter in correct_indicators:
            match = re.search(pattern, question_lower)
            if match:
                answer = match.group(1).strip()
                if is_letter:
                    letter_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
                    if answer.lower() in letter_map:
                        return letter_map[answer.lower()]
                else:
                    # Match against options
                    for idx, opt in enumerate(options):
                        if answer.lower() in str(opt).lower():
                            return idx
        
        # Try to infer from common knowledge patterns
        # Mathematical questions
        if any(op in question_lower for op in ['+', '-', '*', '/', 'x', '÷', '=']):
            # Try to find the mathematically correct answer
            math_pattern = r'(\d+)\s*([+\-*/x÷])\s*(\d+)\s*=\s*(\d+)'
            match = re.search(math_pattern, question_lower)
            if match:
                try:
                    a, op, b, result = int(match.group(1)), match.group(2), int(match.group(3)), int(match.group(4))
                    expected = {'+': a+b, '-': a-b, '*': a*b, 'x': a*b, '/': a//b if b else 0, '÷': a//b if b else 0}
                    if expected.get(op) == result:
                        # Result is correct, find which option matches
                        for idx, opt in enumerate(options):
                            if str(result) in str(opt):
                                return idx
                except:
                    pass
        
        # Capital/country questions
        if 'capital' in question_lower:
            capitals = {
                'france': 'paris', 'germany': 'berlin', 'japan': 'tokyo', 'uk': 'london',
                'italy': 'rome', 'spain': 'madrid', 'india': 'new delhi', 'usa': 'washington'
            }
            for country, capital in capitals.items():
                if country in question_lower:
                    for idx, opt in enumerate(options):
                        if capital in str(opt).lower():
                            return idx
        
        # Language questions
        if 'language' in question_lower:
            if 'web' in question_lower or 'browser' in question_lower:
                for idx, opt in enumerate(options):
                    if 'javascript' in str(opt).lower():
                        return idx
            if 'programming' in question_lower:
                for idx, opt in enumerate(options):
                    if 'python' in str(opt).lower():
                        return idx
        
        # Acronym questions (CPU, RAM, HTML, etc.)
        acronym_pattern = r'([A-Z]{2,})\s+stand\s+for'
        match = re.search(acronym_pattern, question)
        if match:
            acronym = match.group(1)
            expansions = {
                'CPU': 'central processing unit',
                'RAM': 'random access memory',
                'HTML': 'hyper text markup language',
                'HTTP': 'hypertext transfer protocol',
                'FTP': 'file transfer protocol',
                'SQL': 'structured query language',
                'URL': 'uniform resource locator',
                'USB': 'universal serial bus',
                'PDF': 'portable document format',
                'IP': 'internet protocol',
                'GPU': 'graphics processing unit',
            }
            if acronym.upper() in expansions:
                expected = expansions[acronym.upper()]
                for idx, opt in enumerate(options):
                    if expected in str(opt).lower():
                        return idx
        
        # If still cannot infer, return None
        logger.info(f"Could not infer correct answer for: {question[:50]}...")
        return None
    
    def _merge_and_deduplicate_mcqs(self, mcqs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge MCQs from all chunks and remove duplicates while maintaining order.
        
        Only treats MCQs as duplicates if BOTH:
        - Same question text
        - Same options (in same order)
        
        Questions with similar text but different options are kept as separate MCQs.
        """
        if not mcqs:
            return []
        
        seen_mcqs = set()
        unique_mcqs = []
        
        for mcq in mcqs:
            # Get question and options for comparison
            question = mcq.get('question', '').strip()
            options = mcq.get('options', [])
            
            if not question or not options:
                continue
            
            # Create a unique key based on BOTH question AND options
            # Normalize for comparison (case-insensitive, ignore punctuation)
            normalized_question = self._normalize_for_comparison(question)
            normalized_options = '|'.join([self._normalize_for_comparison(str(opt)) for opt in options])
            
            mcq_key = f"{normalized_question}||{normalized_options}"
            
            # Only skip if we've seen this exact question+options combination
            if mcq_key in seen_mcqs:
                logger.debug(f"Skipping duplicate MCQ: {question[:50]}...")
                continue
            
            seen_mcqs.add(mcq_key)
            
            # Add clean MCQ to results
            clean_mcq = {
                'question': question,
                'options': options,
                'correct_answer': mcq.get('correct_answer'),
                'explanation': mcq.get('explanation', 'No explanation')
            }
            unique_mcqs.append(clean_mcq)
        
        logger.info("Deduplication: %d MCQs -> %d unique MCQs", len(mcqs), len(unique_mcqs))
        return unique_mcqs
    
    def _normalize_for_comparison(self, text: str) -> str:
        """Normalize text for comparison by removing extra whitespace and punctuation."""
        if not text:
            return ""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove common punctuation that doesn't affect meaning
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower().strip()
    
    def _validate_mcqs(self, mcqs: List[Dict[str, Any]]) -> bool:
        """Validate MCQs meet requirements."""
        if not isinstance(mcqs, list):
            return False
        for mcq in mcqs:
            if not isinstance(mcq, dict):
                return False
            opts = mcq.get('options', [])
            correct = mcq.get('correct_answer')
            
            # Allow both int and str for validation (conversion happens in _clean_mcq)
            if len(opts) != 4:
                return False
            if isinstance(correct, str):
                # String answers are OK for validation - will be converted later
                continue
            if not isinstance(correct, int) or correct < 0 or correct > 3:
                return False
        return True
    
    def _get_mock_mcqs(self) -> List[Dict[str, Any]]:
        """Return mock MCQs for testing."""
        return [
            {"question": "What is the capital of France?", "options": ["London", "Paris", "Berlin", "Madrid"], "correct_answer": 1, "explanation": "Paris is the capital of France."},
            {"question": "Which planet is the Red Planet?", "options": ["Venus", "Mars", "Jupiter", "Saturn"], "correct_answer": 1, "explanation": "Mars appears red due to iron oxide."},
            {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "correct_answer": 1, "explanation": "2 + 2 equals 4."}
        ]

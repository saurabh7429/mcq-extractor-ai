"""
Tests for AI Processor service.
"""
import unittest
import json
from unittest.mock import patch, MagicMock
from backend.services.ai_processor import AIProcessor


class TestAIProcessor(unittest.TestCase):
    """Test cases for AIProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = AIProcessor()
    
    def test_initialization(self):
        """Test AIProcessor initialization."""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.model_name, 'gemini-1.5-flash')
    
    def test_extract_mcq_no_api_key(self):
        """Test extract_mcq returns mock data when no API key."""
        self.processor.api_key = ''
        result = self.processor.extract_mcq("test text")
        self.assertEqual(len(result), 3)
        self.assertIn('question', result[0])
        self.assertIn('options', result[0])
        self.assertIn('correct_answer', result[0])
    
    def test_split_text_into_chunks(self):
        """Test text chunking."""
        text = 'a' * 15000
        chunks = self.processor._split_text_into_chunks(text)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 10000)
        self.assertEqual(len(chunks[1]), 5000)
    
    def test_clean_mcq_valid(self):
        """Test cleaning valid MCQ."""
        mcq = {
            'question': 'What is 2+2?',
            'options': ['1', '2', '3', '4'],
            'correct_answer': 3,
            'explanation': '2+2=4'
        }
        result = self.processor._clean_mcq(mcq)
        self.assertIsNotNone(result)
        self.assertEqual(result['question'], 'What is 2+2?')
        self.assertEqual(len(result['options']), 4)
        self.assertEqual(result['correct_answer'], 3)
    
    def test_clean_mcq_invalid_options(self):
        """Test cleaning invalid MCQ with wrong options count."""
        mcq = {
            'question': 'What is 2+2?',
            'options': ['1', '2'],
            'correct_answer': 3
        }
        result = self.processor._clean_mcq(mcq)
        self.assertIsNone(result)
    
    def test_clean_mcq_invalid_answer(self):
        """Test cleaning MCQ with invalid correct_answer."""
        mcq = {
            'question': 'What is 2+2?',
            'options': ['1', '2', '3', '4'],
            'correct_answer': 5
        }
        result = self.processor._clean_mcq(mcq)
        self.assertIsNone(result)
    
    def test_validate_mcqs_valid(self):
        """Test validation of valid MCQs."""
        mcqs = [
            {'question': 'Q1?', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 0},
            {'question': 'Q2?', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 1}
        ]
        self.assertTrue(self.processor._validate_mcqs(mcqs))
    
    def test_validate_mcqs_invalid(self):
        """Test validation of invalid MCQs."""
        mcqs = [
            {'question': 'Q1?', 'options': ['A', 'B'], 'correct_answer': 0}
        ]
        self.assertFalse(self.processor._validate_mcqs(mcqs))
    
    def test_validate_mcqs_empty(self):
        """Test validation of empty list."""
        self.assertFalse(self.processor._validate_mcqs([]))
    
    def test_merge_mcqs(self):
        """Test MCQ merging and deduplication."""
        mcqs = [
            {'question': 'What is 2+2?', 'options': ['1', '2', '3', '4'], 'correct_answer': 3},
            {'question': 'What is 2+2?', 'options': ['1', '2', '3', '4'], 'correct_answer': 3},
            {'question': 'What is 3+3?', 'options': ['1', '2', '3', '6'], 'correct_answer': 3}
        ]
        result = self.processor._merge_mcqs(mcqs)
        self.assertEqual(len(result), 2)
    
    def test_parse_response_valid_json(self):
        """Test parsing valid JSON response."""
        response = '[{"question": "Q1?", "options": ["A", "B", "C", "D"], "correct_answer": 0}]'
        result = self.processor._parse_response(response)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['question'], 'Q1?')
    
    def test_parse_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        response = 'not valid json'
        result = self.processor._parse_response(response)
        self.assertEqual(len(result), 0)
    
    def test_parse_response_no_array(self):
        """Test parsing response without JSON array."""
        response = 'Some text without JSON'
        result = self.processor._parse_response(response)
        self.assertEqual(len(result), 0)
    
    @patch('backend.services.ai_processor.genai.GenerativeModel')
    def test_call_gemini_api(self, mock_model):
        """Test Gemini API call."""
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        mock_instance.generate_content.return_value.text = '[{"question": "Q1?", "options": ["A", "B", "C", "D"], "correct_answer": 0}]'
        
        result = self.processor._call_gemini_api("test text", 0)
        self.assertEqual(len(result), 1)
    
    def test_get_mock_mcqs(self):
        """Test mock MCQs."""
        result = self.processor._get_mock_mcqs()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['correct_answer'], 1)


if __name__ == '__main__':
    unittest.main()

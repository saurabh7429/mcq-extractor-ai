"""
Tests for JSON Formatter service.
"""
import unittest
import json
import tempfile
import os
from pathlib import Path
from backend.services.json_formatter import JSONFormatter


class TestJSONFormatter(unittest.TestCase):
    """Test cases for JSONFormatter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = JSONFormatter()
    
    def test_initialization(self):
        """Test JSONFormatter initialization."""
        self.assertIsNotNone(self.formatter)
    
    def test_format_mcq_valid(self):
        """Test formatting valid MCQ."""
        mcqs = [
            {
                'question': 'What is 2+2?',
                'options': ['1', '2', '3', '4'],
                'correct_answer': 3
            }
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['question'], 'What is 2+2?')
        self.assertEqual(len(result[0]['options']), 4)
        self.assertEqual(result[0]['answer'], '4')
    
    def test_format_mcq_string_answer(self):
        """Test formatting MCQ with string answer."""
        mcqs = [
            {
                'question': 'What is the capital of France?',
                'options': ['London', 'Paris', 'Berlin', 'Madrid'],
                'correct_answer': 'Paris'
            }
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['answer'], 'Paris')
    
    def test_format_mcq_duplicate_questions(self):
        """Test that duplicate questions are removed."""
        mcqs = [
            {'question': 'What is 2+2?', 'options': ['1', '2', '3', '4'], 'correct_answer': 3},
            {'question': 'What is 2+2?', 'options': ['1', '2', '3', '4'], 'correct_answer': 2},
            {'question': 'What is 3+3?', 'options': ['1', '2', '3', '6'], 'correct_answer': 3}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 2)
    
    def test_format_mcq_invalid_options_count(self):
        """Test that MCQs with wrong option count are discarded."""
        mcqs = [
            {'question': 'What is 2+2?', 'options': ['1', '2'], 'correct_answer': 0},
            {'question': 'What is 3+3?', 'options': ['1', '2', '3', '4', '5'], 'correct_answer': 3},
            {'question': 'What is 4+4?', 'options': ['1', '2', '3', '4'], 'correct_answer': 3}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['question'], 'What is 4+4?')
    
    def test_format_mcq_answer_not_in_options(self):
        """Test that MCQs with answer not in options are discarded."""
        mcqs = [
            {'question': 'What is 2+2?', 'options': ['1', '2', '3', '4'], 'correct_answer': '5'}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 0)
    
    def test_format_mcq_incremental_ids(self):
        """Test that IDs are auto-assigned incrementally."""
        mcqs = [
            {'question': 'Q1?', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 0},
            {'question': 'Q2?', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 1},
            {'question': 'Q3?', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 2}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[1]['id'], 2)
        self.assertEqual(result[2]['id'], 3)
    
    def test_format_mcq_clean_text(self):
        """Test that text is cleaned properly."""
        mcqs = [
            {'question': '  What  is   2+2?  ', 'options': ['  1  ', '2', '3', '4'], 'correct_answer': 0}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(result[0]['question'], 'What is 2+2?')
        self.assertEqual(result[0]['options'], ['1', '2', '3', '4'])
    
    def test_format_mcq_empty_list(self):
        """Test formatting empty list."""
        result = self.formatter.format_mcq([])
        self.assertEqual(len(result), 0)
    
    def test_save_to_file(self):
        """Test saving MCQs to file."""
        mcqs = [
            {'id': 1, 'question': 'Q1?', 'options': ['A', 'B', 'C', 'D'], 'answer': 'A'}
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            file_path = self.formatter.save_to_file(mcqs, 'test.json', output_dir)
            
            self.assertTrue(file_path.exists())
            
            with open(file_path, 'r') as f:
                loaded = json.load(f)
            
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]['question'], 'Q1?')
    
    def test_load_from_file(self):
        """Test loading MCQs from file."""
        mcqs = [
            {'id': 1, 'question': 'Q1?', 'options': ['A', 'B', 'C', 'D'], 'answer': 'A'}
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            file_path = output_dir / 'test.json'
            
            with open(file_path, 'w') as f:
                json.dump(mcqs, f)
            
            loaded = self.formatter.load_from_file(file_path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]['question'], 'Q1?')


if __name__ == '__main__':
    unittest.main()

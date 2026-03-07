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
                'options': ['One', 'Two', 'Three', 'Four'],
                'correct_answer': 3
            }
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['question'], 'What is 2+2?')
        self.assertEqual(len(result[0]['options']), 4)
        self.assertEqual(result[0]['correct_answer'], 3)  # Index, not text
    
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
        self.assertEqual(result[0]['correct_answer'], 1)  # Index of Paris
    
    def test_format_mcq_duplicate_questions(self):
        """Test that duplicate questions are removed."""
        mcqs = [
            {'question': 'What is 2+2?', 'options': ['One', 'Two', 'Three', 'Four'], 'correct_answer': 3},
            {'question': 'What is 2+2?', 'options': ['One', 'Two', 'Three', 'Four'], 'correct_answer': 2},
            {'question': 'What is 3+3?', 'options': ['One', 'Two', 'Three', 'Six'], 'correct_answer': 3}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 2)
    
    def test_format_mcq_invalid_options_count(self):
        """Test that MCQs with wrong option count are discarded."""
        mcqs = [
            {'question': 'What is 2+2?', 'options': ['One', 'Two'], 'correct_answer': 0},
            {'question': 'What is 3+3?', 'options': ['One', 'Two', 'Three', 'Four', 'Five'], 'correct_answer': 3},
            {'question': 'What is 4+4?', 'options': ['One', 'Two', 'Three', 'Four'], 'correct_answer': 3}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['question'], 'What is 4+4?')
    
    def test_format_mcq_answer_not_in_options(self):
        """Test that MCQs with answer not in options are discarded."""
        mcqs = [
            {'question': 'What is 2+2?', 'options': ['One', 'Two', 'Three', 'Four'], 'correct_answer': 'Five'}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 0)
    
    def test_format_mcq_incremental_ids(self):
        """Test that IDs are auto-assigned incrementally."""
        mcqs = [
            {'question': 'Q1?', 'options': ['Option1', 'Option2', 'Option3', 'Option4'], 'correct_answer': 0},
            {'question': 'Q2?', 'options': ['Option1', 'Option2', 'Option3', 'Option4'], 'correct_answer': 1},
            {'question': 'Q3?', 'options': ['Option1', 'Option2', 'Option3', 'Option4'], 'correct_answer': 2}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[1]['id'], 2)
        self.assertEqual(result[2]['id'], 3)
    
    def test_format_mcq_clean_text(self):
        """Test that text is cleaned properly."""
        mcqs = [
            {'question': '  What  is   2+2?  ', 'options': ['  One  ', 'Two', 'Three', 'Four'], 'correct_answer': 0}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(result[0]['question'], 'What is 2+2?')
        self.assertEqual(result[0]['options'], ['One', 'Two', 'Three', 'Four'])
    
    def test_format_mcq_empty_list(self):
        """Test formatting empty list."""
        result = self.formatter.format_mcq([])
        self.assertEqual(len(result), 0)
    
    def test_format_mcq_letter_only_options_filtered(self):
        """Test that letter-only options are filtered out."""
        mcqs = [
            {'question': 'What is the answer?', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 0}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 0)  # Should be filtered out
    
    def test_format_mcq_with_option_labels_removed(self):
        """Test that option labels are removed."""
        mcqs = [
            {'question': 'What is the capital?', 'options': ['A) Paris', 'B) London', 'C) Berlin', 'D) Madrid'], 'correct_answer': 0}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['options'], ['Paris', 'London', 'Berlin', 'Madrid'])
        self.assertEqual(result[0]['correct_answer'], 0)
    
    def test_format_mcq_with_inline_options(self):
        """Test that inline options are properly extracted."""
        mcqs = [
            {'question': 'Which one is fruit?', 'options': ['(A) Apple', '(B) Car', '(C) Book', '(D) Phone'], 'correct_answer': 0}
        ]
        result = self.formatter.format_mcq(mcqs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['options'], ['Apple', 'Car', 'Book', 'Phone'])
        self.assertEqual(result[0]['correct_answer'], 0)
    
    def test_save_to_file(self):
        """Test saving MCQs to file."""
        mcqs = [
            {'id': 1, 'question': 'Q1?', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 0}
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
            {'id': 1, 'question': 'Q1?', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 0}
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            file_path = output_dir / 'test.json'
            
            with open(file_path, 'w') as f:
                json.dump(mcqs, f)
            
            loaded = self.formatter.load_from_file(file_path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]['question'], 'Q1?')
    
    def test_format_mcq_null_correct_answer(self):
        """Test that MCQs with null correct_answer are handled."""
        mcqs = [
            {'question': 'What is the answer?', 'options': ['Option1', 'Option2', 'Option3', 'Option4'], 'correct_answer': None}
        ]
        result = self.formatter.format_mcq(mcqs)
        # Should be filtered out since we can't infer the answer
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()


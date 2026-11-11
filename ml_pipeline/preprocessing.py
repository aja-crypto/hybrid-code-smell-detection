"""
Preprocessing Module for Code Smell Detection

Handles:
1. Code cleaning and normalization
2. Tokenization using GraphCodeBERT
3. Conversion to PyTorch tensors
4. Batch processing
"""

import re
import torch
from transformers import AutoTokenizer
from typing import List, Dict, Tuple


class CodePreprocessor:
    """
    Code preprocessing utility for cleaning and preparing code for model input
    """
    
    def __init__(self, model_name='microsoft/graphcodebert-base', max_length=512):
        """
        Initialize preprocessor with tokenizer
        
        Args:
            model_name (str): HuggingFace model identifier
            max_length (int): Maximum sequence length for tokenization
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_length = max_length
    
    def remove_comments(self, code: str) -> str:
        """
        Remove comments from code
        
        Args:
            code (str): Source code
        
        Returns:
            str: Code without comments
        """
        # Remove single-line comments (// and #)
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        code = re.sub(r'#.*?$', '', code, flags=re.MULTILINE)
        
        # Remove multi-line comments (/* */ and """ """)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        return code
    
    def remove_strings(self, code: str) -> str:
        """
        Remove string literals from code
        
        Args:
            code (str): Source code
        
        Returns:
            str: Code without string literals
        """
        # Remove double-quoted strings
        code = re.sub(r'"[^"]*"', '"STRING"', code)
        # Remove single-quoted strings
        code = re.sub(r"'[^']*'", "'STRING'", code)
        
        return code
    
    def normalize_whitespace(self, code: str) -> str:
        """
        Normalize whitespace in code
        
        Args:
            code (str): Source code
        
        Returns:
            str: Code with normalized whitespace
        """
        # Remove excessive blank lines
        code = re.sub(r'\n\s*\n', '\n', code)
        # Remove trailing whitespace
        code = '\n'.join(line.rstrip() for line in code.split('\n'))
        
        return code
    
    def clean_code(self, code: str) -> str:
        """
        Complete code cleaning pipeline
        
        Args:
            code (str): Raw source code
        
        Returns:
            str: Cleaned code
        """
        code = self.remove_comments(code)
        code = self.remove_strings(code)
        code = self.normalize_whitespace(code)
        code = code.strip()
        
        return code
    
    def tokenize(self, code: str, return_tensors=True) -> Dict:
        """
        Tokenize code using GraphCodeBERT tokenizer
        
        Args:
            code (str): Source code to tokenize
            return_tensors (bool): Return PyTorch tensors if True
        
        Returns:
            dict: Tokenized output with 'input_ids' and 'attention_mask'
        """
        encoded = self.tokenizer(
            code,
            return_tensors='pt' if return_tensors else None,
            max_length=self.max_length,
            padding='max_length',
            truncation=True
        )
        
        return encoded
    
    def preprocess(self, code: str) -> Dict:
        """
        Complete preprocessing pipeline: clean -> tokenize
        
        Args:
            code (str): Raw source code
        
        Returns:
            dict: Preprocessed tensors ready for model input
        """
        # Clean code
        cleaned_code = self.clean_code(code)
        
        # Tokenize
        tokens = self.tokenize(cleaned_code, return_tensors=True)
        
        return tokens
    
    def batch_preprocess(self, codes: List[str]) -> Dict:
        """
        Batch preprocessing for multiple code samples
        
        Args:
            codes (List[str]): List of source codes
        
        Returns:
            dict: Batch of preprocessed tensors
        """
        cleaned_codes = [self.clean_code(code) for code in codes]
        
        # Tokenize batch
        tokens = self.tokenizer(
            cleaned_codes,
            return_tensors='pt',
            max_length=self.max_length,
            padding=True,
            truncation=True
        )
        
        return tokens


class TripletGenerator:
    """
    Generate triplets (anchor, positive, negative) for contrastive learning
    """
    
    def __init__(self, preprocessor: CodePreprocessor):
        """
        Initialize triplet generator
        
        Args:
            preprocessor (CodePreprocessor): Code preprocessor instance
        """
        self.preprocessor = preprocessor
    
    def create_triplet(self, anchor_code: str, positive_code: str, 
                       negative_code: str) -> Dict:
        """
        Create a single triplet
        
        Args:
            anchor_code (str): Anchor code sample
            positive_code (str): Positive code sample (same class as anchor)
            negative_code (str): Negative code sample (different class)
        
        Returns:
            dict: Triplet with tokenized inputs
        """
        anchor = self.preprocessor.preprocess(anchor_code)
        positive = self.preprocessor.preprocess(positive_code)
        negative = self.preprocessor.preprocess(negative_code)
        
        return {
            'anchor': anchor,
            'positive': positive,
            'negative': negative
        }
    
    def batch_triplets(self, anchor_codes: List[str], positive_codes: List[str],
                      negative_codes: List[str]) -> Dict:
        """
        Create batch of triplets
        
        Args:
            anchor_codes (List[str]): Anchor code samples
            positive_codes (List[str]): Positive code samples
            negative_codes (List[str]): Negative code samples
        
        Returns:
            dict: Batch of triplets
        """
        anchor_batch = self.preprocessor.batch_preprocess(anchor_codes)
        positive_batch = self.preprocessor.batch_preprocess(positive_codes)
        negative_batch = self.preprocessor.batch_preprocess(negative_codes)
        
        return {
            'anchor': anchor_batch,
            'positive': positive_batch,
            'negative': negative_batch
        }


# Utility functions

def load_code_from_file(filepath: str) -> str:
    """
    Load source code from file
    
    Args:
        filepath (str): Path to code file
    
    Returns:
        str: File contents
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""


def validate_code(code: str, min_length: int = 10) -> Tuple[bool, str]:
    """
    Validate code input
    
    Args:
        code (str): Source code
        min_length (int): Minimum code length
    
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if not code or len(code.strip()) == 0:
        return False, "Code cannot be empty"
    
    if len(code.strip()) < min_length:
        return False, f"Code must be at least {min_length} characters"
    
    return True, "Valid"

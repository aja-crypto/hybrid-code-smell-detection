"""
Utility Functions for Code Smell Detection

Common utilities for preprocessing, model loading, and analysis.
"""

import os
import json
import torch
from typing import List, Dict, Tuple


class ModelUtils:
    """Utility functions for model operations"""
    
    @staticmethod
    def load_model_state(model, model_path: str, device: str = 'cpu'):
        """
        Load pre-trained model weights
        
        Args:
            model: PyTorch model instance
            model_path (str): Path to saved model weights
            device (str): Device to load model on
        
        Returns:
            model: Loaded model
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        state_dict = torch.load(model_path, map_location=device)
        model.load_state_dict(state_dict)
        model = model.to(device)
        model.eval()
        
        return model
    
    @staticmethod
    def save_model_state(model, model_path: str):
        """
        Save model weights
        
        Args:
            model: PyTorch model instance
            model_path (str): Path to save weights
        """
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        torch.save(model.state_dict(), model_path)


class DataUtils:
    """Utility functions for data operations"""
    
    @staticmethod
    def load_text_file(filepath: str) -> List[str]:
        """
        Load lines from text file
        
        Args:
            filepath (str): Path to text file
        
        Returns:
            List[str]: Lines from file
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return []
    
    @staticmethod
    def save_json(data: dict, filepath: str):
        """Save data to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_json(filepath: str) -> dict:
        """Load data from JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)


class MetricsUtils:
    """Utility functions for metrics calculation"""
    
    @staticmethod
    def calculate_metrics(predictions: List[int], ground_truth: List[int]) -> Dict:
        """
        Calculate classification metrics
        
        Args:
            predictions (List[int]): Predicted labels
            ground_truth (List[int]): True labels
        
        Returns:
            dict: Metrics dictionary
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
        )
        
        accuracy = accuracy_score(ground_truth, predictions)
        precision = precision_score(ground_truth, predictions, average='weighted', zero_division=0)
        recall = recall_score(ground_truth, predictions, average='weighted', zero_division=0)
        f1 = f1_score(ground_truth, predictions, average='weighted', zero_division=0)
        cm = confusion_matrix(ground_truth, predictions)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': cm.tolist()
        }
    
    @staticmethod
    def print_metrics(metrics: Dict):
        """Print metrics in readable format"""
        print("\n" + "="*50)
        print("EVALUATION METRICS")
        print("="*50)
        print(f"Accuracy:  {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1 Score:  {metrics['f1']:.4f}")
        print("\nConfusion Matrix:")
        for row in metrics['confusion_matrix']:
            print(f"  {row}")
        print("="*50 + "\n")


class CodeUtils:
    """Utility functions for code analysis"""
    
    @staticmethod
    def get_code_statistics(code: str) -> Dict:
        """
        Get statistics about code
        
        Args:
            code (str): Source code
        
        Returns:
            dict: Code statistics
        """
        lines = code.split('\n')
        
        return {
            'lines': len(lines),
            'characters': len(code),
            'tokens': len(code.split()),
            'non_empty_lines': len([l for l in lines if l.strip()]),
            'max_line_length': max(len(l) for l in lines) if lines else 0,
            'avg_line_length': sum(len(l) for l in lines) / len(lines) if lines else 0
        }
    
    @staticmethod
    def get_supported_extensions() -> List[str]:
        """Get list of supported code file extensions"""
        return ['.java', '.py', '.js', '.cpp', '.c', '.ts', '.go', '.rb', '.php', '.txt']
    
    @staticmethod
    def is_code_file(filename: str) -> bool:
        """Check if file is a supported code file"""
        _, ext = os.path.splitext(filename)
        return ext.lower() in CodeUtils.get_supported_extensions()


# Export utility classes
__all__ = ['ModelUtils', 'DataUtils', 'MetricsUtils', 'CodeUtils']

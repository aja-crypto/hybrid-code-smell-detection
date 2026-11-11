"""
Inference Script for Code Smell Detection

Standalone script for making predictions without running the API server.
Useful for batch processing or integration into other systems.
"""

import argparse
import os
import sys
import torch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ml_pipeline'))

from hybrid_model import HybridCodeSmellModel
from preprocessing import CodePreprocessor, load_code_from_file, validate_code


def load_model(model_path: str, device: str = 'cpu'):
    """
    Load trained model
    
    Args:
        model_path (str): Path to model weights
        device (str): Device to load on
    
    Returns:
        model: Loaded model instance
    """
    print(f"Loading model from {model_path}...")
    
    model = HybridCodeSmellModel(model_name='microsoft/graphcodebert-base')
    
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        print("✓ Model weights loaded successfully")
    else:
        print(f"⚠ Warning: Model file not found at {model_path}")
        print("  Using model with random weights")
    
    model.to(device)
    model.eval()
    
    return model


def analyze_code(model, preprocessor, code: str, device: str = 'cpu'):
    """
    Analyze single code snippet
    
    Args:
        model: Model instance
        preprocessor: Preprocessor instance
        code (str): Code to analyze
        device (str): Device to use
    
    Returns:
        dict: Analysis result
    """
    # Validate code
    is_valid, message = validate_code(code)
    if not is_valid:
        return {'valid': False, 'error': message}
    
    # Get prediction
    with torch.no_grad():
        result = model.predict(code, device=device)
    
    prediction = result['prediction']
    confidence = result['confidence']
    probabilities = result['probabilities']
    
    # Prepare output
    return {
        'valid': True,
        'prediction': prediction,
        'label': 'Code Smell Detected' if prediction == 1 else 'Clean Code',
        'confidence': float(confidence),
        'confidence_percentage': f"{confidence * 100:.2f}%",
        'probabilities': {
            'clean_code': float(probabilities[0]),
            'code_smell': float(probabilities[1])
        }
    }


def main():
    """Main inference function"""
    
    parser = argparse.ArgumentParser(
        description='Code Smell Detection - Inference Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze from stdin
  python inference.py
  
  # Analyze from file
  python inference.py --file code_sample.py
  
  # Use GPU if available
  python inference.py --gpu
  
  # Analyze multiple files
  python inference.py --batch *.py
        """
    )
    
    parser.add_argument('--file', type=str, help='Code file to analyze')
    parser.add_argument('--batch', type=str, help='Pattern for batch analysis (e.g., "*.py")')
    parser.add_argument('--gpu', action='store_true', help='Use GPU if available')
    parser.add_argument('--model', type=str, 
                       default='../ml_pipeline/saved_models/hybrid_code_smell_model.pt',
                       help='Path to model weights')
    
    args = parser.parse_args()
    
    # Setup device
    device = 'cuda' if args.gpu and torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}\n")
    
    # Load model and preprocessor
    model = load_model(args.model, device=device)
    preprocessor = CodePreprocessor()
    print("✓ Preprocessor initialized\n")
    
    # Analyze code
    if args.file:
        # Analyze from file
        print(f"Analyzing file: {args.file}")
        code = load_code_from_file(args.file)
        result = analyze_code(model, preprocessor, code, device=device)
        
        print_result(result, filename=os.path.basename(args.file))
        
    elif args.batch:
        # Batch analysis
        import glob
        files = glob.glob(args.batch)
        
        if not files:
            print(f"No files matching pattern: {args.batch}")
            return
        
        print(f"Analyzing {len(files)} files...\n")
        
        results = []
        for filepath in files:
            code = load_code_from_file(filepath)
            result = analyze_code(model, preprocessor, code, device=device)
            result['file'] = os.path.basename(filepath)
            results.append(result)
            print_result(result, filename=os.path.basename(filepath))
            print("-" * 60)
        
        # Print summary
        print("\n" + "=" * 60)
        print("BATCH ANALYSIS SUMMARY")
        print("=" * 60)
        valid_results = [r for r in results if r.get('valid', False)]
        if valid_results:
            smells_detected = sum(1 for r in valid_results if r['prediction'] == 1)
            print(f"Total files analyzed: {len(valid_results)}")
            print(f"Code smells detected: {smells_detected}")
            print(f"Clean code files: {len(valid_results) - smells_detected}")
            avg_confidence = sum(r['confidence'] for r in valid_results) / len(valid_results)
            print(f"Average confidence: {avg_confidence * 100:.2f}%")
        
    else:
        # Interactive mode
        print("Code Smell Detection - Interactive Mode")
        print("(Enter code below, press Ctrl+D or Ctrl+Z to analyze)")
        print("-" * 60)
        
        try:
            code = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nInterrupted")
            return
        
        result = analyze_code(model, preprocessor, code, device=device)
        print_result(result)


def print_result(result: dict, filename: str = None):
    """Pretty print analysis result"""
    
    if not result.get('valid', False):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    if filename:
        print(f"📄 File: {filename}")
    
    print(f"Result: {result['label']}")
    print(f"Confidence: {result['confidence_percentage']}")
    print(f"\nProbabilities:")
    print(f"  Clean Code:      {result['probabilities']['clean_code']*100:6.2f}%")
    print(f"  Code Smell:      {result['probabilities']['code_smell']*100:6.2f}%")
    
    if result['prediction'] == 1:
        print("\n⚠️  This code appears to have code smells.")
        print("Possible issues:")
        print("  • Long methods or functions")
        print("  • Duplicate code segments")
        print("  • Poor variable naming")
        print("  • Excessive complexity")
    else:
        print("\n✅ This code appears to be clean.")


if __name__ == '__main__':
    main()

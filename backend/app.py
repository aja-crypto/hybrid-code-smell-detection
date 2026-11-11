"""
Flask Backend API for Code Smell Detection

REST API endpoints for:
1. Code analysis (POST /api/analyze)
2. Batch analysis (POST /api/batch-analyze)
3. Health check (GET /api/health)
4. Model info (GET /api/model-info)

MongoDB integration for storing analysis history
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from pymongo import MongoClient
import traceback

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ml_pipeline'))

# --- Optional ML dependencies (demo-safe fallback) ---
ML_AVAILABLE = True
ML_IMPORT_ERROR = None
try:
    import torch  # type: ignore
    from hybrid_model import HybridCodeSmellModel  # type: ignore
    from preprocessing import CodePreprocessor, validate_code  # type: ignore
except Exception as e:
    ML_AVAILABLE = False
    ML_IMPORT_ERROR = str(e)
    torch = None  # type: ignore
    HybridCodeSmellModel = None  # type: ignore
    CodePreprocessor = None  # type: ignore

    def validate_code(code: str, min_length: int = 10):
        if not isinstance(code, str) or not code.strip():
            return False, "Empty code"
        if len(code.strip()) < min_length:
            return False, f"Code is too short (min {min_length} chars)"
        return True, "OK"

import re


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml_pipeline', 'saved_models', 'hybrid_code_smell_model.pt')
DEVICE = None
if ML_AVAILABLE:
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'code_smell_detection'

# Global variables
model = None
preprocessor = None
db = None
model_ready = False


def init_model():
    """
    Initialize the trained model and preprocessor.
    Refuses to run inference with random weights.
    """
    global model, preprocessor, model_ready
    
    try:
        if not ML_AVAILABLE:
            model = None
            preprocessor = None
            model_ready = False
            print("ML dependencies not available. Starting in DEMO mode.")
            print(f"ML import error: {ML_IMPORT_ERROR}")
            return

        print(f"Loading model from {MODEL_PATH}...")
        
        if not os.path.exists(MODEL_PATH):
            print(f"ERROR: Trained model weights not found at {MODEL_PATH}")
            print("Refusing to initialize with random weights.")
            print("Run 'python ml_pipeline/training.py' to train the model first.")
            model = None
            preprocessor = None
            model_ready = False
            return
        
        # Initialize model and preprocessor
        model = HybridCodeSmellModel(model_name='microsoft/graphcodebert-base')
        preprocessor = CodePreprocessor(model_name='microsoft/graphcodebert-base', max_length=512)
        
        # Load trained weights — mandatory
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        print("Model weights loaded successfully")
        
        model.to(DEVICE)
        model.eval()
        model_ready = True
        print("Model initialized successfully")
        
    except Exception as e:
        print(f"Error initializing model: {e}")
        print(traceback.format_exc())
        model = None
        preprocessor = None
        model_ready = False


def demo_predict(code: str):
    """
    Heuristic fallback prediction when ML dependencies are missing.
    This is intended for UI/demo continuity only.
    """
    # Simple smell-ish signals: long code, too many branches, deep nesting, many params.
    length = len(code)
    if_count = len(re.findall(r"\bif\b", code))
    for_count = len(re.findall(r"\bfor\b|\bwhile\b", code))
    try_count = len(re.findall(r"\btry\b|\bcatch\b|\bexcept\b", code))
    params_like = len(re.findall(r",", code.split("\n", 1)[0]))  # rough
    score = 0.0
    score += min(length / 2000.0, 1.0) * 0.35
    score += min((if_count + for_count) / 15.0, 1.0) * 0.35
    score += min(try_count / 5.0, 1.0) * 0.10
    score += min(params_like / 10.0, 1.0) * 0.20
    score = max(0.0, min(score, 1.0))

    # Convert score into a probability-like output.
    prob_smell = 0.15 + 0.7 * score
    prob_smell = max(0.0, min(prob_smell, 0.95))
    prob_clean = 1.0 - prob_smell
    prediction = 1 if prob_smell >= 0.5 else 0
    confidence = max(prob_smell, prob_clean)

    detected_lines = []
    for idx, line in enumerate(code.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) > 120:
            detected_lines.append({
                "line": idx,
                "reason": "Very long line",
                "snippet": stripped[:120]
            })
        elif re.search(r"\b(if|elif|for|while|except)\b", stripped):
            detected_lines.append({
                "line": idx,
                "reason": "Control-flow complexity hotspot",
                "snippet": stripped[:120]
            })
        elif re.search(r"\bprint\(|console\.log\(|System\.out\.print", stripped):
            detected_lines.append({
                "line": idx,
                "reason": "Debug/log statement",
                "snippet": stripped[:120]
            })

    return {
        "prediction": prediction,
        "confidence": float(confidence),
        "probabilities": [float(prob_clean), float(prob_smell)],
        "demo_mode": True,
        "demo_reason": "ML dependencies unavailable on this Python environment",
        "detected_lines": detected_lines[:12]
    }


def init_database():
    """
    Initialize MongoDB connection
    """
    global db
    
    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
            socketTimeoutMS=2000,
        )
        # Force a connection check now (otherwise MongoClient is lazy).
        client.admin.command("ping")
        db = client[DB_NAME]
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB: {e}")
        print("Running without database persistence")
        db = None


def save_analysis_to_db(analysis_result):
    """
    Save analysis result to MongoDB
    
    Args:
        analysis_result (dict): Analysis result to save
    """
    if db is None:
        return
    
    try:
        collection = db['analyses']
        collection.insert_one({
            'timestamp': datetime.utcnow(),
            'code_snippet': analysis_result.get('code', '')[:1000],  # Limit stored code
            'result': analysis_result
        })
    except Exception as e:
        print(f"Error saving to database: {e}")


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON: Status and model information
    """
    return jsonify({
        'status': 'ok',
        'device': str(DEVICE),
        'model_loaded': model_ready,
        'model_ready': model_ready,
        'demo_mode': not model_ready,
        'database_connected': db is not None,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    """
    Get model information
    
    Returns:
        JSON: Model metadata
    """
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'model_name': 'Hybrid Contrastive-Transformer Fusion',
        'base_model': 'microsoft/graphcodebert-base',
        'embedding_dim': 768,
        'max_length': preprocessor.max_length,
        'device': str(DEVICE),
        'description': 'Detects code smells using transformer embeddings and contrastive learning',
        'output_classes': {
            '0': 'No Code Smell (Clean Code)',
            '1': 'Code Smell Detected'
        }
    }), 200


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """
    Analyze single code snippet
    
    Request JSON:
    {
        "code": "source code here",
        "file_name": "optional file name"
    }
    
    Response JSON:
    {
        "prediction": 0 or 1,
        "label": "Clean Code" or "Code Smell",
        "confidence": 0.0-1.0,
        "probabilities": [prob_clean, prob_smell],
        "analysis_time_ms": milliseconds,
        "status": "success"
    }
    """
    try:
        # Validate request
        if not request.json or 'code' not in request.json:
            return jsonify({'error': 'Missing code in request'}), 400
        
        code = request.json.get('code', '').strip()
        file_name = request.json.get('file_name', 'unknown')
        
        # Validate code
        is_valid, message = validate_code(code, min_length=10)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Predict
        start_time = datetime.utcnow()
        
        if not ML_AVAILABLE or model is None:
            result = demo_predict(code)
        else:
            with torch.no_grad():
                result = model.predict(code, device=DEVICE)
        
        end_time = datetime.utcnow()
        analysis_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Prepare response
        prediction = result['prediction']
        confidence = result['confidence']
        label = 'Code Smell Detected' if prediction == 1 else 'Clean Code'
        
        response = {
            'status': 'success',
            'prediction': prediction,
            'label': label,
            'confidence': float(confidence),
            'probabilities': {
                'clean_code': float(result['probabilities'][0]),
                'code_smell': float(result['probabilities'][1])
            },
            'analysis_time_ms': analysis_time_ms,
            'file_name': file_name,
            'demo_mode': bool(result.get('demo_mode', False)),
            'detected_lines': result.get('detected_lines', [])
        }
        
        # Save to database
        save_analysis_to_db({
            'code': code,
            'file_name': file_name,
            **response
        })
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in analyze endpoint: {e}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    Analyze multiple code snippets
    
    Request JSON:
    {
        "codes": [
            {"code": "snippet 1", "file_name": "optional"},
            {"code": "snippet 2", "file_name": "optional"}
        ]
    }
    
    Response JSON:
    {
        "results": [analysis results],
        "summary": {
            "total": number,
            "smells_detected": number,
            "clean_code": number,
            "average_confidence": float
        }
    }
    """
    try:
        if not request.json or 'codes' not in request.json:
            return jsonify({'error': 'Missing codes in request'}), 400
        
        codes = request.json.get('codes', [])
        if not isinstance(codes, list) or len(codes) == 0:
            return jsonify({'error': 'codes must be a non-empty list'}), 400
        
        results = []
        total_confidence = 0
        smells_count = 0
        
        for item in codes:
            if isinstance(item, str):
                code = item
                file_name = 'unknown'
            elif isinstance(item, dict):
                code = item.get('code', '').strip()
                file_name = item.get('file_name', 'unknown')
            else:
                continue
            
            # Validate code
            is_valid, _ = validate_code(code, min_length=10)
            if not is_valid:
                continue
            
            # Predict
            if not ML_AVAILABLE or model is None:
                result = demo_predict(code)
            else:
                with torch.no_grad():
                    result = model.predict(code, device=DEVICE)
            
            prediction = result['prediction']
            confidence = result['confidence']
            label = 'Code Smell Detected' if prediction == 1 else 'Clean Code'
            
            result_item = {
                'file_name': file_name,
                'code_length': len(code),
                'prediction': prediction,
                'label': label,
                'confidence': float(confidence)
            }
            
            results.append(result_item)
            total_confidence += confidence
            if prediction == 1:
                smells_count += 1
        
        summary = {
            'total': len(results),
            'smells_detected': smells_count,
            'clean_code': len(results) - smells_count,
            'average_confidence': float(total_confidence / len(results)) if results else 0
        }
        
        return jsonify({
            'status': 'success',
            'results': results,
            'summary': summary,
            'demo_mode': (not ML_AVAILABLE or model is None)
        }), 200
        
    except Exception as e:
        print(f"Error in batch_analyze endpoint: {e}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Analyze code from uploaded file
    
    Request: Multi-part form with file
    
    Response: Analysis result
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content
        try:
            code = file.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return jsonify({'error': f'Could not read file: {str(e)}'}), 400
        
        # Validate code
        is_valid, message = validate_code(code, min_length=10)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Predict
        if not ML_AVAILABLE or model is None:
            result = demo_predict(code)
        else:
            with torch.no_grad():
                result = model.predict(code, device=DEVICE)
        
        prediction = result['prediction']
        confidence = result['confidence']
        label = 'Code Smell Detected' if prediction == 1 else 'Clean Code'
        
        response = {
            'status': 'success',
            'file_name': file.filename,
            'prediction': prediction,
            'label': label,
            'confidence': float(confidence),
            'probabilities': {
                'clean_code': float(result['probabilities'][0]),
                'code_smell': float(result['probabilities'][1])
            },
            'demo_mode': bool(result.get('demo_mode', False)),
            'detected_lines': result.get('detected_lines', [])
        }
        
        # Save to database
        save_analysis_to_db({
            'code': code,
            'file_name': file.filename,
            **response
        })
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in upload endpoint: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Get analysis history from database
    
    Query params:
    - limit: max number of records (default: 50)
    
    Response: List of previous analyses
    """
    if db is None:
        return jsonify({
            'status': 'success',
            'count': 0,
            'history': [],
            'warning': 'Database not available'
        }), 200
    
    try:
        limit = request.args.get('limit', default=50, type=int)
        collection = db['analyses']
        
        # Get latest records
        records = list(collection.find().sort('timestamp', -1).limit(limit))
        
        # Convert to JSON serializable format (robust to mixed timestamp types)
        for record in records:
            record['_id'] = str(record.get('_id', ''))
            ts = record.get('timestamp')
            if hasattr(ts, 'isoformat'):
                record['timestamp'] = ts.isoformat()
            elif ts is None:
                record['timestamp'] = None
            else:
                record['timestamp'] = str(ts)
        
        return jsonify({
            'status': 'success',
            'count': len(records),
            'history': records
        }), 200
        
    except Exception as e:
        # Never break the UI because history failed.
        return jsonify({
            'status': 'success',
            'count': 0,
            'history': [],
            'warning': f'Could not load history: {str(e)}'
        }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize model and database
    print("Initializing application...")
    init_model()
    init_database()
    
    # Run Flask app
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)

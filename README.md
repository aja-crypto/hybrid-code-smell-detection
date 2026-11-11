# Code Smell Detection System
## Hybrid Contrastive-Transformer Fusion Framework

A comprehensive machine learning system for detecting code smells using transformer-based embeddings and contrastive learning. This project combines GraphCodeBERT with triplet loss and classification layers to identify potential code quality issues.

---

## 📋 Project Overview

### What is a Code Smell?
Code smells are indicators of deeper programming problems that can lead to:
- Long methods or functions
- Duplicate code segments
- Poor variable naming
- Excessive complexity
- Tight coupling between components
- Low code cohesion

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React.js, HTML5, CSS3, Axios |
| **Backend** | Python Flask, Flask-CORS |
| **ML Model** | PyTorch, HuggingFace Transformers |
| **Embeddings** | GraphCodeBERT (microsoft/graphcodebert-base) |
| **Learning** | Triplet Loss + Cross-Entropy Loss |
| **Database** | MongoDB (optional) |

---

## 🏗️ Project Architecture

```
final_year_project/
├── frontend/                 # React.js Application
│   ├── public/              # Static files
│   │   └── index.html
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── AnalysisForm.js
│   │   │   ├── ResultDisplay.js
│   │   │   ├── LoadingSpinner.js
│   │   │   └── HealthCheck.js
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   └── .env.example
│
├── backend/                  # Flask API Server
│   ├── app.py              # Main Flask application
│   └── requirements.txt
│
├── ml_pipeline/             # Machine Learning Components
│   ├── hybrid_model.py      # HybridCodeSmellModel
│   ├── preprocessing.py     # CodePreprocessor, TripletGenerator
│   ├── training.py          # Training script
│   ├── saved_models/        # Trained model weights
│   └── tokenizer/           # GraphCodeBERT tokenizer
│
├── dataset/                 # Training Data
│   ├── train_clean.txt     # Clean code samples
│   └── train_smells.txt    # Code smell samples
│
├── utils/                   # Utility functions
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have installed:
- **Python 3.9+** (for ML pipeline and backend)
- **Node.js 16+** (for frontend)
- **npm** or **yarn** (Node package manager)
- **MongoDB** (optional, for database features)

### Step 1: Clone or Setup Project

```bash
cd c:\Users\purru\OneDrive\Desktop\final_year_project
```

### Step 2: Install Backend Dependencies

```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies

```bash
cd frontend

# Install Node packages
npm install

# Create .env file from template
copy .env.example .env

# On macOS/Linux:
cp .env.example .env
```

### Step 4: Train the Model (Optional)

If you want to train the model from scratch:

```bash
cd ml_pipeline

python training.py
```

This will:
- Load code samples from `dataset/train_clean.txt` and `dataset/train_smells.txt`
- Preprocess the code using GraphCodeBERT tokenizer
- Train the hybrid model with triplet loss + classification loss
- Save the trained model to `saved_models/hybrid_code_smell_model.pt`

### Step 5: Start the Backend Server

```bash
# From project root, with venv activated
cd backend

python app.py
```

The Flask API will be available at: `http://localhost:5000`

### Step 6: Start the Frontend Application

In a new terminal:

```bash
cd frontend

npm start
```

The React app will open at: `http://localhost:3000`

---

## 📚 System Components

### 1. Frontend (React)

**Location:** `frontend/src/`

**Components:**
- `App.js` - Main application component with state management
- `AnalysisForm.js` - Code input, file upload interface
- `ResultDisplay.js` - Results visualization with confidence scores
- `LoadingSpinner.js` - Loading animation
- `HealthCheck.js` - Backend API status indicator

**Features:**
- ✅ Code textarea input (512 tokens max)
- ✅ File upload (.java, .py, .js, .cpp, etc.)
- ✅ Single code analysis
- ✅ Batch analysis (multiple snippets)
- ✅ Results with confidence scores
- ✅ Analysis history display
- ✅ Responsive design

### 2. Backend API (Flask)

**Location:** `backend/app.py`

**Endpoints:**

#### Health Check
```
GET /api/health
Response: {
  "status": "ok",
  "device": "cpu/cuda",
  "model_loaded": true,
  "database_connected": true
}
```

#### Analyze Single Code
```
POST /api/analyze
Request: {
  "code": "source code here",
  "file_name": "optional.py"
}
Response: {
  "status": "success",
  "prediction": 0 or 1,
  "label": "Clean Code" or "Code Smell Detected",
  "confidence": 0.95,
  "probabilities": {
    "clean_code": 0.05,
    "code_smell": 0.95
  },
  "analysis_time_ms": 234
}
```

#### Batch Analysis
```
POST /api/batch-analyze
Request: {
  "codes": [
    {"code": "snippet 1"},
    {"code": "snippet 2"}
  ]
}
Response: {
  "status": "success",
  "results": [...],
  "summary": {
    "total": 2,
    "smells_detected": 1,
    "clean_code": 1,
    "average_confidence": 0.85
  }
}
```

#### Upload File
```
POST /api/upload
(multipart form with file)
Response: Same as /analyze
```

#### Get Model Info
```
GET /api/model-info
Response: {
  "model_name": "Hybrid Contrastive-Transformer Fusion",
  "base_model": "microsoft/graphcodebert-base",
  "embedding_dim": 768,
  "max_length": 512
}
```

#### Analysis History
```
GET /api/history?limit=50
Response: {
  "status": "success",
  "count": 10,
  "history": [...]
}
```

### 3. Machine Learning Model

**Location:** `ml_pipeline/`

#### HybridCodeSmellModel
```python
# Key components:
- GraphCodeBERT encoder (768-dim embeddings)
- Triplet Loss Module (contrastive learning)
- Classification Head (binary classifier)
- Hybrid Loss = Triplet Loss + λ * Classification Loss
```

#### Features:
- **CLS Embeddings**: Extracts contextual code embeddings
- **Triplet Loss**: Minimizes anchor-positive distance, maximizes anchor-negative distance
- **Classification Loss**: Cross-entropy for binary classification
- **Hybrid Training**: Combines both loss functions for better generalization

#### Model Prediction
```python
result = model.predict(code, device='cpu')
# Returns:
{
  'prediction': 0 or 1,
  'confidence': 0.95,
  'logits': array,
  'probabilities': [0.05, 0.95]
}
```

### 4. Preprocessing Module

**Location:** `ml_pipeline/preprocessing.py`

**Functions:**
- `remove_comments()` - Remove single and multi-line comments
- `remove_strings()` - Sanitize string literals
- `normalize_whitespace()` - Clean up whitespace
- `tokenize()` - GraphCodeBERT tokenization
- `preprocess()` - Complete pipeline

### 5. Training Script

**Location:** `ml_pipeline/training.py`

**Features:**
- ✅ Loads data from text files
- ✅ Creates datasets and dataloaders
- ✅ Trains with Adam optimizer
- ✅ Validates on holdout set
- ✅ Saves best model weights
- ✅ Records training history
- ✅ Calculates metrics (Accuracy, Precision, Recall, F1)

---

## 📊 Model Architecture

### Hybrid Architecture

```
Input Code (String)
    ↓
GraphCodeBERT Tokenizer
    ↓
Tokenized Input [batch_size, seq_length]
    ↓
GraphCodeBERT Encoder
    ↓
CLS Token Embeddings [batch_size, 768]
    ↓
Classification Head
    ├→ Linear(768 → 256) + ReLU
    ├→ Dropout(0.1)
    ├→ Linear(256 → 128) + ReLU
    ├→ Dropout(0.1)
    └→ Linear(128 → 2) [Logits]
    ↓
Softmax → Predictions [0/1]
    
Loss = Triplet Loss + 0.5 * Classification Loss
```

### Training Process

1. **Data Loading**: Load clean and code smell samples
2. **Preprocessing**: Clean, tokenize, convert to tensors
3. **Forward Pass**: 
   - Extract embeddings from GraphCodeBERT
   - Pass through classification head
4. **Loss Calculation**:
   - Triplet Loss: Contrastive learning
   - Classification Loss: Cross-entropy
   - Hybrid Loss: Weighted combination
5. **Backward Pass**: Gradient descent with clipping
6. **Validation**: Evaluate on holdout set
7. **Model Saving**: Save best weights based on F1 score

---

## 🎓 Training Instructions

### Dataset Format

**train_clean.txt:**
- One clean code sample per line
- Multi-line code separated by blank lines

**train_smells.txt:**
- One code smell sample per line
- Multi-line code separated by blank lines

### Quick Training

```bash
cd ml_pipeline

# Configure training parameters in training.py:
# - EPOCHS = 5 (or more for better results)
# - BATCH_SIZE = 16
# - LEARNING_RATE = 2e-5

python training.py
```

### Expected Training Output

```
==================================================
Epoch 1/5
==================================================
Epoch 1, Batch 10, Loss: 0.8432
Train Loss: 0.7543
Train Accuracy: 0.6234
Train F1: 0.6124

Val Loss: 0.7891
Val Accuracy: 0.6567
Val Precision: 0.6789
Val Recall: 0.6234
Val F1: 0.6498

New best F1: 0.6498. Saving model...

Training complete! Best F1: 0.6498
Model saved to: ../ml_pipeline/saved_models/hybrid_code_smell_model.pt
```

---

## 💻 Using the Application

### Step 1: Input Code
- **Paste Code**: Use the textarea to paste code directly
- **Upload File**: Click "Upload & Paste" to upload a file (supports .java, .py, .js, .cpp, .c, .ts, .go, .rb, .php, .txt)

### Step 2: Analyze
- Click **"Analyze Code"** for single analysis
- Click **"Batch Analyze"** to analyze multiple snippets (separated by blank lines)

### Step 3: View Results
Results include:
- **Prediction**: Smell Detected / Clean Code
- **Confidence Score**: 0-100% certainty
- **Probability Distribution**: Visual representation
- **Interpretation**: Detailed feedback
- **Technical Details**: Model info and timing

### Step 4: History
Recent analyses are displayed in the history panel on the homepage.

---

## 🔧 Configuration

### Backend Configuration

**Environment Variables (`.env` in `backend/`):**
```
FLASK_ENV=production
MONGODB_URI=mongodb://localhost:27017/
DEBUG=False
```

### Frontend Configuration

**Environment Variables (`.env` in `frontend/`):**
```
REACT_APP_API_URL=http://localhost:5000/api
NODE_ENV=production
```

---

## 📈 Performance Metrics

### Model Evaluation

The model is evaluated using:
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1 Score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Breakdown of predictions

### Reported Performance (example run)

The sample training log shown above corresponds to the following **validation** metrics:

| Metric | Value |
|--------|-------|
| Accuracy | 65.67% |
| Precision | 67.89% |
| Recall | 62.34% |
| F1 Score | 64.98% |

*Note: These values are for a specific run and depend on dataset quality, split strategy, and training settings. Do not confuse per-sample “confidence score” shown in the UI with overall dataset accuracy.*

---

## 🐛 Troubleshooting

### Issue: Backend Server Won't Start

**Solution:**
```bash
# Check if port 5000 is in use
netstat -tulpn | grep 5000

# Kill existing process
lsof -ti:5000 | xargs kill -9

# Check Python packages
pip list | grep -E "flask|torch|transformers"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Frontend Can't Connect to Backend

**Solution:**
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Check frontend .env file
cat frontend/.env

# Verify CORS is enabled in Flask
# Check that app.py has CORS(app)

# Restart frontend
npm start
```

### Issue: Model Loading Error

**Solution:**
```bash
# Check if model file exists
ls -la ml_pipeline/saved_models/

# Download GraphCodeBERT tokenizer
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('microsoft/graphcodebert-base')"

# Train new model
cd ml_pipeline
python training.py
```

### Issue: Out of Memory Error

**Solution:**
```python
# Reduce batch size in training.py:
BATCH_SIZE = 8  # Reduce from 16

# Reduce max sequence length in preprocessing.py:
max_length = 256  # Reduce from 512
```

---

## 📦 Deployment

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ml_pipeline/ ./ml_pipeline/
COPY backend/ ./backend/

EXPOSE 5000

CMD ["python", "backend/app.py"]
```

Build and run:
```bash
docker build -t code-smell-detector .
docker run -p 5000:5000 code-smell-detector
```

### Cloud Deployment (AWS/GCP/Azure)

1. **Backend**: Deploy Flask app to:
   - AWS Lambda + API Gateway
   - Google Cloud Run
   - Azure App Service

2. **Frontend**: Deploy React app to:
   - AWS S3 + CloudFront
   - Google Cloud Storage
   - Azure Static Web Apps

3. **Database**: Use managed MongoDB:
   - AWS DocumentDB
   - MongoDB Atlas

---

## 📚 Code Examples

### Python Backend Usage

```python
from ml_pipeline.hybrid_model import HybridCodeSmellModel
from ml_pipeline.preprocessing import CodePreprocessor
import torch

# Load model and preprocessor
model = HybridCodeSmellModel()
model.load_state_dict(torch.load('saved_models/hybrid_code_smell_model.pt'))
preprocessor = CodePreprocessor()

# Analyze code
code = """
def process_data(data):
    result = []
    for item in data:
        x = item * 2
        y = x + 5
        z = y - 3
        result.append(z)
    return result
"""

result = model.predict(code)
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']*100:.2f}%")
```

### Frontend (React) Usage

```javascript
import axios from 'axios';

const analyzeCode = async (code) => {
  try {
    const response = await axios.post('http://localhost:5000/api/analyze', {
      code: code,
      file_name: 'example.py'
    });
    
    console.log('Result:', response.data);
  } catch (error) {
    console.error('Error:', error);
  }
};
```

---

## 🎯 Future Enhancements

- [ ] Multi-language code smell detection (Java, Python, JavaScript, etc.)
- [ ] Real-time suggestions for code refactoring
- [ ] Code smell severity levels (critical, major, minor)
- [ ] Integration with IDE plugins (VS Code, PyCharm, IntelliJ)
- [ ] Advanced visualization of code structure and issues
- [ ] Machine learning model improvements and retraining
- [ ] REST API rate limiting and authentication
- [ ] User dashboard and analytics

---

## 📄 License

This project is created for educational purposes as part of a final year engineering project.

---

## 👨‍💼 Contributors

- **Author**: Final Year Project Student
- **Advisor**: Your Faculty Advisor
- **University**: Your University Name

---

## 🙏 Acknowledgments

- **GraphCodeBERT**: Microsoft Research
- **PyTorch**: Facebook AI Research
- **HuggingFace**: Hugging Face Team
- **React**: Facebook

---

## ❓ FAQ

**Q: How does the model detect code smells?**
A: The model uses transformer embeddings to understand code context and learns patterns of code smells through contrastive learning with triplet loss.

**Q: What is the maximum code size?**
A: Maximum 512 tokens (approximately 2000-3000 characters depending on the language).

**Q: Can I use a GPU?**
A: Yes! The model automatically detects and uses CUDA if available. Check with `torch.cuda.is_available()`.

**Q: How do I add more training data?**
A: Add samples to `dataset/train_clean.txt` and `dataset/train_smells.txt`, then retrain the model.

**Q: Can I use this in production?**
A: Yes, but consider adding proper error handling, monitoring, and authentication for production deployment.

---

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the documentation
3. Check GitHub issues
4. Contact your project advisor

---

**Happy Code Smell Hunting! 🏴‍☠️🔍**

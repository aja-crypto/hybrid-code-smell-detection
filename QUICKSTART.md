# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Option 1: Automated Setup (Recommended)

#### On Windows:
```bash
cd final_year_project
setup.bat
```

#### On macOS/Linux:
```bash
cd final_year_project
chmod +x setup.sh
./setup.sh
```

---

### Option 2: Manual Setup

#### Step 1: Setup Backend

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Setup Frontend

```bash
cd frontend

# Install Node packages
npm install

# Create environment file
copy .env.example .env
# macOS/Linux:
cp .env.example .env
```

---

## 🎯 Running the Application

### Terminal 1: Start Backend API

```bash
# Make sure virtual environment is activated
cd backend
python app.py
```

**Expected output:**
```
Initializing application...
Loading model from ...
Model initialized successfully
Starting Flask server...
 * Running on http://0.0.0.0:5000
```

### Terminal 2: Start Frontend

```bash
cd frontend
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view the app in your browser.
  Local: http://localhost:3000
```

---

## ✅ Verify Installation

### Check Backend Health

```bash
# In a new terminal
curl http://localhost:5000/api/health
```

**Expected response:**
```json
{
  "status": "ok",
  "device": "cpu",
  "model_loaded": true,
  "database_connected": false
}
```

### Check Frontend

Open your browser and go to: `http://localhost:3000`

You should see the Code Smell Detection interface.

---

## 📝 First Analysis

1. **Paste Code**: Copy-paste code into the textarea or upload a file
2. **Click Analyze**: Press the "Analyze Code" button
3. **View Results**: See predictions with confidence scores

### Test Code

Paste this code to test:

```python
def process_data(data):
    x = data
    for i in range(10):
        x = x + 1
        y = x * 2
        z = y / 2
        data = z
    return data
```

Expected: Should detect as "Code Smell" (inefficient code structure)

---

## 🏋️ Train Custom Model

If you want to train the model with your own data:

```bash
cd ml_pipeline

# Edit the data files:
# - dataset/train_clean.txt (add clean code samples)
# - dataset/train_smells.txt (add code smell samples)

# Run training
python training.py
```

The trained model will be saved to: `saved_models/hybrid_code_smell_model.pt`

---

## 🐛 Common Issues

### Issue: Port Already in Use

```bash
# Kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

### Issue: Module Not Found

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Issue: Can't Connect to Backend

1. Check if Flask server is running (`python app.py`)
2. Check if port 5000 is accessible
3. Check .env file in frontend/ directory

### Issue: Model Loading Error

```bash
# Download required models
python -c "from transformers import AutoModel, AutoTokenizer; AutoModel.from_pretrained('microsoft/graphcodebert-base'); AutoTokenizer.from_pretrained('microsoft/graphcodebert-base')"
```

---

## 📊 API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Check API status |
| `/api/analyze` | POST | Analyze single code |
| `/api/batch-analyze` | POST | Analyze multiple codes |
| `/api/upload` | POST | Upload and analyze file |
| `/api/model-info` | GET | Get model information |
| `/api/history` | GET | Get analysis history |

---

## 📁 Project Structure

```
final_year_project/
├── frontend/              # React web interface
├── backend/               # Flask API server
├── ml_pipeline/           # ML model and training
│   ├── hybrid_model.py   # Main model
│   ├── training.py        # Training script
│   └── preprocessing.py   # Data preprocessing
├── dataset/               # Training data
├── utils/                 # Utility functions
├── requirements.txt       # Python dependencies
└── README.md             # Full documentation
```

---

## 🌐 Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: Available at /api endpoints

---

## 🛑 Stop Services

```bash
# Press Ctrl+C in each terminal to stop the services
```

---

## 📞 Next Steps

1. ✅ **Verify everything works** - Test with provided code sample
2. 📚 **Read full documentation** - See README.md for detailed info
3. 🤖 **Train custom model** - Add your own code samples (optional)
4. 🚀 **Deploy to cloud** - Use Docker (optional)

---

## 💡 Tips

- Max code size: 512 tokens (~2000-3000 characters)
- Supported languages: Java, Python, JavaScript, C++, C, TypeScript, Go, Ruby, PHP
- For best results, use well-formatted code
- Batch analysis is useful for multiple files

---

## 🎓 Project Features

✅ Transformer-based code embeddings (GraphCodeBERT)
✅ Contrastive learning with triplet loss
✅ Binary classification (Smell / No Smell)
✅ Confidence scoring
✅ File upload support
✅ Batch analysis
✅ Analysis history
✅ REST API
✅ React frontend with modern UI
✅ Responsive design

---

**Happy analyzing! 🔍**

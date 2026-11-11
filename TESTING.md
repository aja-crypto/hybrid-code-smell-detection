# Testing and Evaluation Guide

## 🧪 Testing the Code Smell Detection System

### Prerequisites

- Backend server running: `python backend/app.py`
- Frontend server running: `npm start`
- Model loaded and ready

---

## Part 1: Backend API Testing

### 1.1 Health Check Endpoint

```bash
curl -X GET http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "device": "cpu",
  "model_loaded": true,
  "database_connected": false,
  "timestamp": "2024-04-11T10:30:00.000000"
}
```

### 1.2 Model Info Endpoint

```bash
curl -X GET http://localhost:5000/api/model-info
```

**Expected Response:**
```json
{
  "model_name": "Hybrid Contrastive-Transformer Fusion",
  "base_model": "microsoft/graphcodebert-base",
  "embedding_dim": 768,
  "max_length": 512,
  "device": "cpu",
  "description": "...",
  "output_classes": {
    "0": "No Code Smell (Clean Code)",
    "1": "Code Smell Detected"
  }
}
```

### 1.3 Single Code Analysis

Test with clean code:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a + b",
    "file_name": "test.py"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "prediction": 0,
  "label": "Clean Code",
  "confidence": 0.95,
  "probabilities": {
    "clean_code": 0.95,
    "code_smell": 0.05
  },
  "analysis_time_ms": 234,
  "file_name": "test.py"
}
```

Test with code smell:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def process(a):\n    x = a; x = x + 1; x = x * 2; x = x / 3; x = x - 5; x = x + 10; x = x * 2; x = x - 1; return x",
    "file_name": "bad_code.py"
  }'
```

---

## Part 2: Web Interface Testing

### 2.1 UI Components

Open `http://localhost:3000` and verify:

- [ ] Header displays correctly
- [ ] Health status indicator shows (green = connected)
- [ ] Code textarea renders
- [ ] Upload button is functional
- [ ] Analyze button is enabled

### 2.2 Single Code Analysis

1. Paste this clean code:
```python
def calculate_sum(numbers):
    """Calculate sum of numbers."""
    return sum(numbers)
```

2. Click "Analyze Code"
3. Verify:
   - [ ] Result shows "Clean Code"
   - [ ] Confidence > 90%
   - [ ] Analysis time < 1 second

### 2.3 Code Smell Detection

1. Paste this code with smell:
```python
def process_data(data):
    result = []
    for item in data:
        x = item
        x = x + 1
        y = x * 2
        z = y / 2
        data = z
        result.append(data)
    return result
```

2. Click "Analyze Code"
3. Verify:
   - [ ] Result shows "Code Smell Detected"
   - [ ] Confidence shown
   - [ ] Interpretation section displayed

### 2.4 File Upload

1. Create a test file: `test_code.py`
2. Add code to the file
3. Click "Upload & Direct Upload" or drag file
4. Verify:
   - [ ] File name appears in UI
   - [ ] Analysis runs after upload
   - [ ] Results display correctly

### 2.5 Batch Analysis

1. Paste multiple code snippets separated by blank lines:

```python
def func1():
    return 1

def func2():
    x = 1
    y = 2
    z = x + y
    a = z * 2
    b = a / 2
    c = b - 1
    return c
```

2. Click "Batch Analyze"
3. Verify:
   - [ ] Both snippets analyzed
   - [ ] Summary shows total, smells, clean
   - [ ] Confidence scores visible

---

## Part 3: Inference Script Testing

### 3.1 Interactive Mode

```bash
# From project root
python inference.py
# Type or paste code, press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows)
```

### 3.2 File Analysis

```bash
python inference.py --file dataset/train_clean.txt
```

### 3.3 Batch Analysis

```bash
python inference.py --batch "*.py"
```

### 3.4 GPU Testing (if available)

```bash
python inference.py --gpu --file test.py
```

---

## Part 4: Model Training and Evaluation

### 4.1 Train Model

```bash
cd ml_pipeline
python training.py
```

**Expected Output:**
```
Loading data...
Training samples: N
Validation samples: M

==================================================
Epoch 1/5
==================================================
Train Loss: 0.7543
Train Accuracy: 0.6234
Train F1: 0.6124

Val Loss: 0.7891
Val Accuracy: 0.6567
Val Precision: 0.6789
Val Recall: 0.6234
Val F1: 0.6498

New best F1: 0.6498. Saving model...
```

**Important note on metrics consistency:**
- The UI may show **high confidence (e.g., 99%)** for a single prediction. That is **prediction confidence**, not overall model accuracy.
- When reporting results in documentation or PPT, use **validation/test metrics** (Accuracy / Precision / Recall / F1) computed over the full evaluation set.

### 4.2 Evaluate Trained Model

Check the saved training history:

```bash
# Model saved to: saved_models/hybrid_code_smell_model.pt
# History saved to: saved_models/hybrid_code_smell_model_history.json

python -c "
import json
with open('saved_models/hybrid_code_smell_model_history.json') as f:
    history = json.load(f)
    print('Final Validation Metrics:')
    final_val = history['val'][-1]
    for key, value in final_val.items():
        if key != 'confusion_matrix':
            print(f'  {key}: {value:.4f}')
"
```

---

## Part 5: Performance Benchmarking

### 5.1 Inference Speed Test

```python
import time
import torch
from ml_pipeline.hybrid_model import HybridCodeSmellModel

model = HybridCodeSmellModel()
model.load_state_dict(torch.load('ml_pipeline/saved_models/hybrid_code_smell_model.pt'))
model.eval()

test_code = "def test(): return 1"

# Warm up
model.predict(test_code)

# Benchmark
times = []
for _ in range(10):
    start = time.time()
    result = model.predict(test_code)
    times.append(time.time() - start)

avg_time = sum(times) / len(times)
print(f"Average inference time: {avg_time*1000:.2f}ms")
```

### 5.2 Memory Usage Test

```bash
# Monitor memory during inference
# Windows:
wmic os get TotalVisibleMemorySize, FreePhysicalMemory

# Linux:
free -h

# macOS:
vm_stat

# Then run inference and monitor
```

---

## Part 6: Database Testing (Optional)

If MongoDB is running:

```bash
# Check if database is connected
curl http://localhost:5000/api/health | jq .database_connected

# Get analysis history
curl http://localhost:5000/api/history?limit=10
```

---

## Part 7: Error Handling Tests

### 7.1 Empty Code

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": ""}'
```

**Expected:** 400 error - "Missing code in request" or "Code cannot be empty"

### 7.2 Very Long Code

```bash
# Generate long code
python -c "
code = 'x = 1; ' * 100000  # Very long code
print(code)
" | curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "'"'"'long code here'"'"'"}'
```

**Expected:** Still processes (tokens truncated to 512)

### 7.3 Invalid JSON

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d 'invalid json'
```

**Expected:** 400 error

### 7.4 Missing Endpoint

```bash
curl http://localhost:5000/api/nonexistent
```

**Expected:** 404 error

---

## Part 8: Frontend UI Tests

### Test Cases

| Test | Steps | Expected |
|------|-------|----------|
| Load page | Open http://localhost:3000 | Page loads in < 2s |
| Input code | Paste code in textarea | Code appears in field |
| Analyze clean | Upload clean code | "Clean Code" result |
| Analyze smell | Upload code with smell | "Code Smell Detected" |
| Files supported | Try .java, .py, .js | All upload successfully |
| Batch analyze | Multiple snippets | All analyzed |
| Responsive | Resize browser | Layout adjusts on mobile |
| Error handling | Submit empty code | Error message shows |

---

## Part 9: Automated Testing (Optional)

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

```bash
# Start services, then:
python -m pytest tests/integration/ -v
```

---

## Part 10: Performance Metrics

### Collect Metrics

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Make predictions on test set
predictions = [model.predict(code)['prediction'] for code in test_codes]
ground_truth = [1, 0, 1, 0, ...]  # Actual labels

accuracy = accuracy_score(ground_truth, predictions)
precision = precision_score(ground_truth, predictions)
recall = recall_score(ground_truth, predictions)
f1 = f1_score(ground_truth, predictions)

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")
```

---

## Checklist: Full System Test

- [ ] Backend starts without errors
- [ ] Frontend loads properly
- [ ] Health check endpoint responds
- [ ] Single code analysis works
- [ ] Batch analysis works
- [ ] File upload works
- [ ] Results display correctly
- [ ] Confidence scores shown
- [ ] Analysis history displays
- [ ] Error handling works
- [ ] Performance acceptable (< 1sec per analysis)
- [ ] Responsive design works
- [ ] No console errors in browser
- [ ] No errors in backend logs

---

## Troubleshooting Test Failures

See the main README.md file for common issues and solutions.

---

**All tests passing? Great! Your system is ready for production! 🎉**

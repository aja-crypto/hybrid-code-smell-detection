# API Documentation

## Code Smell Detection REST API

Base URL: `http://localhost:5000/api`

---

## Endpoints

### 1. Health Check

Check if the API is running and model is loaded.

**Request:**
```
GET /api/health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "device": "cpu",
  "model_loaded": true,
  "database_connected": false,
  "timestamp": "2024-04-11T10:30:00.000000"
}
```

---

### 2. Model Information

Get detailed information about the model.

**Request:**
```
GET /api/model-info
```

**Response (200 OK):**
```json
{
  "model_name": "Hybrid Contrastive-Transformer Fusion",
  "base_model": "microsoft/graphcodebert-base",
  "embedding_dim": 768,
  "max_length": 512,
  "device": "cpu",
  "description": "Detects code smells using transformer embeddings and contrastive learning",
  "output_classes": {
    "0": "No Code Smell (Clean Code)",
    "1": "Code Smell Detected"
  }
}
```

---

### 3. Analyze Code

Analyze a single code snippet for code smells.

**Request:**
```
POST /api/analyze
Content-Type: application/json

{
  "code": "def add(a, b):\n    return a + b",
  "file_name": "math_utils.py"
}
```

**Parameters:**
- `code` (string, required): Source code to analyze
- `file_name` (string, optional): Name of the file (for logging)

**Response (200 OK):**
```json
{
  "status": "success",
  "prediction": 0,
  "label": "Clean Code",
  "confidence": 0.9532,
  "probabilities": {
    "clean_code": 0.9532,
    "code_smell": 0.0468
  },
  "analysis_time_ms": 234,
  "file_name": "math_utils.py"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Code cannot be empty"
}
```

**Response (500 Internal Server Error):**
```json
{
  "status": "error",
  "error": "Model prediction failed"
}
```

**Fields:**
- `prediction` (0 or 1): 0 = Clean Code, 1 = Code Smell
- `label` (string): Human-readable prediction
- `confidence` (0.0-1.0): Model confidence in prediction
- `probabilities` (object): Probability for each class
- `analysis_time_ms` (int): Analysis duration in milliseconds

---

### 4. Batch Analyze

Analyze multiple code snippets in one request.

**Request:**
```
POST /api/batch-analyze
Content-Type: application/json

{
  "codes": [
    {
      "code": "def add(a, b):\n    return a + b",
      "file_name": "file1.py"
    },
    {
      "code": "x = 1; y = 2; z = x+y; a = z*2; b = a/2; return b",
      "file_name": "file2.py"
    }
  ]
}
```

**Parameters:**
- `codes` (array, required): Array of code objects
  - `code` (string): Source code
  - `file_name` (string, optional): File name

**Response (200 OK):**
```json
{
  "status": "success",
  "results": [
    {
      "file_name": "file1.py",
      "code_length": 25,
      "prediction": 0,
      "label": "Clean Code",
      "confidence": 0.9532
    },
    {
      "file_name": "file2.py",
      "code_length": 45,
      "prediction": 1,
      "label": "Code Smell Detected",
      "confidence": 0.8734
    }
  ],
  "summary": {
    "total": 2,
    "smells_detected": 1,
    "clean_code": 1,
    "average_confidence": 0.9133
  }
}
```

---

### 5. Upload File

Upload and analyze a code file.

**Request:**
```
POST /api/upload
Content-Type: multipart/form-data

[FILE DATA]
```

**Parameters:**
- `file` (file, required): Code file to analyze
  - Supported: .java, .py, .js, .cpp, .c, .ts, .go, .rb, .php, .txt

**Response (200 OK):**
```json
{
  "status": "success",
  "file_name": "MyClass.java",
  "prediction": 1,
  "label": "Code Smell Detected",
  "confidence": 0.8542,
  "probabilities": {
    "clean_code": 0.1458,
    "code_smell": 0.8542
  }
}
```

**Response (400 Bad Request):**
```json
{
  "error": "No file provided"
}
```

---

### 6. Analysis History

Retrieve previous analysis results from database.

**Request:**
```
GET /api/history?limit=50
```

**Query Parameters:**
- `limit` (integer, optional): Maximum number of records (default: 50)

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 5,
  "history": [
    {
      "_id": "60a1b2c3d4e5f6g7h8i9j0k1",
      "timestamp": "2024-04-11T10:30:00.000000",
      "code_snippet": "def test(): ...",
      "result": {
        "status": "success",
        "file_name": "test.py",
        "prediction": 0,
        "label": "Clean Code",
        "confidence": 0.95
      }
    }
  ]
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Analysis completed |
| 400 | Bad Request | Missing or invalid parameters |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Server Error | Model loading failed |
| 503 | Service Unavailable | Database not connected |

### Error Response Format

```json
{
  "error": "Error message describing the issue",
  "status": "error"
}
```

---

## Rate Limiting

No rate limiting currently implemented. Consider adding for production:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## Authentication

Currently no authentication. For production, add API key authentication:

```bash
# Header-based API key
Authorization: Bearer YOUR_API_KEY
```

---

## CORS Headers

All endpoints return CORS-enabled headers:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## Examples

### Example 1: Clean Code Analysis

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def greet(name):\n    \"\"\"Print greeting.\"\"\"\n    print(f\"Hello, {name}!\")",
    "file_name": "greeting.py"
  }'
```

### Example 2: File Upload

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@mycode.py"
```

### Example 3: Batch Analysis with Python

```python
import requests

url = "http://localhost:5000/api/batch-analyze"

data = {
    "codes": [
        {"code": "x = 1 + 2", "file_name": "calc.py"},
        {"code": "def foo(a):\n    x=a\n    y=x+1\n    return y", "file_name": "process.py"}
    ]
}

response = requests.post(url, json=data)
print(response.json())
```

### Example 4: JavaScript Fetch

```javascript
const analyzeCode = async (code) => {
  const response = await fetch('http://localhost:5000/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      code: code,
      file_name: 'sample.js'
    })
  });
  
  const result = await response.json();
  console.log(result);
};

analyzeCode('function add(a, b) { return a + b; }');
```

---

## Performance

### Response Times

- Health check: ~10ms
- Single analysis: 200-500ms (depending on code size)
- Batch analysis: 200-500ms per snippet
- File upload parsing: 50-200ms

### Limits

- Maximum code size: 512 tokens (~2000-3000 characters)
- Maximum batch size: 100 snippets per request
- File size limit: 10MB

---

## Deployment

### Production Checklist

- [ ] Disable debug mode: `DEBUG=False`
- [ ] Add authentication
- [ ] Implement rate limiting
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Add request logging
- [ ] Set up monitoring/alerting
- [ ] Configure database backups
- [ ] Set up error tracking (Sentry)

---

## Support & Troubleshooting

### Common Issues

1. **Model not loading:**
   - Check model file exists at configured path
   - Verify sufficient disk space
   - Check for GPU/CUDA compatibility

2. **Slow analysis:**
   - Check system resources
   - Consider using GPU
   - Reduce code size

3. **Database connection errors:**
   - Verify MongoDB is running
   - Check connection string
   - Verify network connectivity

---

**API Documentation - Last Updated: April 2024**

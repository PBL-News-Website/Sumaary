# Text Summarization API

A Flask-based REST API for text summarization using Facebook's BART model.

## Features

- Text summarization using BART-large-CNN model
- RESTful API with JSON input/output
- Health check endpoint
- Customizable summary length
- CORS support for web applications

## API Endpoints

### Health Check
```
GET /health
```
Returns the API status.

### Summarize Text
```
POST /summarize
```
Request body:
```json
{
  "text": "Your long text here...",
  "max_length": 130,
  "min_length": 30
}
```

Response:
```json
{
  "summary": "Generated summary...",
  "original_length": 500,
  "summary_length": 85
}
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
python app.py
```

3. Test the API:
```bash
python test_local.py
```

## Deployment on Render

This app is ready for deployment on Render with:

- `requirements.txt` - Lists all Python dependencies
- `Procfile` - Specifies the web server command (`web: gunicorn app:app`)

### Steps to Deploy on Render:

1. Push your code to GitHub
2. Connect your GitHub repo to Render
3. Create a new Web Service
4. Render will automatically detect the `requirements.txt` and `Procfile`
5. Your app will be deployed and accessible via the provided URL

### Environment Variables

The app automatically uses Render's `PORT` environment variable. No additional configuration needed.

## File Structure

- `app.py` - Main Flask application
- `model.py` - Original local testing script
- `requirements.txt` - Python dependencies
- `Procfile` - Deployment configuration
- `test_local.py` - Local testing script
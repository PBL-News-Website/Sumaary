from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging
import torch

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model and tokenizer once when the app starts
logger.info("Loading lightweight summarization model...")
# Using a lighter model for faster deployment
MODEL_NAME = "sshleifer/distilbart-cnn-12-6"  # Smaller, faster version of BART

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    low_cpu_mem_usage=True,
    torch_dtype=torch.float32  # Use float32 for CPU
)
logger.info("Model loaded successfully!")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Summarization API is running"})

@app.route('/summarize', methods=['POST'])
def summarize_text():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data['text']
        
        if len(text.strip()) == 0:
            return jsonify({"error": "Empty text provided"}), 400
        
        logger.info(f"Summarizing text of length: {len(text)}")
        
        # Tokenize input with truncation and optimized length
        inputs = tokenizer(
            text, 
            return_tensors="pt", 
            max_length=512,   # Reduced from 1024 for faster processing
            truncation=True,
            padding=False
        )
        
        # Generate summary with optimized parameters
        with torch.no_grad():  # Disable gradient computation for inference
            summary_ids = model.generate(
                inputs["input_ids"], 
                max_length=data.get('max_length', 100),  # Reduced default
                min_length=data.get('min_length', 20),   # Reduced default
                length_penalty=1.5,  # Slightly reduced
                num_beams=2,  # Reduced from 4 for faster inference
                early_stopping=True,
                do_sample=False  # Deterministic output
            )
        
        # Decode the summary
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        logger.info("Summary generated successfully")
        
        return jsonify({
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary)
        })
        
    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500

@app.route('/batch_summarize', methods=['POST'])
def batch_summarize():
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({"error": "No texts provided"}), 400
        
        texts = data['texts']
        if not isinstance(texts, list):
            return jsonify({"error": "texts must be a list"}), 400
        
        summaries = []
        for i, text in enumerate(texts):
            logger.info(f"Processing text {i+1}/{len(texts)}")
            
            inputs = tokenizer(
                text, 
                return_tensors="pt", 
                max_length=512,  # Optimized
                truncation=True,
                padding=False
            )
            
            with torch.no_grad():
                summary_ids = model.generate(
                    inputs["input_ids"], 
                    max_length=data.get('max_length', 100),  # Optimized default
                    min_length=data.get('min_length', 20),   # Optimized default
                    length_penalty=1.5,  # Optimized
                    num_beams=2,     # Optimized for speed
                    early_stopping=True,
                    do_sample=False
                )
            
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summaries.append(summary)
        
        return jsonify({"summaries": summaries})
        
    except Exception as e:
        logger.error(f"Error during batch summarization: {str(e)}")
        return jsonify({"error": f"Batch summarization failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Use environment variables for configuration
    import os
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host=host, port=port)

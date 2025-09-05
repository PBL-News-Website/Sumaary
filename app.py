from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model and tokenizer once when the app starts
logger.info("Loading BART model...")
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
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
        
        # Tokenize input with truncation and max_length
        inputs = tokenizer(
            text, 
            return_tensors="pt", 
            max_length=1024,   # BART limit
            truncation=True
        )
        
        # Generate summary
        summary_ids = model.generate(
            inputs["input_ids"], 
            max_length=data.get('max_length', 130),  # Allow customization
            min_length=data.get('min_length', 30),   # Allow customization
            length_penalty=2.0,
            num_beams=4, 
            early_stopping=True
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
                max_length=1024,
                truncation=True
            )
            
            summary_ids = model.generate(
                inputs["input_ids"], 
                max_length=data.get('max_length', 130),
                min_length=data.get('min_length', 30),
                length_penalty=2.0,
                num_beams=4, 
                early_stopping=True
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

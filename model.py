from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

text = input("Enter the text to summarize: ")

# Add truncation & max_length
inputs = tokenizer(
    text, 
    return_tensors="pt", 
    max_length=1024,   # BART limit
    truncation=True
)

summary_ids = model.generate(
    inputs["input_ids"], 
    max_length=130, 
    min_length=30, 
    length_penalty=2.0,
    num_beams=4, 
    early_stopping=True
)

summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
print(summary)

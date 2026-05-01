import os
import re

INPUT_DIR = "data/raw"
OUTPUT_DIR = "data/processed"

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

def preprocess():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file in os.listdir(INPUT_DIR):
        with open(f"{INPUT_DIR}/{file}", "r", encoding="utf-8") as f:
            text = f.read()

        cleaned = clean_text(text)

        with open(f"{OUTPUT_DIR}/{file}", "w") as f:
            f.write(cleaned)

if __name__ == "__main__":
    preprocess()

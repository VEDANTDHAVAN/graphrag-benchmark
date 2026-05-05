import os
import time
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# ==== OPENAI ====
def openai_generate(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    start = time.time()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    latency = time.time() - start

    text = response.choices[0].message.content
    usage = response.usage

    return {
        "text": text,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "latency": latency   
    }

# ---------------- GEMINI ----------------
def gemini_generate(prompt):
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    model = genai.GenerativeModel("gemini-1.5-flash")

    start = time.time()

    response = model.generate_content(prompt)

    latency = time.time() - start

    text = response.text

    # Gemini free tier doesn’t always return tokens → estimate
    tokens = len(prompt.split()) + len(text.split())

    return {
        "text": text,
        "prompt_tokens": len(prompt.split()),
        "completion_tokens": len(text.split()),
        "total_tokens": tokens,
        "latency": latency
    }


# ---------------- OLLAMA ----------------
def ollama_generate(prompt):
    import requests

    start = time.time()

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    ).json()

    latency = time.time() - start

    text = response["response"]

    tokens = len(prompt.split()) + len(text.split())

    return {
        "text": text,
        "prompt_tokens": len(prompt.split()),
        "completion_tokens": len(text.split()),
        "total_tokens": tokens,
        "latency": latency
    }


# ---------------- MAIN ENTRY ----------------
def generate(prompt):
    if PROVIDER == "openai":
        return openai_generate(prompt)
    elif PROVIDER == "gemini":
        return gemini_generate(prompt)
    elif PROVIDER == "ollama":
        return ollama_generate(prompt)
    else:
        raise ValueError("Invalid LLM provider")
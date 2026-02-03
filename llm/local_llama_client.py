import ollama
import sys
import json
import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from dotenv import load_dotenv
load_dotenv()

def call_llm(prompt, model="mistral"):
    """
    Uses the official Ollama library with strict JSON enforcement.
    Streams output to console so you see activity, but returns clean text.
    """
    print(f"\n[LLM] Generating JSON with {model}...", file=sys.stderr)

    # We append a specific instruction to ensure Mistral behaves
    json_prompt = prompt + "\nRespond using JSON."

    full_response = ""
    
    try:
        stream = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': json_prompt}],
            format='json',       # <--- The Magic Switch: Forces valid JSON
            stream=True,         # stream=True allows us to print characters as they arrive
        )

        for chunk in stream:
            content = chunk['message']['content']
            
            # 1. Print to console (so you see it working)
            sys.stderr.write(content)
            sys.stderr.flush()
            
            # 2. Accumulate for the return value
            full_response += content

        print("", file=sys.stderr) # Newline after finishing
        return full_response

    except Exception as e:
        print(f"\n[LLM] Error: {e}", file=sys.stderr)
        return "[]"

# NVIDIA LLM Call


def call_nvidia_llm(prompt, model="meta/llama-3.3-70b-instruct"):
    """
    Calls NVIDIA NIM model using langchain-nvidia-ai-endpoints.
    Streams output to console and returns final full response.
    """
    print(f"\n[LLM] Calling NVIDIA model {model}...", file=sys.stderr)

    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY missing in .env")

    try:
        llm = ChatNVIDIA(
            model=model,
            api_key=api_key,
            temperature=0.0,
            max_tokens=4096,
            stream=True,
        )

        stream = llm.stream(prompt)

        full_response = ""

        for chunk in stream:
            text = chunk.content
            sys.stderr.write(text)
            sys.stderr.flush()
            full_response += text

        print("", file=sys.stderr)
        return full_response

    except Exception as e:
        print(f"[LLM] NVIDIA Error: {e}", file=sys.stderr)
        return "[]"

# # Test block
# if __name__ == "__main__":
#     test_prompt = "List 3 colors. Return a JSON array."
#     result = call_llm(test_prompt)
#     print("\n--- Result for Code ---")
#     print(result)
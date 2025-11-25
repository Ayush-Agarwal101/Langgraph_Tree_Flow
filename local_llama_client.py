import ollama
import sys
import json

def call_llm(prompt, model="llama2"):
    """
    Uses the official Ollama library with strict JSON enforcement.
    Streams output to console so you see activity, but returns clean text.
    """
    print(f"\n[LLM] Generating JSON with {model}...", file=sys.stderr)

    # We append a specific instruction to ensure Llama2 behaves
    json_prompt = prompt + "\nRespond using JSON."

    full_response = ""
    
    try:
        # stream=True allows us to print characters as they arrive
        stream = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': json_prompt}],
            format='json',  # <--- The Magic Switch: Forces valid JSON
            stream=True,
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

# # Test block
# if __name__ == "__main__":
#     test_prompt = "List 3 colors. Return a JSON array."
#     result = call_llm(test_prompt)
#     print("\n--- Result for Code ---")
#     print(result)
# local_llama_client.py
import subprocess

OLLAMA_PATH = r"C:\Users\ayush\AppData\Local\Programs\Ollama\ollama.exe"

def call_llm(prompt, model="llama2"):
    """
    Safely call Ollama locally with UTF-8 decoding.
    Prevents Windows cp1252 decode errors.
    """

    try:
        process = subprocess.Popen(
            [OLLAMA_PATH, "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False  # IMPORTANT: read raw bytes
        )

        # Send input (UTF-8 encoded)
        out_bytes, err_bytes = process.communicate(prompt.encode("utf-8"))

        # Decode safely
        out = out_bytes.decode("utf-8", errors="replace")
        err = err_bytes.decode("utf-8", errors="replace")

        if err.strip():
            print("[LLM] Ollama stderr:", err)

        return out.strip()

    except Exception as e:
        print(f"[LLM] Ollama call failed: {e}")
        return ""

# llm/local_llama_client.py

import os
from dotenv import load_dotenv
load_dotenv()

import ollama
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langsmith import traceable

# Global Config

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
# options: "ollama" or "nvidia"


# Unified call_llm
@traceable(name="LLM Call")
def call_llm(prompt: str, model: str = "mistral") -> str:
    """
    Unified LLM call.
    Switch provider using LLM_PROVIDER env variable.
    Returns plain string output.
    No streaming.
    """

    if LLM_PROVIDER == "ollama":
        return _call_ollama(prompt, model)

    elif LLM_PROVIDER == "nvidia":
        return _call_nvidia(prompt, model)

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")

# Ollama (Non-streaming)

def _call_ollama(prompt: str, model: str) -> str:
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return response["message"]["content"]


# NVIDIA (Non-streaming)

def _call_nvidia(prompt: str, model: str) -> str:
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY missing in .env")

    llm = ChatNVIDIA(
        model=model,
        api_key=api_key,
        temperature=0.0,
        max_tokens=4096,
    )

    response = llm.invoke(prompt)

    return response.content
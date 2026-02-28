# core/llm_structured.py

import re
import json
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from llm.local_llama_client import call_llm
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class StructuredLLM:
    def __init__(self, model: str = None):

        provider = os.getenv("LLM_PROVIDER", "ollama")

        if model:
            self.model = model
        else:
            if provider == "nvidia":
                self.model = os.getenv("NVIDIA_DEFAULT_MODEL", "meta/llama3-70b-instruct")
            else:
                self.model = os.getenv("OLLAMA_DEFAULT_MODEL", "mistral")

    @traceable(name="Structured LLM Call")
    def call(
            self,
            prompt: str,
            schema: Type[T],
            *,
            system_context: str | None = None,
            max_retries: int = 2
    ) -> T:
        """
        Structured LLM call that enforces strict JSON output
        and parses it into the provided schema.
        """

        json_enforcer = """
    You must respond ONLY with valid JSON.
    Do NOT include explanation.
    Do NOT include markdown.
    Do NOT include the schema.
    Only output the final JSON object.
    """

        # Build full prompt
        if system_context:
            full_prompt = (
                f"{system_context}\n\n"
                f"{json_enforcer}\n\n"
                f"{prompt}"
            )
        else:
            full_prompt = f"{json_enforcer}\n\n{prompt}"

        # Retry loop
        for attempt in range(max_retries + 1):
            raw_output = call_llm(full_prompt, model=self.model)

            try:
                # Extract first JSON object from response
                json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

                if not json_match:
                    raise ValueError("No JSON object found in LLM output.")

                json_str = json_match.group(0)

                parsed = json.loads(json_str)
                return schema(**parsed)

            except Exception as e:
                print(f"[StructuredLLM] Attempt {attempt} failed")
                print("Raw output:", raw_output)
                print("Error:", str(e))

                if attempt == max_retries:
                    raise RuntimeError(
                        f"Structured LLM failed after {max_retries} retries."
                    )
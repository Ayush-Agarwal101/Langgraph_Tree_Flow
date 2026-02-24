# core/llm_structured.py

import json
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from llm.local_llama_client import call_llm
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class StructuredLLM:
    def __init__(self, model: str = None):
        self.model = model or os.getenv("DEFAULT_LLM_MODEL", "mistral")

    @traceable(name="Structured LLM Call")
    def call(self, prompt: str, schema: Type[T], max_retries: int = 2) -> T:
        system_prompt = """
        You must respond ONLY with valid JSON.
        Do NOT include explanation.
        Do NOT include markdown.
        Do NOT include the schema.
        Only output the final JSON object.
        """

        full_prompt = system_prompt + "\n\n" + prompt

        for attempt in range(max_retries + 1):
            raw_output = call_llm(full_prompt, model=self.model)

            try:
                parsed = json.loads(raw_output)
                return schema(**parsed)

            except Exception as e:
                print(f"[StructuredLLM] Attempt {attempt} failed")
                print("Raw output:", raw_output)
                print("Error:", str(e))

                if attempt == max_retries:
                    raise RuntimeError(
                        f"Structured LLM failed after {max_retries} retries."
                    )

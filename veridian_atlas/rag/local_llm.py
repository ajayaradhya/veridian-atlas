"""
local_llm.py
------------
Wrapper around Qwen 1.5B for CPU inference.

Install:
    pip install transformers accelerate
    pip install qwen-vl-utils (if vision later)
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


class LocalQwenLLM:
    def __init__(self, model_name="Qwen/Qwen1.5-1.8B-Chat"):
        print("[LLM] Loading Qwen model... (CPU mode)")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map="cpu"
        )

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cpu")
        output = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.2,
            do_sample=False
        )
        return self.tokenizer.decode(output[0], skip_special_tokens=True)

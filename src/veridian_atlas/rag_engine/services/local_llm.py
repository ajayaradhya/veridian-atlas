"""
local_llm.py
------------
Local Qwen wrapper for 0.5B instruct model optimized for GTX 1060 or CPU.
Ensures deterministic output with correct JSON extraction.
"""

import torch
import re
import json
from transformers import AutoModelForCausalLM, AutoTokenizer

_MODEL = None
_TOKENIZER = None
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


def _extract_json(text: str):
    """
    Extract first JSON object block safely.
    If no valid JSON is found, return raw text.
    """
    match = re.search(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", text, re.DOTALL)
    return match.group(0).strip() if match else text.strip()


def get_qwen():
    """
    Singleton load – prevents repeatedly reloading the model.
    """
    global _MODEL, _TOKENIZER
    if _MODEL is not None and _TOKENIZER is not None:
        return _MODEL, _TOKENIZER

    use_gpu = torch.cuda.is_available()
    device = torch.device("cuda" if use_gpu else "cpu")
    dtype = torch.float16 if use_gpu else torch.float32

    print(f"[LLM] Loading Qwen-0.5B → {device}")

    _TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

    _MODEL = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=dtype, trust_remote_code=True
    ).to(device)

    if use_gpu:
        print(f"[GPU READY] {torch.cuda.get_device_name(0)}")
        print(f"[VRAM USED] {torch.cuda.memory_allocated()/1024**2:.2f} MB\n")
    else:
        print("[CPU MODE] Running slower but stable.\n")

    return _MODEL, _TOKENIZER


def generate_response(prompt: str, max_tokens: int = 256) -> dict:
    """
    Deterministic generation – no sampling noise.
    Returns parsed JSON or a fallback dict.
    """
    model, tokenizer = get_qwen()
    device = next(model.parameters()).device

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    output = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=False,  # Ensures reproducible output
        temperature=None,
        top_k=None,
        top_p=None,
        pad_token_id=tokenizer.eos_token_id,
        repetition_penalty=1.05,
        eos_token_id=tokenizer.eos_token_id,
    )

    text = tokenizer.decode(output[0], skip_special_tokens=True)

    # Remove prompt echo if the model repeats input
    if prompt in text:
        text = text.replace(prompt, "").strip()

    extracted = _extract_json(text)

    # Try to parse JSON safely
    try:
        return json.loads(extracted)
    except json.JSONDecodeError:
        return {"answer": "The model did not return valid JSON.", "citations": []}

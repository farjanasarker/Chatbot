#!/usr/bin/env python3
"""
Test script for local LLM inference
"""
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

def test_model():
    print("Testing Qwen 2.5 1.5B model loading...")

    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        print("Model loaded successfully!")

        # Test inference
        prompt = "System: You are a helpful assistant.\nUser: Hello, how are you?\nAssistant:"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Test response: {response}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model()
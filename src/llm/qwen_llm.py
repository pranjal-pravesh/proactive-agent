import time
import re
from llama_cpp import Llama

class QwenLLM:
    def __init__(self, model_path, n_ctx=2048, n_threads=8):
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False
            )
            print("Qwen3-1.7B GGUF model loaded.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.llm = None

    @staticmethod
    def remove_think_tags(text):
        # Remove <think></think> or <think>   </think> (whitespace-only content)
        text = re.sub(r'<think>\s*</think>', '', text, flags=re.DOTALL)

        # Remove standalone <think> or </think> tags with no matching content
        text = re.sub(r'</?think>', '', text)

        return text.strip()


    def generate(self, user_input, max_tokens=2000, temperature=0.7, top_p=0.9):
        if not self.llm:
            return "[LLM not loaded]"
        formatted_prompt = (
            "<|im_start|>system\n"
            "You are a concise assistant. Do not include your thinking process. I repeat, thinking is prohibited. "
            "Do not explain your reasoning unless asked. Just answer directly.\n"
            "<|im_end|>\n"
            "<|im_start|>user\n"
            f"{user_input}\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        start_time = time.time()
        output = self.llm(
            formatted_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=["<|im_end|>"],
        )
        end_time = time.time()
        response = output["choices"][0]["text"].strip()
        cleaned_response = self.remove_think_tags(response)
        return cleaned_response, end_time - start_time

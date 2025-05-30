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
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Remove standalone <think> or </think> tags with no matching content
        text = re.sub(r'</?think>', '', text)

        # Remove only the most obvious thinking patterns at the start
        thinking_patterns = [
            r'^(Okay,?\s*let\'s see\.?\s*)',
            r'^(Let me think about this\.?\s*)',
            r'^(Hmm,?\s*let me check\.?\s*)',
            r'^(Looking at the context\.?\s*)',
            r'^(The user is asking.*?\.?\s*)',
        ]
        
        for pattern in thinking_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove verbose reasoning patterns in the middle (but be more conservative)
        reasoning_patterns = [
            r'\s*So,?\s*based on that,?\s*the answer is\s*',
            r'\s*Therefore,?\s*the answer is\s*',
            r'\s*From the context.*?\.?\s*So\s*',
        ]
        
        for pattern in reasoning_patterns:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)

        # Clean extra whitespace and return
        text = re.sub(r'\s+', ' ', text).strip()
        return text


    def generate(self, user_input, max_tokens=2000, temperature=0.7, top_p=0.9, tools_prompt=""):
        if not self.llm:
            return "[LLM not loaded]", 0
        
        # Build system prompt with optional tools support
        system_prompt = ("You are a helpful assistant answering to user's queries. "
                        "Use the context and conversation history if helpful.\n\n"
                        "Guidelines:\n"
                        "- Provide complete, helpful answers to the user's questions\n"
                        "- Avoid showing your reasoning process or thinking steps\n"
                        "- Be direct but informative\n"
                        "- If you don't know something, say so clearly")
        
        if tools_prompt:
            system_prompt += tools_prompt
        
        formatted_prompt = (
            "<|im_start|>system\n"
            f"{system_prompt}\n"
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

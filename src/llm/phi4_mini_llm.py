import time
import re
import json
from llama_cpp import Llama

class Phi4MiniLLM:
    def __init__(self, model_path, n_ctx=2048, n_threads=8):
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False
            )
            print("Phi-4-mini-instruct GGUF model loaded.")
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

    def _convert_tools_to_phi4_format(self, tools_prompt):
        """Convert our tool descriptions to Phi-4's JSON format"""
        if not tools_prompt:
            return None
        
        # Extract tool information from our tools prompt
        # This is a simplified conversion - in a real implementation you might want to parse this more carefully
        tools_json = []
        
        # For now, we'll create a simplified tool definition for Phi-4
        # This assumes we're mainly using the calculator tool
        tools_json.append({
            "name": "calculator",
            "description": "Perform mathematical calculations using mathematical expressions and formulas. Use mathematical notation, not natural language descriptions.",
            "parameters": {
                "expression": {
                    "description": "Mathematical expression using proper mathematical notation. Use: +, -, *, /, ^, sqrt(), sin(), cos(), tan(), log(), pi, e, factorial(). Examples: '2*pi*7', 'pi*7^2', '7!/2!', 'sqrt(144)', 'sin(pi/2)', 'sin(59 degrees)', etc.",
                    "type": "str",
                    "default": ""
                },
                "mode": {
                    "description": "Calculation mode: evaluate, simplify, expand, factor, solve, integrate, differentiate, limit",
                    "type": "str", 
                    "default": "evaluate"
                }
            }
        })
        
        # Add weather tool
        tools_json.append({
            "name": "weather_checker",
            "description": "Get weather information for a specific location",
            "parameters": {
                "location": {
                    "description": "The location to get weather for",
                    "type": "str",
                    "default": ""
                }
            }
        })
        
        # Add calendar tool
        tools_json.append({
            "name": "calendar_scheduler", 
            "description": "Schedule meetings and events",
            "parameters": {
                "action": {
                    "description": "Action to perform: schedule, list, cancel",
                    "type": "str",
                    "default": "schedule"
                },
                "title": {
                    "description": "Event title",
                    "type": "str", 
                    "default": ""
                },
                "date": {
                    "description": "Event date",
                    "type": "str",
                    "default": ""
                },
                "time": {
                    "description": "Event time", 
                    "type": "str",
                    "default": ""
                }
            }
        })
        
        return json.dumps(tools_json)

    def generate(self, user_input, max_tokens=2000, temperature=0.7, top_p=0.9, tools_prompt=""):
        if not self.llm:
            return "[LLM not loaded]", 0
        
        # Build system prompt
        system_prompt = ("You are a helpful and knowledgeable voice assistant. "
                        "You can answer questions about many topics including geography, science, history, mathematics, and general knowledge. "
                        "Use the context and conversation history if helpful.\n\n"
                        "Try to be brief and concise. If you can answer the question in a few words, do not elaborate. But don't force yourself to answer in a few words if the topic is complex.\n\n"
                        "Guidelines:\n"
                        "- Provide complete, helpful answers to the user's questions\n"
                        "- Avoid showing your reasoning process or thinking steps\n"
                        "- You can discuss countries, places, science, history, and general knowledge freely\n"
                        "- Be direct but informative and friendly\n"
                        "- If you truly don't know something specific, say so clearly\n"
                        "- Don't refuse to answer reasonable questions\n"
                        "- Each question should be answered independently")
        
        # Build prompt based on whether tools are available
        if tools_prompt:
            # Use tool-enabled format
            tools_json = self._convert_tools_to_phi4_format(tools_prompt)
            
            system_prompt += ("\n\nYou have access to tools. Don't use the tools if you can answer the question without them. When a user's request requires using a tool, "
                            "respond with a tool call in this exact format:\n\n"
                            "<tool_call>\n"
                            "{\n"
                            '    "tool_name": "tool_name_here",\n'
                            '    "parameters": {\n'
                            '        "param1": "value1",\n'
                            '        "param2": "value2"\n'
                            "    }\n"
                            "}\n"
                            "</tool_call>\n\n"
                            "IMPORTANT RULES:\n"
                            "- ALWAYS wrap tool calls with <tool_call> and </tool_call> tags\n"
                            "- For calculator: PRESERVE units like 'degrees' in expressions\n"
                            "- Use 'evaluate' mode for calculator unless specifically solving equations\n"
                            "- Only use tools when the request requires computation, external data, or specific functionality")
            
            formatted_prompt = (
                f"<|system|>{system_prompt}<|tool|>{tools_json}<|/tool|><|end|>"
                f"<|user|>{user_input}<|end|>"
                f"<|assistant|>"
            )
        else:
            # Use regular chat format
            formatted_prompt = (
                f"<|system|>{system_prompt}<|end|>"
                f"<|user|>{user_input}<|end|>"
                f"<|assistant|>"
            )
        
        start_time = time.time()
        output = self.llm(
            formatted_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=["<|end|>", "<|user|>", "<|system|>"],
        )
        end_time = time.time()
        response = output["choices"][0]["text"].strip()
        cleaned_response = self.remove_think_tags(response)
        return cleaned_response, end_time - start_time 
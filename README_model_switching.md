# Model Switching Guide

The voice assistant now supports two LLM models:

## Available Models

### 1. Qwen3-1.7B (Default)
- **File**: `models/Qwen3-1.7B-Q4_0.gguf`
- **Config**: `configs/config.yaml`
- **Model type**: `qwen3`

### 2. Phi-4-mini-instruct
- **File**: `models/Phi-4-mini-instruct-Q4_K_M.gguf`
- **Config**: `configs/config_phi4mini.yaml`
- **Model type**: `phi4mini`

## How to Switch Models

### Method 1: Use different config files
```bash
# Run with Qwen3 (default)
python main.py --config configs/config.yaml

# Run with Phi-4-mini
python main.py --config configs/config_phi4mini.yaml
```

### Method 2: Edit config file
Edit `configs/config.yaml` and change:
```yaml
llm:
  model_type: "qwen3"  # Change to "phi4mini"
  model_path: "models/Qwen3-1.7B-Q4_0.gguf"  # Change to "models/Phi-4-mini-instruct-Q4_K_M.gguf"
```

## Key Differences

### Qwen3-1.7B
- Smaller model (1.7B parameters)
- Uses `<|im_start|>` prompt format
- Custom tool calling integration
- Faster inference

### Phi-4-mini
- Larger model (better performance)
- Uses `<|system|>`, `<|user|>`, `<|assistant|>` format
- Native tool calling support with `<|tool|>` tokens
- More advanced reasoning capabilities

## Tool Calling

Both models support the same tool calling format:
```
<tool_call>
{
    "tool_name": "calculator",
    "parameters": {
        "expression": "sin(59 degrees)/cos(22 degrees)"
    }
}
</tool_call>
```

### Available Tools

1. **Calculator** - Mathematical calculations and expressions
   - Supports complex math, trigonometry, factorials, etc.
   - Handles degree/radian conversions automatically
   - Example: "Calculate the area of a circle with radius 5"

2. **Weather Checker** - Real-time weather information using weatherstack API
   - Current weather conditions and temperature
   - Requires API key configuration (see WEATHER_SETUP.md)
   - Example: "What's the weather like in London?"

3. **Calendar Scheduler** - Meeting and event management
   - Schedule, list, and cancel events
   - Example: "Schedule a meeting tomorrow at 2 PM"

## Model Files Location

Make sure your model files are in the `models/` directory:
```
models/
├── Qwen3-1.7B-Q4_0.gguf
└── Phi-4-mini-instruct-Q4_K_M.gguf
```

## Weather API Setup

To enable weather functionality:

1. Get a free API key from [weatherstack.com](https://weatherstack.com/signup)
2. **Quick Setup**: Run `python setup_weather.py` to create your .env file
3. Edit `.env` and add your API key: `WEATHERSTACK_API_KEY=your_key_here`
4. Or set environment variable: `WEATHERSTACK_API_KEY=your_key_here`
5. See `WEATHER_SETUP.md` for detailed instructions

**Security Note**: The `.env` file is automatically excluded from git to keep your API key secure.

## Dependencies

Install required packages:
```bash
pip install -r requirements.txt
``` 
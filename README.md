# Proactive Voice Assistant Agent

A modular voice assistant system that continuously listens to audio, detects voice activity, transcribes speech to text, understands user intents, keeps conversational context, analyzes sentiment, and executes tasks based on recognized commands.

## Features

- **Speech-to-Text (STT):** Real-time speech transcription using Whisper
- **Voice Activity Detection (VAD):** Using Silero VAD to detect when the user is speaking
- **Intent Recognition:** NLP models to extract user intents from transcriptions
- **Sentiment Analysis:** To understand user emotions
- **Contextual Memory:** Maintains context across interactions
- **Task Executor:** Performs actions based on recognized intents
- **Main Orchestrator:** Ties all modules together in an event-driven, always-listening pipeline

## Project Structure

```
proactive-agent/
├── configs/               # Configuration files
│   └── config.yaml        # Main configuration 
├── src/                   # Source code
│   ├── stt/               # Speech-to-Text module
│   ├── vad/               # Voice Activity Detection module
│   ├── intent/            # Intent Recognition module
│   ├── sentiment/         # Sentiment Analysis module
│   ├── context/           # Context Management module
│   └── executor/          # Task Execution module
├── tests/                 # Unit tests
│   ├── stt/               # STT tests
│   ├── vad/               # VAD tests
│   ├── intent/            # Intent tests
│   ├── sentiment/         # Sentiment tests
│   ├── context/           # Context tests
│   └── executor/          # Executor tests
├── main.py                # Main entry point
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/proactive-agent.git
   cd proactive-agent
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the voice assistant:
   ```
   python main.py --config configs/config.yaml
   ```

## Configuration

The system is configured through YAML files in the `configs` directory. You can modify:

- Audio settings (sample rate, block duration)
- STT model settings (model size, compute type, device)
- VAD settings (threshold, speech padding)
- Intent recognition settings
- Sentiment analysis settings
- Context management settings
- Task execution settings

## Development

### Running Tests

```
python -m unittest discover -s tests
```

### Adding New Tasks

To add a new task:

1. Implement a task handler function
2. Register it with the TaskExecutor in `main.py`:
   ```python
   assistant.task_executor.register_task("task_name", task_handler)
   ```

## License

MIT

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Silero VAD](https://github.com/snakers4/silero-vad) for voice activity detection
- Other open-source libraries and frameworks used in this project 
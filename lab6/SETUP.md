# Setup Instructions

## Installing Ollama (FREE - Runs Locally)

1. **Install Ollama**:
   - **macOS**: 
     ```bash
     brew install ollama
     ```
     Or download from https://ollama.ai
   - **Linux**: 
     ```bash
     curl -fsSL https://ollama.ai/install.sh | sh
     ```
   - **Windows**: Download from https://ollama.ai

2. **Start Ollama server** (in a separate terminal):
   ```bash
   ollama serve
   ```
   Keep this running while you use the app.

3. **Pull a model** (in another terminal):
   ```bash
   ollama pull llama2
   # or try other models:
   ollama pull mistral
   ollama pull phi
   ollama pull gemma
   ```
   
   This downloads the model to your local machine (first time may take a few minutes).

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## Notes

- **Ollama is completely FREE** - runs models locally on your machine
- No API keys or billing required
- Models are downloaded once and stored locally
- First generation may be slower as the model loads into memory
- Make sure Ollama server is running (`ollama serve`) before using the app

## Troubleshooting

- **"Cannot connect to Ollama"**: Make sure `ollama serve` is running in a separate terminal
- **"Model not found"**: Pull the model first with `ollama pull <model-name>`
- **Slow responses**: This is normal for local models. Larger models are slower but better quality
- **Out of memory**: Try a smaller model like `phi` or `gemma:2b`

## Available Models

Popular free models you can use:
- `llama2` - Good general purpose model
- `llama3` - Newer version of Llama
- `mistral` - Fast and efficient
- `phi` - Small and fast
- `gemma` - Google's open model
- `qwen` - Alibaba's model

Check available models: `ollama list`

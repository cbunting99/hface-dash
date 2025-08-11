# Transformers Dashboard

A web-based dashboard for managing, running, and monitoring AI models using Hugging Face's transformers library and OpenAI-compatible endpoints.

## Features
- Launch and monitor models using Hugging Face transformers
- Interact with OpenAI API
- View model status and logs
- Extensible for custom model services

## Project Structure
```
api/              # API endpoints (dashboard, OpenAI)
data/             # Data files
models/           # Model files
services/         # Model management logic
static/           # Frontend JS
templates/        # HTML templates
main.py           # App entry point
Dockerfile        # Container config
requirements.txt  # Python dependencies
```

## Setup
1. Clone the repo:
   ```powershell
   git clone https://github.com/cbunting99/hface-dash.git
   cd hface-dash
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv .env
   .env\Scripts\activate
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run the app:
   ```powershell
   python main.py
   ```

## Docker
To build and run with Docker:
```powershell
   docker build -t transformers-dashboard .
   docker run -p 5000:5000 transformers-dashboard
```

## Using Hugging Face Transformers

This dashboard uses Hugging Face's `transformers` library for model management and inference.

### Install transformers
Add to your environment:
```powershell
pip install transformers==4.41.1
```

### Example Usage
You can use `transformers` in your Python code to load and run models:
```python
from transformers import pipeline

# Load a text-generation pipeline
generator = pipeline('text-generation', model='gpt2')
result = generator('Hello, world!', max_length=50)
print(result)
```

Integrate this logic in your API or services for custom model endpoints.

## Testing
To run tests (if available):
```powershell
   python -m unittest discover
```

## License
See LICENSE for details.

---

**Happy AI model management! 🤖✨**
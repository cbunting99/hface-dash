# VLLM Dashboard

A comprehensive web dashboard for managing VLLM models with OpenAI-compatible API support.

## 🚀 Features

- **Model Management**: Download, load, unload, and delete models from HuggingFace
- **Progress Tracking**: Real-time download progress with detailed status updates
- **System Monitoring**: CPU, memory, and disk usage monitoring
- **OpenAI API**: Compatible with OpenAI API format for seamless integration
- **Web Interface**: Modern, responsive dashboard for easy model management
- **Docker Support**: Fully containerized with GPU support

## 🛠 Quick Start

### Prerequisites

- Docker with NVIDIA Container Toolkit
- NVIDIA GPU with CUDA support

### Option 1: Using the startup script

```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Docker commands

```bash
# Create directories
mkdir -p models data

# Build and start
docker-compose up --build
```

### Option 3: Local development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA support
pip install torch==2.1.2+cu118 --index-url https://download.pytorch.org/whl/cu118

# Create directories
mkdir -p models data static templates

# Run the application
python main.py
```

## 🌐 Access Points

- **Web Dashboard**: http://localhost:8000
- **OpenAI API**: http://localhost:8000/v1

## 📖 Usage Guide

### 1. Download Models

1. Enter a **Model Name** (e.g., "my-chat-model")
2. Enter the **HuggingFace Model ID** (e.g., "microsoft/DialoGPT-medium")
3. Click **Download** and watch the progress bar

### 2. Load Models

- Click the **Load** button on any downloaded model
- Wait for the model to load into GPU memory
- The status will change to "Loaded"

### 3. Test Generation

1. Select a loaded model from the dropdown
2. Enter your prompt
3. Adjust max tokens and temperature
4. Click **Generate**

### 4. VS Code Integration

Configure your VS Code AI extension:
- **Base URL**: `http://localhost:8000/v1`
- **Model**: Any loaded model name from the dashboard

## 🔧 API Endpoints

### Dashboard API (`/api`)

- `GET /api/models` - List all models
- `GET /api/system` - System information
- `POST /api/models/download` - Download a model
- `POST /api/models/{name}/load` - Load a model
- `POST /api/models/{name}/unload` - Unload a model
- `DELETE /api/models/{name}` - Delete a model
- `POST /api/generate` - Generate text

### OpenAI API (`/v1`)

- `GET /v1/models` - List loaded models
- `POST /v1/chat/completions` - Chat completions
- `POST /v1/completions` - Text completions

## 💡 Example API Usage

### Chat Completion

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Text Completion

```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "prompt": "The future of AI is",
    "max_tokens": 50,
    "temperature": 0.7
  }'
```

## 🐛 Troubleshooting

### Common Issues

1. **Docker build fails**: 
   - Make sure you have NVIDIA Container Toolkit installed
   - Try using a different CUDA base image version

2. **GPU not detected**: 
   - Ensure NVIDIA drivers are installed
   - Check that `nvidia-smi` works in your system

3. **Out of memory**: 
   - Reduce `gpu_memory_utilization` in `services/model_manager.py`
   - Try smaller models first

4. **Model download fails**: 
   - Check internet connection
   - Verify the HuggingFace model ID is correct
   - Some models may require authentication

### View Logs

```bash
docker-compose logs -f vllm-dashboard
```

### Restart Services

```bash
docker-compose restart
```

## 📁 Project Structure

```
├── api/                 # API routes
│   ├── dashboard.py     # Dashboard API endpoints
│   └── openai_api.py    # OpenAI-compatible API
├── services/            # Business logic
│   └── model_manager.py # Model management service
├── templates/           # HTML templates
│   └── index.html       # Main dashboard
├── static/              # Static assets
│   └── app.js          # Frontend JavaScript
├── models/              # Downloaded models (created at runtime)
├── data/                # Application data (created at runtime)
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── start.sh            # Startup script
└── README.md           # This file
```

## 🎯 Recommended Models to Try

### Small Models (Good for testing)
- `microsoft/DialoGPT-small`
- `gpt2`
- `distilgpt2`

### Medium Models
- `microsoft/DialoGPT-medium`
- `gpt2-medium`

### Larger Models (Require more GPU memory)
- `microsoft/DialoGPT-large`
- `gpt2-large`
- `EleutherAI/gpt-neo-1.3B`

## 📄 License

MIT License

---

**Happy AI model management! 🤖✨**
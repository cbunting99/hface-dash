# Transformers Dashboard

A web-based dashboard for managing, running, and monitoring AI models using Hugging Face's transformers library.

## Features
- Launch and monitor models using Hugging Face transformers
- View model status and logs
- Extensible for custom model services

## Docker Instructions

To build and run the dashboard with Docker:

```powershell
git clone https://github.com/cbunting99/hface-dash.git
cd hface-dash
docker build -t transformers-dashboard .
docker run -p 8000:8000 transformers-dashboard
```

The dashboard will be available at `http://localhost:8000`.

## License
See LICENSE for details.

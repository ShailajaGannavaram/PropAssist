# PropAssist — Real Estate AI Agent

## How to Start the Project

You need 3 PowerShell windows open at the same time.

### PowerShell 1 — Start Ollama (AI Engine)
ollama serve
If you see "port already in use" — Ollama is already running, skip this.

### PowerShell 2 — Start Django Backend
cd C:\AI_Agent
venv\Scripts\activate
python manage.py runserver

### PowerShell 3 — Start React Frontend
cd C:\AI_Agent\frontend
npm start

## Open in Browser

Chatbot   — http://localhost:3000
Admin     — http://127.0.0.1:8000/admin
API       — http://127.0.0.1:8000/api/chat/

## Admin Login
Username: admin
Password: admin123

## Project Structure
C:\AI_Agent
  config       Django settings and URLs
  chat         Chat API and AI logic
  properties   Property database models
  frontend     React chat interface
  venv         Python virtual environment
  .env         API keys (never share this)

## Important Notes
- Always start Ollama and Django BEFORE opening React
- Django runs on port 8000
- React runs on port 3000
- API key is in the .env file — never upload to GitHub
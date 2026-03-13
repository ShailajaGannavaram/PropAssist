# PropAssist — AI Real Estate Agent

## Live URLs
- Chatbot: https://propertyassist.vercel.app
- Admin Panel: https://propertyassist.onrender.com/admin
- API: https://propertyassist.onrender.com/api/chat/

## Admin Login
- Username: admin
- Password: admin123

## Tech Stack
- Frontend: React.js (deployed on Vercel)
- Backend: Django + Django REST Framework (deployed on Render)
- AI: Anthropic Claude (claude-sonnet-4-6)
- Database: PostgreSQL (Render)
- Properties: 14,522 real Indian properties from Kaggle dataset

## Features
- AI chat restricted to real estate only
- Smart property search by city, area and type
- Web search for properties not in database
- Action buttons — Show More, Refine by Price, Location, Type, Schedule Visit
- Lead capture — saves customer name and phone automatically
- Streaming responses like ChatGPT
- Django admin panel for management

## Local Development

### Requirements
- Python 3.11
- Node.js
- PostgreSQL

### PowerShell 1 — Django Backend
cd C:\AI_Agent
venv\Scripts\activate
python manage.py runserver

### PowerShell 2 — React Frontend
cd C:\AI_Agent\frontend
npm start

## Open in Browser
- Chatbot: http://localhost:3000
- Admin: http://127.0.0.1:8000/admin
- API: http://127.0.0.1:8000/api/chat/

## Project Structure
C:\AI_Agent
  config/        Django settings and URLs
  chat/          Chat API, AI logic, lead capture
  properties/    Property database models
  frontend/      React chat interface
  .env           API keys (never share or upload to GitHub)





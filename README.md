# AI Hotel PMS - Hotel Management System

![React](https://img.shields.io/badge/React-19.2.0-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9.3-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green)
![Python](https://img.shields.io/badge/Python-3.11+-yellow)

## 📋 About

AI Hotel PMS is an AI-powered intelligent hotel management system. This system is designed to digitize hotel operations and improve guest experience using modern web technologies.

### Features

**Admin Panel:**

- Room management (add, edit, delete, availability status)
- Dynamic pricing management
- Maintenance request tracking
- Housekeeping task management
- Guest information management
- Reservation management

**Guest Portal (Coming Soon):**

- Room listing and filtering
- Online reservation system
- Service requests
- Feedback and complaint management

**Future Features (AI Agent):**

- Smart Concierge Assistant
- Room recommendation system
- Dynamic pricing optimization
- 24/7 customer support

---

## 🛠️ Technologies Used

### Frontend

- **React 19** - User interface library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Page routing
- **Axios** - HTTP client

### Backend

- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Pydantic** - Data validation
- **JWT** - Authentication

---

## 🚀 Setup and Run

### Prerequisites

- Docker Desktop
- Node.js (v18+)
- Python (v3.11+)
- npm or yarn

### Step 1: Start Database with Docker

```bash
# Go to Backend folder
cd Backend

# Start Docker containers
docker compose up -d

# Check if container is running
docker ps
```

**Note:** Database will run on port `localhost:5500`.

### Step 2: Backend Setup

```bash
# Stay in Backend folder
cd Backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Create Database

```bash
# Create database tables and add seed data
python app/init_db.py
```

This command:

- Creates database tables
- Creates default users

### Step 4: Run Backend Server

```bash
# Start backend server
uvicorn app.main:app --reload
```

Backend will run at http://localhost:8000.

### Step 5: Frontend Setup and Run

```bash
# Go to Frontend folder
cd Frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at http://localhost:5173.

---

## 📁 Project Structure

```
Web Project/
├── Frontend/                 # React frontend application
│   ├── src/
│   │   ├── api/             # API calls
│   │   ├── components/      # React components
│   │   │   ├── common/     # Common components
│   │   │   └── layouts    # Layout components
│   │   ├── pages/          # Page components
│   │   │   ├── admin/      # Admin pages
│   │   │   └── user/       # User pages
│   │   ├── hooks          # Custom React hooks
│   │   ├── types          # TypeScript types
│   │   └── App.tsx        # Main application
│   └── package.json
│
├── Backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── controllers    # Business logic controllers
│   │   ├── models         # Database models
│   │   ├── routes         # API routes
│   │   ├── schemas        # Pydantic schemas
│   │   ├── services       # Business logic services
│   │   ├── repositories   # Database access layer
│   │   └── utils         # Helper functions
│   └── requirements.txt
│
├── AI_Agent_Plan.md         # AI Agent planning document
├── TODO.md                  # TODO list
└── README.md
```

---

## 🔐 Default Users

When the database is initialized (by running `python app/init_db.py`), the following users are automatically created:

| Role      | Email                 | Password   |
| --------- | --------------------- | ---------- |
| Moderator | moderator@example.com | Dev@12345! |
| User      | user@example.com      | Dev@12345! |

---

## 📄 AI Agent Planning Document

The detailed planning document for AI Agent integration is available in ai_agent_documantation.

### AI Agent Summary

**Agent Name:** Multi-Agent System  
**Type:** Orchestrator with Sub-Agents  
**Purpose:** Automate hotel operations with AI

**Agents:**

1. **Guest Feedback Analyzer** - Analyzes reviews, routes issues to departments
2. **Dynamic Pricing Orchestrator** - Coordinates Event/Weather/Occupancy agents
3. **Analytics Agent** - Automatic reporting and insights



# Shipment Management System

A full-stack application for managing shipments with user authentication and real-time tracking.

## Project Structure

```
BACKEND PROJECT 2/
├── app/                    # Backend application
│   ├── __init__.py
│   ├── auth.py            # Authentication utilities
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection
│   ├── logger.py          # Logging configuration
│   ├── main.py            # FastAPI application
│   ├── middleware.py      # Custom middleware
│   ├── schemas.py         # Pydantic models
│   └── seed.py            # Database seeding
├── frontend/              # Vue.js frontend
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   ├── views/         # Vue views
│   │   ├── App.vue        # Root component
│   │   └── main.ts        # Application entry
│   └── package.json       # Frontend dependencies
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup Instructions

### Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv myvenv
   source myvenv/bin/activate  # On Windows: myvenv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

The backend will be available at uvohttp://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:5175

## Features

- User authentication with JWT tokens
- Shipment tracking and management
- Real-time status updates
- Responsive web interface
- Secure API endpoints
- Database persistence
- Logging and error handling

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for the interactive API documentation.

## Development

- Backend: FastAPI with SQLModel
- Frontend: Vue 3 with TypeScript
- Database: SQLite
- Authentication: JWT with OAuth2

## API Endpoints

### Authentication
- `POST /token` - Login
- `POST /users/` - Register

### Shipments
- `GET /shipments/` - List all shipments
- `POST /shipments/` - Create new shipment
- `GET /shipments/{id}` - Get shipment details
- `PATCH /shipments/{id}` - Update shipment
- `DELETE /shipments/{id}` - Delete shipment

## Usage

1. Register a new account
2. Login with your credentials
3. Start managing your shipments

## Development

- Backend API documentation is available at `http://localhost:8000/docs`
- Frontend development server includes hot-reload
- TypeScript type checking is enabled

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Protected routes
- CORS enabled
- Input validation 
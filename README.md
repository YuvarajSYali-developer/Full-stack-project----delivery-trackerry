# 🚢 ShipTrack Pro - Indian Shipment Management System

A comprehensive full-stack shipment management application built with FastAPI (backend) and Vue.js (frontend), specifically designed for Indian logistics and shipping operations.

## 🌟 Features

- **🔐 User Authentication & Authorization** - Secure login with role-based access
- **📦 Shipment Tracking & Management** - Complete shipment lifecycle management  
- **👥 Customer Management** - Comprehensive customer database
- **📊 Real-time Analytics & Reporting** - Business insights and performance metrics
- **🎯 Role-based Access Control** - Admin, Manager, Employee, and Customer roles
- **🇮🇳 Indian Localization** - Indian cities, customers, and business context
- **📱 Responsive Design** - Works on desktop and mobile devices

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - SQL databases in Python with type safety
- **SQLite** - Lightweight database for development
- **Uvicorn** - Lightning-fast ASGI server
- **Passlib** - Password hashing and verification

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **TypeScript** - Typed superset of JavaScript
- **Vite** - Next generation frontend tooling
- **Pinia** - State management for Vue.js
- **Vue Router** - Official router for Vue.js
- **Axios** - HTTP client for API calls

## 📁 Project Structure

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
├── working_server.py      # Main FastAPI server
├── indian_shipment.db     # SQLite database
├── start_servers.bat      # Start both servers (Windows)
└── README.md             # This file
```

## 📋 Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)

## 🚀 Quick Start (Windows)

### Option 1: Use Batch Files (Easiest)

```bash
# Start both backend and frontend servers
start_servers.bat

# OR start backend only
start_backend_only.bat
```

### Option 2: Manual Setup

#### 🐍 Backend Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd "BACKEND PROJECT 2"
```

2. **Create and activate virtual environment**
```bash
# Create virtual environment
python -m venv myvenv

# Activate virtual environment (Windows)
myvenv\Scripts\activate

# For Git Bash or Linux/Mac
source myvenv/bin/activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Start backend server**
```bash
python working_server.py
```

#### 🌐 Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install Node.js dependencies**
```bash
npm install
```

3. **Start the frontend dev server**
```bash
npm run serve
```

## 🌐 Access URLs

Once both servers are running:

- **🎨 Frontend Application**: http://localhost:5173
- **🔧 Backend API**: http://localhost:8001
- **📚 API Documentation**: http://localhost:8001/docs
- **🔍 Alternative API Docs**: http://localhost:8001/redoc

## 🔑 Login Credentials

Use these test accounts to access the system:

| Role | Username | Password | Full Name |
|------|----------|----------|-----------|
| Admin | admin | admin123 | Rahul Sharma |
| Manager | manager | manager123 | Anita Desai |
| Employee | employee | employee123 | Suresh Kumar |
| Customer | testuser | password123 | Demo User |

## 📊 Sample Data

The application comes pre-loaded with:

- **50+ Sample Shipments** - Realistic Indian shipping data
- **8 Sample Customers** - Indian companies and individuals
- **Multiple User Roles** - Admin, Manager, Employee, Customer accounts

## 🔗 API Endpoints

### Authentication
- `POST /token` - Login
- `POST /users/` - Register

### Shipments
- `GET /shipments/` - List all shipments
- `POST /shipments/` - Create new shipment
- `GET /shipments/{id}` - Get shipment details
- `PATCH /shipments/{id}` - Update shipment
- `DELETE /shipments/{id}` - Delete shipment

## 🛡️ Security Features

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Protected routes
- CORS enabled
- Input validation

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
```bash
# Kill process on port 8001 (Backend)
netstat -ano | findstr :8001
taskkill /PID <PID_NUMBER> /F

# Kill process on port 5173 (Frontend)
netstat -ano | findstr :5173
taskkill /PID <PID_NUMBER> /F
```

2. **Python virtual environment issues**
```bash
# Delete and recreate virtual environment
rmdir /s myvenv
python -m venv myvenv
myvenv\Scripts\activate
pip install -r requirements.txt
```

3. **Node.js dependency issues**
```bash
# Clear npm cache and reinstall
cd frontend
npm cache clean --force
rmdir /s node_modules
del package-lock.json
npm install
```

4. **Login not working**
- Ensure backend server is running on port 8001
- Check browser console for errors
- Verify credentials from the table above
- Try the test login page: `test_login.html`

## 🚀 Usage

1. Register a new account or use test credentials
2. Login with your credentials
3. Start managing your shipments
4. Access real-time tracking and analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Search existing [Issues](../../issues)
3. Create a new issue if needed

## 🙏 Acknowledgments

- Built with modern web technologies
- Designed for Indian logistics industry
- Responsive and user-friendly interface

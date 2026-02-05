# Task Management System

A full-stack task management application built with Flask (backend) and React (frontend), featuring JWT authentication, RESTful API, and a modern responsive UI.

## 🚀 Features

- **User Authentication**: Secure registration and login with JWT tokens
- **Task Management**: Create, read, update, and delete tasks
- **Categories**: Organize tasks with color-coded categories
- **Priority Levels**: Set task priority (low, medium, high)
- **Due Dates**: Track task deadlines
- **Filtering**: Filter tasks by status, priority, and category
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Security**: Rate limiting, security headers, and password validation

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

## 🛠️ Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   ```bash
   copy .env.example .env
   ```
   Edit `.env` and update the secret keys.

6. Initialize the database:
   ```bash
   python ../database/migrate.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env` file (already created, but verify API URL):
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   ```

## 🏃 Running the Application

### Start the Backend

```bash
cd backend
python app.py
```

The backend API will run on `http://localhost:5000`

### Start the Frontend

In a new terminal:

```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000`

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📚 Project Structure

```
task_management_system/
├── backend/
│   ├── app.py              # Application factory
│   ├── config.py           # Configuration settings
│   ├── models.py           # Database models
│   ├── auth.py             # Authentication routes
│   ├── routes.py           # Task and category routes
│   ├── requirements.txt    # Python dependencies
│   └── tests/              # Backend tests
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_tasks.py
│       ├── test_categories.py
│       └── test_integration.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js          # Main application component
│   │   ├── AuthContext.js  # Authentication context
│   │   ├── api.js          # API client
│   │   ├── Login.js        # Login component
│   │   ├── Register.js     # Registration component
│   │   ├── Dashboard.js    # Main dashboard
│   │   ├── TaskForm.js     # Task creation/editing form
│   │   └── index.css       # Global styles
│   └── package.json
└── database/
    ├── schema.sql          # Database schema
    ├── seed_data.sql       # Sample data
    └── migrate.py          # Migration script
```

## 🔑 Default Test Accounts

If you initialized the database with seed data:

- **Username**: john_doe | **Password**: password123
- **Username**: jane_smith | **Password**: password123
- **Username**: test_user | **Password**: password123

## 🌐 API Endpoints

See [API.md](API.md) for detailed API documentation.

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design details.

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- Built as a full-stack development lab project

## 🙏 Acknowledgments

- Flask documentation
- React documentation
- JWT authentication best practices

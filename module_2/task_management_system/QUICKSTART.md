# Quick Start Guide

## Get Started in 5 Minutes

### 1. Setup Backend (Terminal 1)

```powershell
cd module_2\task_management_system\backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (say 'y' for seed data)
cd ..\database
python migrate.py
cd ..\backend

# Run backend server
python app.py
```

Backend will run on http://localhost:5000

### 2. Setup Frontend (Terminal 2)

```powershell
cd module_2\task_management_system\frontend

# Install dependencies
npm install

# Run frontend
npm start
```

Frontend will open automatically on http://localhost:3000

### 3. Login with Test Account

- **Username**: john_doe
- **Password**: password123

Or create a new account via registration!

### 4. Run Tests (Optional)

Backend tests:
```powershell
cd backend
pytest
```

Frontend tests:
```powershell
cd frontend
npm test
```

## Project Structure

```
task_management_system/
├── backend/           # Flask API
├── frontend/          # React App
├── database/          # SQL schema and migrations
├── README.md         # Full documentation
├── API.md            # API reference
├── ARCHITECTURE.md   # System design
├── DEPLOYMENT.md     # Production deployment
└── REFLECTION.md     # Lab reflection
```

## Features

✅ User registration & authentication  
✅ Create, edit, delete tasks  
✅ Task categories with colors  
✅ Priority levels (low, medium, high)  
✅ Due date tracking  
✅ Filter by status, priority, category  
✅ Responsive design  
✅ Security (JWT, rate limiting, validation)  

## Common Issues

**Backend won't start:**
- Make sure virtual environment is activated
- Check if port 5000 is available

**Frontend won't start:**
- Run `npm install` first
- Check if port 3000 is available

**Can't login:**
- Make sure backend is running
- Check backend console for errors
- Verify database was initialized

## Next Steps

1. Explore the codebase
2. Read the documentation
3. Run the tests
4. Try adding new features!

Enjoy! 🚀

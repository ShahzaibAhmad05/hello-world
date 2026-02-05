# URL Shortener Service 🔗

A high-performance URL shortener service built with Python, Flask, and PostgreSQL. Features include URL shortening, click tracking, analytics, expiration support, and a comprehensive RESTful API.

## 🚀 Features

- **URL Shortening**: Convert long URLs to short, shareable codes
- **Click Tracking**: Detailed analytics with timestamps, referrers, and user agents  
- **Expiration Support**: Optional URL expiration with customizable time limits
- **RESTful API**: Clean, well-documented REST endpoints
- **Database Persistence**: PostgreSQL/SQLite with SQLAlchemy ORM
- **Input Validation**: Comprehensive URL validation and security checks
- **Analytics Dashboard**: Click statistics with daily breakdowns
- **Pagination**: Efficient listing of URLs with pagination support
- **Error Handling**: Robust error handling and meaningful error messages

## 🏗️ Architecture

### Tech Stack
- **Backend**: Python 3.8+, Flask 2.3+
- **Database**: PostgreSQL (production) / SQLite (development)  
- **ORM**: SQLAlchemy
- **Testing**: pytest, pytest-flask
- **Validation**: validators library

### Project Structure
```
url_shortener_service/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models (URL, Click)
├── routes.py           # API endpoints
├── utils.py            # Helper functions
├── requirements.txt    # Python dependencies
├── tests/              # Comprehensive test suite
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_utils_models.py
│   └── test_integration.py
└── README.md          # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- pip (Python package manager)

### Quick Start

1. **Clone and navigate to the project**
   ```bash
   cd module_3/url_shortener_service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   export FLASK_ENV=development
   export DATABASE_URL=sqlite:///url_shortener.db
   export SECRET_KEY=your-secret-key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

### Database Setup

The application will automatically create database tables on first run. For production with PostgreSQL:

```bash
export DATABASE_URL=postgresql://username:password@host:port/database_name
python app.py
```

## 📖 API Documentation

### Base URL
```
http://localhost:5000
```

### Authentication
No authentication required for this version. Consider adding API keys or OAuth for production use.

---

### Endpoints

#### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-05T10:30:00Z",
  "version": "1.0.0"
}
```

---

#### 2. API Documentation
**GET** `/docs`

Get comprehensive API documentation in JSON format.

---

#### 3. Shorten URL
**POST** `/shorten`

Create a short URL from a long URL.

**Request Body:**
```json
{
  "url": "https://www.example.com/very-long-url-path",
  "expires_in_hours": 24  // Optional: URL expiration in hours
}
```

**Response (201 Created):**
```json
{
  "message": "URL shortened successfully",
  "data": {
    "id": 1,
    "original_url": "https://www.example.com/very-long-url-path",
    "short_code": "abc123",
    "short_url": "http://localhost:5000/abc123",
    "created_at": "2026-02-05T10:30:00Z",
    "expires_at": "2026-02-06T10:30:00Z",
    "is_active": true,
    "click_count": 0
  }
}
```

**Response (200 OK - URL already exists):**
```json
{
  "message": "URL already exists",
  "data": { /* existing URL data */ }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid URL, missing URL, or validation errors
- `500 Internal Server Error`: Server-side error

---

#### 4. Redirect to Original URL
**GET** `/{short_code}`

Redirect to the original URL and track the click.

**Parameters:**
- `short_code` (path): The short code to redirect

**Response:**
- `302 Found`: Redirects to original URL
- `404 Not Found`: Short URL not found
- `410 Gone`: Short URL has expired

**Side Effects:**
- Records click with timestamp, IP address, user agent, and referrer

---

#### 5. Get URL Statistics
**GET** `/stats/{short_code}`

Retrieve detailed analytics for a short URL.

**Parameters:**
- `short_code` (path): The short code to get stats for

**Response (200 OK):**
```json
{
  "url": {
    "id": 1,
    "original_url": "https://www.example.com/page",
    "short_code": "abc123",
    "short_url": "http://localhost:5000/abc123",
    "created_at": "2026-02-05T10:30:00Z",
    "is_active": true,
    "click_count": 42
  },
  "statistics": {
    "total_clicks": 42,
    "clicks_last_30_days": 15,
    "daily_stats": [
      {"date": "2026-02-05", "clicks": 3},
      {"date": "2026-02-04", "clicks": 5}
    ],
    "top_referrers": [
      {"referrer": "https://google.com", "count": 10},
      {"referrer": "https://twitter.com", "count": 5}
    ],
    "created_at": "2026-02-05T10:30:00Z",
    "is_expired": false
  }
}
```

**Error Responses:**
- `404 Not Found`: Short URL not found

---

#### 6. List URLs
**GET** `/urls`

List all active URLs with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "urls": [
    {
      "id": 1,
      "original_url": "https://example.com",
      "short_code": "abc123",
      "short_url": "http://localhost:5000/abc123",
      "created_at": "2026-02-05T10:30:00Z",
      "click_count": 5
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

#### 7. Deactivate URL
**DELETE** `/urls/{short_code}`

Soft delete (deactivate) a short URL.

**Parameters:**
- `short_code` (path): The short code to deactivate

**Response (200 OK):**
```json
{
  "message": "URL deactivated successfully"
}
```

**Error Responses:**
- `404 Not Found`: Short URL not found

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Verbose output
pytest -v
```

### Test Coverage
- ✅ All API endpoints
- ✅ URL validation and security
- ✅ Database models and relationships
- ✅ Click tracking accuracy
- ✅ Error handling
- ✅ Integration workflows
- ✅ Performance under load

## 🔒 Security Considerations

### Current Security Features
- **URL Validation**: Comprehensive URL format validation
- **Safe URL Checking**: Blocks localhost and private IP addresses
- **Input Sanitization**: Prevents malicious URL inputs
- **SQL Injection Prevention**: SQLAlchemy ORM provides protection
- **Length Limits**: URL length restrictions

### Production Security Recommendations
- Add rate limiting to prevent abuse
- Implement API authentication (API keys, OAuth)
- Add HTTPS enforcement
- Set up monitoring and logging
- Implement CSRF protection for web interface
- Add content filtering for malicious domains

## 📊 Performance

### Optimizations
- Database indexing on short_code and click timestamps
- Efficient pagination with SQLAlchemy
- Connection pooling for database
- Base62 encoding for short URLs

### Scalability Considerations
- Add Redis caching for frequently accessed URLs
- Implement database sharding for high traffic
- Use CDN for global distribution
- Add load balancing for multiple instances

## 🚀 Deployment

### Environment Variables
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key-here
BASE_URL=https://yourdomain.com
PORT=5000
```

### Docker Deployment (Example)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Database Migration
For production deployments, consider using Flask-Migrate for database schema management.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and add tests
4. Ensure all tests pass (`pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check existing issues for solutions
- Review the API documentation at `/docs`

---

**Built with ❤️ using Python, Flask, and PostgreSQL**
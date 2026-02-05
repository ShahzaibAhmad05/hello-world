# API Documentation

Base URL: `http://localhost:5000/api`

All endpoints except `/auth/register` and `/auth/login` require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Authentication Endpoints

### Register User
**POST** `/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Validation:**
- Username: 3-50 characters
- Email: Valid email format
- Password: Minimum 6 characters

**Response:** `201 Created`
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-02-05T10:30:00"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Rate Limit:** 5 requests per hour

---

### Login
**POST** `/auth/login`

Authenticate and receive access tokens.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-02-05T10:30:00"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Rate Limit:** 10 requests per minute

---

### Get Current User
**GET** `/auth/me`

Get information about the currently authenticated user.

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2026-02-05T10:30:00"
}
```

---

### Refresh Token
**POST** `/auth/refresh`

Get a new access token using refresh token.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Task Endpoints

### Get All Tasks
**GET** `/tasks`

Retrieve all tasks for the authenticated user.

**Query Parameters:**
- `completed` (optional): Filter by completion status (`true`/`false`)
- `priority` (optional): Filter by priority (`low`, `medium`, `high`)
- `category_id` (optional): Filter by category ID

**Examples:**
```
GET /tasks
GET /tasks?completed=false
GET /tasks?priority=high
GET /tasks?category_id=3
GET /tasks?completed=false&priority=high
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Complete project proposal",
    "description": "Draft and submit Q1 proposal",
    "completed": false,
    "priority": "high",
    "due_date": "2026-02-08T00:00:00",
    "user_id": 1,
    "category_id": 1,
    "category": {
      "id": 1,
      "name": "Work",
      "color": "#3B82F6",
      "user_id": 1,
      "created_at": "2026-02-05T10:00:00"
    },
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:00:00"
  }
]
```

---

### Get Single Task
**GET** `/tasks/{id}`

Retrieve a specific task by ID.

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Complete project proposal",
  "description": "Draft and submit Q1 proposal",
  "completed": false,
  "priority": "high",
  "due_date": "2026-02-08T00:00:00",
  "user_id": 1,
  "category_id": 1,
  "category": {
    "id": 1,
    "name": "Work",
    "color": "#3B82F6"
  },
  "created_at": "2026-02-05T10:00:00",
  "updated_at": "2026-02-05T10:00:00"
}
```

**Error:** `404 Not Found` if task doesn't exist or doesn't belong to user

---

### Create Task
**POST** `/tasks`

Create a new task.

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description (optional)",
  "priority": "medium",
  "category_id": 1,
  "due_date": "2026-02-15T00:00:00"
}
```

**Required Fields:**
- `title` (string, min 1 character)

**Optional Fields:**
- `description` (string)
- `priority` (string: `low`, `medium`, `high` - default: `medium`)
- `category_id` (integer)
- `due_date` (ISO 8601 datetime string)

**Response:** `201 Created`
```json
{
  "id": 5,
  "title": "New Task",
  "description": "Task description",
  "completed": false,
  "priority": "medium",
  "due_date": "2026-02-15T00:00:00",
  "user_id": 1,
  "category_id": 1,
  "category": {
    "id": 1,
    "name": "Work",
    "color": "#3B82F6"
  },
  "created_at": "2026-02-05T11:00:00",
  "updated_at": "2026-02-05T11:00:00"
}
```

---

### Update Task
**PUT** `/tasks/{id}`

Update an existing task.

**Request Body:** (all fields optional)
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "completed": true,
  "priority": "high",
  "category_id": 2,
  "due_date": "2026-02-20T00:00:00"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Updated Title",
  "description": "Updated description",
  "completed": true,
  "priority": "high",
  "due_date": "2026-02-20T00:00:00",
  "user_id": 1,
  "category_id": 2,
  "created_at": "2026-02-05T10:00:00",
  "updated_at": "2026-02-05T11:30:00"
}
```

---

### Delete Task
**DELETE** `/tasks/{id}`

Delete a task.

**Response:** `200 OK`
```json
{
  "message": "Task deleted successfully"
}
```

---

## Category Endpoints

### Get All Categories
**GET** `/categories`

Retrieve all categories for the authenticated user.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Work",
    "color": "#3B82F6",
    "user_id": 1,
    "created_at": "2026-02-05T10:00:00"
  },
  {
    "id": 2,
    "name": "Personal",
    "color": "#10B981",
    "user_id": 1,
    "created_at": "2026-02-05T10:00:00"
  }
]
```

---

### Create Category
**POST** `/categories`

Create a new category.

**Request Body:**
```json
{
  "name": "Projects",
  "color": "#8B5CF6"
}
```

**Required Fields:**
- `name` (string)

**Optional Fields:**
- `color` (string, hex color code - default: `#3B82F6`)

**Response:** `201 Created`
```json
{
  "id": 3,
  "name": "Projects",
  "color": "#8B5CF6",
  "user_id": 1,
  "created_at": "2026-02-05T11:00:00"
}
```

---

### Update Category
**PUT** `/categories/{id}`

Update an existing category.

**Request Body:** (all fields optional)
```json
{
  "name": "Updated Name",
  "color": "#EC4899"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Updated Name",
  "color": "#EC4899",
  "user_id": 1,
  "created_at": "2026-02-05T10:00:00"
}
```

---

### Delete Category
**DELETE** `/categories/{id}`

Delete a category. Tasks associated with this category will have their `category_id` set to `NULL`.

**Response:** `200 OK`
```json
{
  "message": "Category deleted successfully"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
  "msg": "Missing Authorization Header"
}
```

### 404 Not Found
```json
{
  "error": "Task not found"
}
```

### 409 Conflict
```json
{
  "error": "Username already exists"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limits

- **Registration**: 5 requests per hour
- **Login**: 10 requests per minute
- **Other endpoints**: 200 requests per day, 50 requests per hour

---

## Authentication Flow

1. **Register** or **Login** to receive `access_token` and `refresh_token`
2. Include `access_token` in Authorization header for all subsequent requests
3. When `access_token` expires (1 hour), use `refresh_token` to get a new one
4. `refresh_token` expires after 30 days

**Example Header:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

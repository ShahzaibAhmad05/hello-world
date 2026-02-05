# System Architecture

## Overview

The Task Management System follows a **three-tier architecture** pattern, separating concerns into presentation, application, and data layers. This architecture ensures scalability, maintainability, and testability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           React Frontend (Port 3000)                  │  │
│  │  - Components (Login, Register, Dashboard, TaskForm) │  │
│  │  - State Management (AuthContext)                    │  │
│  │  - API Client (axios)                                │  │
│  │  - Routing (react-router-dom)                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              │ (JSON)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Flask Backend (Port 5000)                   │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │   Routes    │  │     Auth     │  │  Security  │ │  │
│  │  │  (tasks,    │  │   (JWT)      │  │  - CORS    │ │  │
│  │  │ categories) │  │              │  │  - Limiter │ │  │
│  │  └─────────────┘  └──────────────┘  │  - Headers │ │  │
│  │                                      └────────────┘ │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │           Business Logic Layer               │  │  │
│  │  │  - Input Validation                          │  │  │
│  │  │  - Error Handling                            │  │  │
│  │  │  - Authorization (User Isolation)            │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ SQLAlchemy ORM
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SQLite Database                          │  │
│  │                                                       │  │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────────────┐ │  │
│  │  │  Users  │  │Categories│  │       Tasks        │ │  │
│  │  │         │  │          │  │                    │ │  │
│  │  │ - id    │  │ - id     │  │ - id               │ │  │
│  │  │ - name  │  │ - name   │  │ - title            │ │  │
│  │  │ - email │  │ - color  │  │ - description      │ │  │
│  │  │ - pass  │  │ - user_id│  │ - completed        │ │  │
│  │  └─────────┘  └──────────┘  │ - priority         │ │  │
│  │                              │ - due_date         │ │  │
│  │                              │ - user_id (FK)     │ │  │
│  │                              │ - category_id (FK) │ │  │
│  │                              └────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Presentation Layer (Frontend)

**Technology:** React 18.2

**Key Components:**

- **App.js**: Main application component with routing
- **AuthContext.js**: Global authentication state management
- **Login/Register**: User authentication forms with validation
- **Dashboard**: Main task management interface
- **TaskForm**: Modal for creating/editing tasks
- **api.js**: Centralized API client with interceptors

**Design Patterns:**
- Context API for state management
- Protected routes for authentication
- Component composition
- Controlled components for forms

### 2. Application Layer (Backend)

**Technology:** Flask 3.0

**Architecture Pattern:** MVC (Model-View-Controller)

**Key Modules:**

#### Models (`models.py`)
- **User**: Authentication and user data
- **Category**: Task organization
- **Task**: Core task entity

Relationships:
- User → Tasks (1:Many, CASCADE DELETE)
- User → Categories (1:Many, CASCADE DELETE)
- Category → Tasks (1:Many, SET NULL on delete)

#### Routes (`routes.py`, `auth.py`)
- RESTful API endpoints
- Request validation
- Response formatting
- Error handling

#### Security
- **JWT**: Stateless authentication
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-Limiter**: Rate limiting
- **bcrypt**: Password hashing
- Security headers (XSS, CSRF, Clickjacking protection)

#### Configuration (`config.py`)
- Environment-based configuration
- Development, Testing, Production configs
- Secret key management

### 3. Data Layer

**Database:** SQLite (development), PostgreSQL (production-ready)

**ORM:** SQLAlchemy

**Schema Design:**

```sql
Users
  ├─ id (PK)
  ├─ username (UNIQUE, INDEX)
  ├─ email (UNIQUE, INDEX)
  ├─ password_hash
  └─ created_at

Categories
  ├─ id (PK)
  ├─ name
  ├─ color
  ├─ user_id (FK → Users.id, CASCADE)
  └─ created_at

Tasks
  ├─ id (PK)
  ├─ title
  ├─ description
  ├─ completed (INDEX)
  ├─ priority (CHECK: low|medium|high, INDEX)
  ├─ due_date (INDEX)
  ├─ user_id (FK → Users.id, CASCADE)
  ├─ category_id (FK → Categories.id, SET NULL)
  ├─ created_at
  └─ updated_at
```

**Indexing Strategy:**
- Primary keys on all tables
- Unique indexes on username, email
- Foreign key indexes for joins
- Filter indexes on completed, priority, due_date

## Data Flow

### Task Creation Flow

```
1. User fills TaskForm in React
2. Form validation (client-side)
3. POST /api/tasks with JWT token
4. Backend validates JWT → extracts user_id
5. Backend validates task data
6. ORM creates Task record
7. Database applies constraints
8. Response with created task
9. Frontend updates task list
```

### Authentication Flow

```
1. User submits login credentials
2. Backend validates username/password
3. Generate access_token (1hr) + refresh_token (30d)
4. Store tokens in localStorage
5. Include access_token in all API requests
6. On token expiry, use refresh_token
7. On logout, clear localStorage
```

## Security Architecture

### Authentication & Authorization

1. **Password Security**
   - bcrypt hashing (12 rounds)
   - Minimum 6 characters
   - Never stored in plaintext

2. **JWT Tokens**
   - Access token: 1 hour expiry
   - Refresh token: 30 days expiry
   - Signed with HS256 algorithm
   - Contains user_id claim

3. **API Protection**
   - `@jwt_required()` decorator on protected routes
   - User isolation (can only access own data)
   - Rate limiting per endpoint

### Security Headers

```python
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

## Scalability Considerations

### Current (Development)
- Single SQLite database
- In-memory rate limiting
- Synchronous request handling

### Production Recommendations

1. **Database**
   - PostgreSQL for production
   - Connection pooling
   - Read replicas for scaling reads

2. **Caching**
   - Redis for rate limiting
   - Cache frequently accessed data
   - Session storage

3. **Application Server**
   - Gunicorn with multiple workers
   - Nginx reverse proxy
   - Load balancing

4. **Frontend**
   - Static file CDN
   - Code splitting
   - Service workers for offline support

## Testing Strategy

### Unit Tests
- Models: Data validation, relationships
- Routes: API endpoints, error handling
- Auth: Registration, login, token refresh

### Integration Tests
- Complete user workflows
- Cross-feature interactions
- Database transactions

### Test Coverage
- Backend: 80%+ coverage goal
- Focus on business logic
- Edge cases and error paths

## Design Decisions

### Why JWT over Sessions?
- **Stateless**: No server-side session storage
- **Scalable**: Works across multiple servers
- **Mobile-friendly**: Easy to use in mobile apps

### Why SQLite?
- **Development**: Zero configuration
- **Testing**: Fast, in-memory option
- **Portable**: Single file database
- **Production**: Swap to PostgreSQL easily

### Why React over Vue/Angular?
- **Popularity**: Large ecosystem
- **Performance**: Virtual DOM
- **Flexibility**: Component-based architecture
- **Learning**: Widely documented

## Future Enhancements

1. **Real-time Updates**: WebSockets for live collaboration
2. **File Attachments**: Upload files to tasks
3. **Notifications**: Email/push notifications for deadlines
4. **Team Collaboration**: Share tasks with other users
5. **Analytics**: Task completion statistics
6. **Mobile App**: React Native application
7. **Export**: CSV/PDF export functionality

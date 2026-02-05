# Blog API with Nested Comments

A complete RESTful API for a blog platform with nested comments, JWT authentication, rate limiting, and comprehensive testing. Built with Node.js, Express, TypeScript, PostgreSQL, and Prisma ORM.

## 🚀 Features

### Core Functionality
- ✅ **User Authentication**: JWT-based authentication with secure password hashing (bcrypt)
- ✅ **Post Management**: Full CRUD operations for blog posts
- ✅ **Publishing Control**: Publish/unpublish posts (authors only)
- ✅ **Nested Comments**: Comment system with 1-level deep replies
- ✅ **Authorization**: Role-based access control (authors can only edit their own content)
- ✅ **Pagination**: Efficient pagination for list endpoints
- ✅ **Rate Limiting**: Protection against abuse and brute force attacks
- ✅ **Input Validation**: Comprehensive validation using express-validator
- ✅ **Error Handling**: Centralized error handling with custom error types

### Security Features
- 🔒 **Password Hashing**: Bcrypt with 12 salt rounds (OWASP-compliant)
- 🔒 **JWT Tokens**: Secure token-based authentication
- 🔒 **Input Sanitization**: SQL injection prevention via Prisma ORM
- 🔒 **Rate Limiting**: Global and endpoint-specific rate limits
- 🔒 **Environment Variables**: All secrets stored in .env files

### Code Quality
- ✅ **TypeScript**: Full type safety with strict mode
- ✅ **80%+ Test Coverage**: Comprehensive unit and integration tests
- ✅ **JSDoc Comments**: Documentation for complex functions
- ✅ **Modular Architecture**: Clean separation of concerns

## 📋 Prerequisites

- Node.js (v16 or higher)
- PostgreSQL (v12 or higher)
- npm or yarn

## 🛠️ Installation

### 1. Clone and Navigate
```bash
cd module_4/lab
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Environment Setup
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
PORT=3000
NODE_ENV=development
DATABASE_URL="postgresql://username:password@localhost:5432/blog_api_db?schema=public"
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-min-32-chars
JWT_EXPIRES_IN=7d
BCRYPT_SALT_ROUNDS=12
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### 4. Database Setup
```bash
# Generate Prisma Client
npm run prisma:generate

# Run migrations
npm run prisma:migrate

# (Optional) Seed database
npm run prisma:seed
```

## 🚦 Usage

### Development Mode
```bash
npm run dev
```
Server runs on `http://localhost:3000`

### Production Mode
```bash
# Build the project
npm run build

# Start server
npm start
```

### Testing
```bash
# Run all tests with coverage
npm test

# Run tests in watch mode
npm run test:watch

# Run only unit tests
npm run test:unit

# Run only integration tests
npm run test:integration
```

### Database Management
```bash
# Open Prisma Studio (Database GUI)
npm run prisma:studio

# Create new migration
npm run prisma:migrate

# Generate Prisma Client
npm run prisma:generate
```

## 📚 API Documentation

### Base URL
```
http://localhost:3000/api
```

### Quick Reference
Visit `http://localhost:3000/api/docs` for interactive API documentation.

---

## 🔐 Authentication Endpoints

### Register New User
**POST** `/api/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

**Response:** `201 Created`
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "name": "John Doe",
    "createdAt": "2026-02-05T10:00:00.000Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Login
**POST** `/api/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Get Profile
**GET** `/api/auth/profile`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "name": "John Doe",
    "createdAt": "2026-02-05T10:00:00.000Z",
    "updatedAt": "2026-02-05T10:00:00.000Z",
    "_count": {
      "posts": 5,
      "comments": 12
    }
  }
}
```

---

## 📝 Post Endpoints

### Get All Posts
**GET** `/api/posts?page=1&limit=10`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)

**Access:** Public (shows only published posts) / Private (shows all posts)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "My First Blog Post",
      "content": "Post content here...",
      "author": "username",
      "authorId": "uuid",
      "publishedAt": "2026-02-05T10:00:00.000Z",
      "createdAt": "2026-02-05T09:00:00.000Z",
      "updatedAt": "2026-02-05T10:00:00.000Z",
      "_count": {
        "comments": 5
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "totalPages": 3,
    "hasNext": true,
    "hasPrev": false
  }
}
```

### Get Single Post
**GET** `/api/posts/:id`

**Access:** Public (published posts) / Private (author can view unpublished)

**Response:** `200 OK`
```json
{
  "post": {
    "id": "uuid",
    "title": "My First Blog Post",
    "content": "Post content...",
    "author": "username",
    "authorId": "uuid",
    "publishedAt": "2026-02-05T10:00:00.000Z",
    "createdAt": "2026-02-05T09:00:00.000Z",
    "updatedAt": "2026-02-05T10:00:00.000Z",
    "comments": [
      {
        "id": "uuid",
        "content": "Great post!",
        "author": "commenter",
        "authorId": "uuid",
        "createdAt": "2026-02-05T11:00:00.000Z",
        "replies": [
          {
            "id": "uuid",
            "content": "Thank you!",
            "author": "username",
            "authorId": "uuid",
            "createdAt": "2026-02-05T11:30:00.000Z"
          }
        ]
      }
    ]
  }
}
```

### Create Post
**POST** `/api/posts`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "My Blog Post Title",
  "content": "This is the content of my blog post. Must be at least 10 characters.",
  "publish": false
}
```

**Validation:**
- `title`: 3-200 characters, required
- `content`: minimum 10 characters, required
- `publish`: boolean, optional (default: false)

**Response:** `201 Created`
```json
{
  "message": "Post created successfully",
  "post": {
    "id": "uuid",
    "title": "My Blog Post Title",
    "content": "This is the content...",
    "author": "username",
    "authorId": "uuid",
    "publishedAt": null,
    "createdAt": "2026-02-05T10:00:00.000Z",
    "updatedAt": "2026-02-05T10:00:00.000Z"
  }
}
```

### Update Post
**PUT** `/api/posts/:id`

**Headers:**
```
Authorization: Bearer <token>
```

**Access:** Author only

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content"
}
```

**Response:** `200 OK`

### Delete Post
**DELETE** `/api/posts/:id`

**Headers:**
```
Authorization: Bearer <token>
```

**Access:** Author only

**Response:** `200 OK`
```json
{
  "message": "Post deleted successfully"
}
```

### Publish Post
**PATCH** `/api/posts/:id/publish`

**Headers:**
```
Authorization: Bearer <token>
```

**Access:** Author only

**Response:** `200 OK`

### Unpublish Post
**PATCH** `/api/posts/:id/unpublish`

**Headers:**
```
Authorization: Bearer <token>
```

**Access:** Author only

**Response:** `200 OK`

---

## 💬 Comment Endpoints

### Add Comment to Post
**POST** `/api/posts/:postId/comments`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "content": "This is my comment on the post"
}
```

**Validation:**
- `content`: 1-2000 characters, required

**Response:** `201 Created`
```json
{
  "message": "Comment added successfully",
  "comment": {
    "id": "uuid",
    "content": "This is my comment on the post",
    "author": "username",
    "authorId": "uuid",
    "postId": "uuid",
    "parentId": null,
    "createdAt": "2026-02-05T10:00:00.000Z",
    "updatedAt": "2026-02-05T10:00:00.000Z"
  }
}
```

### Reply to Comment
**POST** `/api/comments/:commentId/replies`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "content": "This is my reply"
}
```

**Note:** Only 1 level of nesting allowed. Cannot reply to a reply.

**Response:** `201 Created`
```json
{
  "message": "Reply added successfully",
  "comment": {
    "id": "uuid",
    "content": "This is my reply",
    "author": "username",
    "authorId": "uuid",
    "postId": "uuid",
    "parentId": "parent-comment-uuid",
    "createdAt": "2026-02-05T10:30:00.000Z",
    "updatedAt": "2026-02-05T10:30:00.000Z"
  }
}
```

### Get Comment with Replies
**GET** `/api/comments/:id`

**Access:** Public

**Response:** `200 OK`
```json
{
  "comment": {
    "id": "uuid",
    "content": "Comment content",
    "author": "username",
    "authorId": "uuid",
    "postId": "uuid",
    "parentId": null,
    "createdAt": "2026-02-05T10:00:00.000Z",
    "updatedAt": "2026-02-05T10:00:00.000Z",
    "replies": [
      {
        "id": "uuid",
        "content": "Reply content",
        "author": "other-user",
        "authorId": "uuid",
        "createdAt": "2026-02-05T10:30:00.000Z",
        "updatedAt": "2026-02-05T10:30:00.000Z"
      }
    ]
  }
}
```

### Delete Comment
**DELETE** `/api/comments/:id`

**Headers:**
```
Authorization: Bearer <token>
```

**Access:** Author only

**Note:** Deleting a comment will also delete all its replies (cascade).

**Response:** `200 OK`
```json
{
  "message": "Comment deleted successfully"
}
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "error": "ValidationError",
  "message": "Title must be between 3 and 200 characters"
}
```

### 401 Unauthorized
```json
{
  "error": "UnauthorizedError",
  "message": "No token provided"
}
```

### 403 Forbidden
```json
{
  "error": "ForbiddenError",
  "message": "You can only edit your own posts"
}
```

### 404 Not Found
```json
{
  "error": "NotFoundError",
  "message": "Post not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "TooManyRequests",
  "message": "Too many requests from this IP, please try again later"
}
```

---

## 🏗️ Project Structure

```
lab/
├── prisma/
│   └── schema.prisma           # Database schema
├── src/
│   ├── controllers/            # Request handlers
│   │   ├── auth.controller.ts
│   │   ├── post.controller.ts
│   │   └── comment.controller.ts
│   ├── middleware/             # Custom middleware
│   │   ├── auth.ts
│   │   ├── errorHandler.ts
│   │   ├── rateLimiter.ts
│   │   └── validator.ts
│   ├── routes/                 # API routes
│   │   ├── auth.routes.ts
│   │   ├── post.routes.ts
│   │   └── comment.routes.ts
│   ├── services/               # Business logic
│   │   └── jwt.service.ts
│   ├── utils/                  # Utility functions
│   │   ├── password.ts
│   │   └── pagination.ts
│   ├── validators/             # Input validation
│   │   ├── auth.validator.ts
│   │   ├── post.validator.ts
│   │   └── comment.validator.ts
│   ├── lib/                    # External libraries config
│   │   └── prisma.ts
│   ├── types/                  # TypeScript types
│   │   └── express.d.ts
│   ├── app.ts                  # Express app setup
│   ├── server.ts               # Server entry point
│   └── **/*.test.ts            # Test files
├── .env.example                # Environment template
├── .gitignore
├── jest.config.js              # Jest configuration
├── package.json
├── tsconfig.json               # TypeScript config
└── README.md
```

## 🧪 Testing

### Test Coverage
The project maintains 80%+ code coverage with:
- **Unit Tests**: Password utils, JWT service, pagination
- **Integration Tests**: Auth routes, post routes, comment routes
- **Authorization Tests**: Permission checks, edge cases
- **Full Journey Tests**: Complete user workflows

### Running Tests
```bash
# All tests with coverage
npm test

# Watch mode for development
npm run test:watch

# Unit tests only
npm run test:unit

# Integration tests only
npm run test:integration
```

### Test Files
- `*.unit.test.ts` - Unit tests for isolated functions
- `*.integration.test.ts` - API endpoint integration tests

## 🔒 Security Best Practices

### Authentication & Authorization
- JWT tokens with configurable expiration
- Bcrypt password hashing with 12 salt rounds (OWASP-compliant)
- Token verification on protected routes
- Role-based access control (users can only modify their own content)

### Input Validation
- Comprehensive validation using express-validator
- Email format validation
- Password strength requirements
- Content length restrictions
- SQL injection prevention via Prisma ORM

### Rate Limiting
- Global rate limit: 100 requests per 15 minutes
- Authentication endpoints: 5 requests per 15 minutes
- Prevents brute force attacks

### Environment Variables
- All secrets in `.env` file (never committed)
- Example file provided (`.env.example`)
- No hardcoded credentials

## 🚀 Deployment Considerations

### Environment Variables
Ensure all environment variables are properly set:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Strong secret key (minimum 32 characters)
- `NODE_ENV`: Set to `production`
- `PORT`: Server port

### Database
- Run migrations: `npm run prisma:migrate`
- Generate Prisma Client: `npm run prisma:generate`

### Build
```bash
npm run build
npm start
```

## 📖 Example Usage Flow

### 1. Register and Login
```bash
# Register
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "author@example.com",
    "username": "author",
    "password": "Author@1234",
    "name": "Blog Author"
  }'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "author@example.com",
    "password": "Author@1234"
  }'
```

### 2. Create and Publish Post
```bash
# Create draft post
curl -X POST http://localhost:3000/api/posts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "content": "This is the content of my first blog post.",
    "publish": false
  }'

# Publish post
curl -X PATCH http://localhost:3000/api/posts/<post-id>/publish \
  -H "Authorization: Bearer <token>"
```

### 3. Add Comments
```bash
# Add comment
curl -X POST http://localhost:3000/api/posts/<post-id>/comments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great post!"
  }'

# Reply to comment
curl -X POST http://localhost:3000/api/comments/<comment-id>/replies \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Thank you!"
  }'
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
# Verify DATABASE_URL in .env
# Test connection:
npm run prisma:studio
```

### Migration Errors
```bash
# Reset database (WARNING: deletes all data)
npx prisma migrate reset

# Re-run migrations
npm run prisma:migrate
```

### Port Already in Use
```powershell
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Test Failures
```bash
# Ensure database is clean
# Run tests sequentially
npm test -- --runInBand
```

## 📄 License

ISC

## 👤 Author

Your Name

---

**Built with ❤️ using TypeScript, Express, Prisma, and PostgreSQL**

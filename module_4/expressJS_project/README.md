# Express.js Authentication API

A comprehensive Express.js REST API with TypeScript, PostgreSQL, Prisma ORM, and JWT authentication.

## Features

- ✅ **TypeScript**: Full type safety and modern JavaScript features
- ✅ **Express.js**: Fast, minimalist web framework
- ✅ **PostgreSQL**: Robust relational database
- ✅ **Prisma ORM**: Modern database toolkit with type-safe queries
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **Bcrypt**: Password hashing with OWASP-compliant security
- ✅ **Input Validation**: Using express-validator
- ✅ **Comprehensive Tests**: Unit and integration tests with Jest
- ✅ **Error Handling**: Centralized error handling middleware
- ✅ **CORS**: Cross-origin resource sharing enabled
- ✅ **Environment Variables**: Configuration via .env files

## Prerequisites

- Node.js (v16 or higher)
- PostgreSQL (v12 or higher)
- npm or yarn

## Installation

1. **Clone the repository**
   ```bash
   cd module_4/expressJS_project
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   PORT=3000
   NODE_ENV=development
   DATABASE_URL="postgresql://username:password@localhost:5432/express_auth_db?schema=public"
   JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
   JWT_EXPIRES_IN=7d
   BCRYPT_SALT_ROUNDS=12
   ```

4. **Set up the database**
   ```bash
   # Generate Prisma Client
   npm run prisma:generate
   
   # Run database migrations
   npm run prisma:migrate
   ```

## Usage

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
# Build the project
npm run build

# Start the server
npm start
```

### Database Management
```bash
# Open Prisma Studio (Database GUI)
npm run prisma:studio

# Create a new migration
npm run prisma:migrate

# Generate Prisma Client
npm run prisma:generate
```

## Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm test -- --coverage
```

## API Endpoints

### Authentication

#### Register New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePass123",
  "firstName": "John",
  "lastName": "Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Get Current User Profile
```http
GET /api/auth/profile
Authorization: Bearer <token>
```

### Users

#### Get All Users
```http
GET /api/users
Authorization: Bearer <token>
```

#### Get User by ID
```http
GET /api/users/:id
Authorization: Bearer <token>
```

### Health Check
```http
GET /health
```

## Project Structure

```
expressJS_project/
├── prisma/
│   └── schema.prisma          # Prisma schema
├── src/
│   ├── controllers/           # Request handlers
│   │   ├── auth.controller.ts
│   │   └── user.controller.ts
│   ├── middleware/            # Custom middleware
│   │   ├── auth.ts
│   │   ├── errorHandler.ts
│   │   └── validator.ts
│   ├── routes/                # API routes
│   │   ├── auth.routes.ts
│   │   └── user.routes.ts
│   ├── services/              # Business logic
│   │   └── jwt.service.ts
│   ├── utils/                 # Utility functions
│   │   └── password.ts
│   ├── lib/                   # External libraries config
│   │   └── prisma.ts
│   ├── types/                 # TypeScript types
│   │   └── express.d.ts
│   ├── app.ts                 # Express app setup
│   ├── server.ts              # Server entry point
│   └── *.test.ts              # Test files
├── .env.example               # Environment variables template
├── .gitignore
├── jest.config.js             # Jest configuration
├── package.json
├── tsconfig.json              # TypeScript configuration
└── README.md
```

## Security Features

### Password Security
- **Bcrypt hashing** with 12 salt rounds (OWASP-compliant)
- Passwords must contain:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number

### JWT Security
- Tokens expire after 7 days (configurable)
- Secure token verification
- Token-based authentication for protected routes

### Input Validation
- Email format validation
- Username validation (3-30 alphanumeric characters)
- Password strength requirements
- SQL injection prevention via Prisma

### Error Handling
- Custom error classes
- Centralized error handler
- No sensitive information in error responses
- Proper HTTP status codes

## Code Quality

### TypeScript Strict Mode
- `strict: true` for maximum type safety
- `noUnusedLocals` and `noUnusedParameters` enabled
- `noImplicitReturns` for consistent function returns

### Testing
- Minimum 80% code coverage requirement
- Unit tests for utilities and services
- Integration tests for API endpoints
- Comprehensive test scenarios

## Development Practices

Following PEP8-equivalent practices for TypeScript:
- Clean, descriptive naming conventions
- JSDoc documentation for complex functions
- Modular, functional components
- Input sanitization and validation
- Environment variables for secrets
- Comprehensive error handling

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Verify DATABASE_URL in .env
- Check database credentials

### Migration Errors
```bash
# Reset database (WARNING: deletes all data)
npx prisma migrate reset

# Re-run migrations
npm run prisma:migrate
```

### Port Already in Use
Change the PORT in .env file or kill the process using the port:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill
```

## License

ISC

## Author

Your Name

---

**Note**: This project follows OWASP security best practices and maintains strict typing for production-ready code quality.

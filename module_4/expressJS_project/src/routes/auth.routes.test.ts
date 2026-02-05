import request from 'supertest';
import app from '../app';
import prisma from '../lib/prisma';
import { hashPassword } from '../utils/password';

describe('Auth Routes', () => {
  // Clean up database before each test
  beforeEach(async () => {
    await prisma.user.deleteMany({});
  });

  // Clean up database after all tests
  afterAll(async () => {
    await prisma.user.deleteMany({});
    await prisma.$disconnect();
  });

  describe('POST /api/auth/register', () => {
    const validUserData = {
      email: 'test@example.com',
      username: 'testuser',
      password: 'Test@1234',
      firstName: 'Test',
      lastName: 'User',
    };

    it('should register a new user successfully', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send(validUserData)
        .expect(201);

      expect(response.body).toHaveProperty('message', 'User registered successfully');
      expect(response.body).toHaveProperty('user');
      expect(response.body).toHaveProperty('token');
      expect(response.body.user.email).toBe(validUserData.email);
      expect(response.body.user.username).toBe(validUserData.username);
      expect(response.body.user).not.toHaveProperty('password');
    });

    it('should reject registration with duplicate email', async () => {
      await request(app).post('/api/auth/register').send(validUserData);

      const response = await request(app)
        .post('/api/auth/register')
        .send({ ...validUserData, username: 'different' })
        .expect(400);

      expect(response.body).toHaveProperty('error');
      expect(response.body.message).toContain('Email already registered');
    });

    it('should reject registration with duplicate username', async () => {
      await request(app).post('/api/auth/register').send(validUserData);

      const response = await request(app)
        .post('/api/auth/register')
        .send({ ...validUserData, email: 'different@example.com' })
        .expect(400);

      expect(response.body).toHaveProperty('error');
      expect(response.body.message).toContain('Username already taken');
    });

    it('should reject registration with invalid email', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({ ...validUserData, email: 'invalid-email' })
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject registration with weak password', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({ ...validUserData, password: 'weak' })
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject registration with short username', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({ ...validUserData, username: 'ab' })
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });
  });

  describe('POST /api/auth/login', () => {
    const userData = {
      email: 'login@example.com',
      username: 'loginuser',
      password: 'Login@1234',
    };

    beforeEach(async () => {
      // Create a test user
      const hashedPassword = await hashPassword(userData.password);
      await prisma.user.create({
        data: {
          email: userData.email,
          username: userData.username,
          password: hashedPassword,
        },
      });
    });

    it('should login successfully with valid credentials', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: userData.email,
          password: userData.password,
        })
        .expect(200);

      expect(response.body).toHaveProperty('message', 'Login successful');
      expect(response.body).toHaveProperty('user');
      expect(response.body).toHaveProperty('token');
      expect(response.body.user.email).toBe(userData.email);
      expect(response.body.user).not.toHaveProperty('password');
    });

    it('should reject login with invalid email', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'wrong@example.com',
          password: userData.password,
        })
        .expect(401);

      expect(response.body).toHaveProperty('error');
      expect(response.body.message).toContain('Invalid credentials');
    });

    it('should reject login with invalid password', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: userData.email,
          password: 'WrongPassword123',
        })
        .expect(401);

      expect(response.body).toHaveProperty('error');
      expect(response.body.message).toContain('Invalid credentials');
    });

    it('should reject login for inactive user', async () => {
      // Deactivate user
      await prisma.user.update({
        where: { email: userData.email },
        data: { isActive: false },
      });

      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: userData.email,
          password: userData.password,
        })
        .expect(401);

      expect(response.body).toHaveProperty('error');
    });
  });

  describe('GET /api/auth/profile', () => {
    let authToken: string;
    const userData = {
      email: 'profile@example.com',
      username: 'profileuser',
      password: 'Profile@1234',
    };

    beforeEach(async () => {
      // Register and get token
      const response = await request(app)
        .post('/api/auth/register')
        .send(userData);

      authToken = response.body.token;
    });

    it('should get user profile with valid token', async () => {
      const response = await request(app)
        .get('/api/auth/profile')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toHaveProperty('user');
      expect(response.body.user.email).toBe(userData.email);
      expect(response.body.user).not.toHaveProperty('password');
    });

    it('should reject request without token', async () => {
      const response = await request(app)
        .get('/api/auth/profile')
        .expect(401);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject request with invalid token', async () => {
      const response = await request(app)
        .get('/api/auth/profile')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);

      expect(response.body).toHaveProperty('error');
    });
  });
});

import request from 'supertest';
import app from '../app';
import prisma from '../lib/prisma';
import { hashPassword } from '../utils/password';

describe('Auth Routes - Integration Tests', () => {
  beforeEach(async () => {
    await prisma.user.deleteMany({});
  });

  afterAll(async () => {
    await prisma.user.deleteMany({});
    await prisma.$disconnect();
  });

  describe('POST /api/auth/register', () => {
    const validUserData = {
      email: 'test@example.com',
      username: 'testuser',
      password: 'Test@1234',
      name: 'Test User',
    };

    it('should register new user successfully', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send(validUserData)
        .expect(201);

      expect(response.body).toHaveProperty('message');
      expect(response.body).toHaveProperty('user');
      expect(response.body).toHaveProperty('token');
      expect(response.body.user.email).toBe(validUserData.email);
      expect(response.body.user).not.toHaveProperty('password');
    });

    it('should reject duplicate email', async () => {
      await request(app).post('/api/auth/register').send(validUserData);

      const response = await request(app)
        .post('/api/auth/register')
        .send({ ...validUserData, username: 'different' })
        .expect(400);

      expect(response.body.message).toContain('Email already registered');
    });

    it('should reject duplicate username', async () => {
      await request(app).post('/api/auth/register').send(validUserData);

      const response = await request(app)
        .post('/api/auth/register')
        .send({ ...validUserData, email: 'different@example.com' })
        .expect(400);

      expect(response.body.message).toContain('Username already taken');
    });

    it('should reject invalid email', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({ ...validUserData, email: 'invalid-email' })
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject weak password', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({ ...validUserData, password: 'weak' })
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

      expect(response.body).toHaveProperty('token');
      expect(response.body.user.email).toBe(userData.email);
    });

    it('should reject invalid email', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'wrong@example.com',
          password: userData.password,
        })
        .expect(401);

      expect(response.body.message).toContain('Invalid credentials');
    });

    it('should reject invalid password', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: userData.email,
          password: 'WrongPassword123',
        })
        .expect(401);

      expect(response.body.message).toContain('Invalid credentials');
    });
  });

  describe('GET /api/auth/profile', () => {
    let authToken: string;

    beforeEach(async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'profile@example.com',
          username: 'profileuser',
          password: 'Profile@1234',
        });

      authToken = response.body.token;
    });

    it('should get user profile with valid token', async () => {
      const response = await request(app)
        .get('/api/auth/profile')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toHaveProperty('user');
      expect(response.body.user.email).toBe('profile@example.com');
    });

    it('should reject request without token', async () => {
      await request(app)
        .get('/api/auth/profile')
        .expect(401);
    });

    it('should reject request with invalid token', async () => {
      await request(app)
        .get('/api/auth/profile')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);
    });
  });
});

import request from 'supertest';
import app from '../app';
import prisma from '../lib/prisma';
import { hashPassword } from '../utils/password';

describe('User Routes', () => {
  let authToken: string;
  let testUserId: string;

  beforeAll(async () => {
    // Clean database
    await prisma.user.deleteMany({});

    // Create test user and get auth token
    const password = await hashPassword('Test@1234');
    const user = await prisma.user.create({
      data: {
        email: 'testuser@example.com',
        username: 'testuser',
        password,
      },
    });
    testUserId = user.id;

    // Login to get token
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'testuser@example.com',
        password: 'Test@1234',
      });

    authToken = response.body.token;

    // Create additional test users
    await prisma.user.create({
      data: {
        email: 'user2@example.com',
        username: 'user2',
        password,
        firstName: 'John',
        lastName: 'Doe',
      },
    });
  });

  afterAll(async () => {
    await prisma.user.deleteMany({});
    await prisma.$disconnect();
  });

  describe('GET /api/users', () => {
    it('should get all users with valid auth token', async () => {
      const response = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toHaveProperty('count');
      expect(response.body).toHaveProperty('users');
      expect(Array.isArray(response.body.users)).toBe(true);
      expect(response.body.users.length).toBeGreaterThanOrEqual(2);
      expect(response.body.users[0]).not.toHaveProperty('password');
    });

    it('should reject request without auth token', async () => {
      const response = await request(app)
        .get('/api/users')
        .expect(401);

      expect(response.body).toHaveProperty('error');
    });
  });

  describe('GET /api/users/:id', () => {
    it('should get user by ID with valid auth token', async () => {
      const response = await request(app)
        .get(`/api/users/${testUserId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toHaveProperty('user');
      expect(response.body.user.id).toBe(testUserId);
      expect(response.body.user).not.toHaveProperty('password');
    });

    it('should return 404 for non-existent user ID', async () => {
      const fakeId = '00000000-0000-0000-0000-000000000000';
      const response = await request(app)
        .get(`/api/users/${fakeId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404);

      expect(response.body).toHaveProperty('error');
      expect(response.body.message).toContain('not found');
    });

    it('should reject request without auth token', async () => {
      const response = await request(app)
        .get(`/api/users/${testUserId}`)
        .expect(401);

      expect(response.body).toHaveProperty('error');
    });
  });
});

import request from 'supertest';
import app from '../app';
import prisma from '../lib/prisma';

describe('App Integration Tests', () => {
  beforeAll(async () => {
    await prisma.user.deleteMany({});
  });

  afterAll(async () => {
    await prisma.user.deleteMany({});
    await prisma.$disconnect();
  });

  describe('Health Check', () => {
    it('should return 200 for health endpoint', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body).toHaveProperty('status', 'OK');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('uptime');
    });
  });

  describe('404 Handler', () => {
    it('should return 404 for non-existent routes', async () => {
      const response = await request(app)
        .get('/non-existent-route')
        .expect(404);

      expect(response.body).toHaveProperty('error', 'Not Found');
    });
  });

  describe('Full User Journey', () => {
    it('should complete full registration, login, and profile access flow', async () => {
      const userData = {
        email: 'journey@example.com',
        username: 'journeyuser',
        password: 'Journey@1234',
        firstName: 'Journey',
        lastName: 'User',
      };

      // 1. Register
      const registerResponse = await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(201);

      expect(registerResponse.body).toHaveProperty('token');
      const token = registerResponse.body.token;

      // 2. Get profile with token from registration
      const profileResponse = await request(app)
        .get('/api/auth/profile')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);

      expect(profileResponse.body.user.email).toBe(userData.email);

      // 3. Login
      const loginResponse = await request(app)
        .post('/api/auth/login')
        .send({
          email: userData.email,
          password: userData.password,
        })
        .expect(200);

      expect(loginResponse.body).toHaveProperty('token');
      const newToken = loginResponse.body.token;

      // 4. Access protected route with new token
      const usersResponse = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${newToken}`)
        .expect(200);

      expect(usersResponse.body.users).toBeDefined();
      expect(usersResponse.body.users.length).toBeGreaterThan(0);

      // 5. Get specific user
      const userId = loginResponse.body.user.id;
      const userResponse = await request(app)
        .get(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${newToken}`)
        .expect(200);

      expect(userResponse.body.user.id).toBe(userId);
    });
  });
});

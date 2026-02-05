import request from 'supertest';
import app from '../app';
import prisma from '../lib/prisma';

describe('Post Routes - Integration Tests', () => {
  let authToken: string;
  let userId: string;
  let postId: string;

  beforeAll(async () => {
    await prisma.comment.deleteMany({});
    await prisma.post.deleteMany({});
    await prisma.user.deleteMany({});

    const response = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'postauthor@example.com',
        username: 'postauthor',
        password: 'Test@1234',
      });

    authToken = response.body.token;
    userId = response.body.user.id;
  });

  afterAll(async () => {
    await prisma.comment.deleteMany({});
    await prisma.post.deleteMany({});
    await prisma.user.deleteMany({});
    await prisma.$disconnect();
  });

  describe('POST /api/posts', () => {
    it('should create new post', async () => {
      const response = await request(app)
        .post('/api/posts')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          title: 'Test Post',
          content: 'This is test content',
          publish: false,
        })
        .expect(201);

      expect(response.body.post).toHaveProperty('id');
      expect(response.body.post.title).toBe('Test Post');
      expect(response.body.post.publishedAt).toBeNull();
      postId = response.body.post.id;
    });

    it('should create and publish post', async () => {
      const response = await request(app)
        .post('/api/posts')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          title: 'Published Post',
          content: 'This will be published',
          publish: true,
        })
        .expect(201);

      expect(response.body.post.publishedAt).not.toBeNull();
    });

    it('should reject unauthenticated request', async () => {
      await request(app)
        .post('/api/posts')
        .send({
          title: 'Test',
          content: 'Content',
        })
        .expect(401);
    });

    it('should reject invalid data', async () => {
      await request(app)
        .post('/api/posts')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          title: 'AB', // Too short
          content: 'Short',
        })
        .expect(400);
    });
  });

  describe('GET /api/posts', () => {
    it('should get all posts with pagination', async () => {
      const response = await request(app)
        .get('/api/posts?page=1&limit=10')
        .expect(200);

      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('pagination');
      expect(Array.isArray(response.body.data)).toBe(true);
    });
  });

  describe('GET /api/posts/:id', () => {
    it('should get single post', async () => {
      const response = await request(app)
        .get(`/api/posts/${postId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.post.id).toBe(postId);
      expect(response.body.post).toHaveProperty('comments');
    });

    it('should return 404 for non-existent post', async () => {
      await request(app)
        .get('/api/posts/00000000-0000-0000-0000-000000000000')
        .expect(404);
    });
  });

  describe('PUT /api/posts/:id', () => {
    it('should update own post', async () => {
      const response = await request(app)
        .put(`/api/posts/${postId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          title: 'Updated Title',
          content: 'Updated content',
        })
        .expect(200);

      expect(response.body.post.title).toBe('Updated Title');
    });

    it('should reject unauthorized update', async () => {
      const otherUserResponse = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'other@example.com',
          username: 'otheruser',
          password: 'Test@1234',
        });

      await request(app)
        .put(`/api/posts/${postId}`)
        .set('Authorization', `Bearer ${otherUserResponse.body.token}`)
        .send({
          title: 'Hacked',
        })
        .expect(403);
    });
  });

  describe('PATCH /api/posts/:id/publish', () => {
    it('should publish post', async () => {
      const response = await request(app)
        .patch(`/api/posts/${postId}/publish`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.post.publishedAt).not.toBeNull();
    });

    it('should reject already published post', async () => {
      await request(app)
        .patch(`/api/posts/${postId}/publish`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(400);
    });
  });

  describe('PATCH /api/posts/:id/unpublish', () => {
    it('should unpublish post', async () => {
      const response = await request(app)
        .patch(`/api/posts/${postId}/unpublish`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.post.publishedAt).toBeNull();
    });
  });

  describe('DELETE /api/posts/:id', () => {
    it('should delete own post', async () => {
      await request(app)
        .delete(`/api/posts/${postId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      // Verify deleted
      await request(app)
        .get(`/api/posts/${postId}`)
        .expect(404);
    });
  });
});

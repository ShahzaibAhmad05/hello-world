import request from 'supertest';
import app from '../app';
import prisma from '../lib/prisma';

describe('Comment Routes - Integration Tests', () => {
  let authToken: string;
  let postId: string;
  let commentId: string;

  beforeAll(async () => {
    await prisma.comment.deleteMany({});
    await prisma.post.deleteMany({});
    await prisma.user.deleteMany({});

    const userResponse = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'commenter@example.com',
        username: 'commenter',
        password: 'Test@1234',
      });

    authToken = userResponse.body.token;

    const postResponse = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: 'Post for Comments',
        content: 'Content here',
        publish: true,
      });

    postId = postResponse.body.post.id;
  });

  afterAll(async () => {
    await prisma.comment.deleteMany({});
    await prisma.post.deleteMany({});
    await prisma.user.deleteMany({});
    await prisma.$disconnect();
  });

  describe('POST /api/posts/:postId/comments', () => {
    it('should add comment to post', async () => {
      const response = await request(app)
        .post(`/api/posts/${postId}/comments`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'This is a test comment',
        })
        .expect(201);

      expect(response.body.comment).toHaveProperty('id');
      expect(response.body.comment.content).toBe('This is a test comment');
      expect(response.body.comment.parentId).toBeNull();
      commentId = response.body.comment.id;
    });

    it('should reject unauthenticated comment', async () => {
      await request(app)
        .post(`/api/posts/${postId}/comments`)
        .send({
          content: 'Anonymous comment',
        })
        .expect(401);
    });

    it('should reject comment on non-existent post', async () => {
      await request(app)
        .post('/api/posts/00000000-0000-0000-0000-000000000000/comments')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'Comment',
        })
        .expect(404);
    });

    it('should reject empty content', async () => {
      await request(app)
        .post(`/api/posts/${postId}/comments`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: '',
        })
        .expect(400);
    });
  });

  describe('POST /api/comments/:commentId/replies', () => {
    it('should add reply to comment', async () => {
      const response = await request(app)
        .post(`/api/comments/${commentId}/replies`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'This is a reply',
        })
        .expect(201);

      expect(response.body.comment.parentId).toBe(commentId);
      expect(response.body.comment.content).toBe('This is a reply');
    });

    it('should reject reply to non-existent comment', async () => {
      await request(app)
        .post('/api/comments/00000000-0000-0000-0000-000000000000/replies')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'Reply',
        })
        .expect(404);
    });

    it('should reject reply to reply (> 1 level deep)', async () => {
      // First get a reply ID
      const replyResponse = await request(app)
        .post(`/api/comments/${commentId}/replies`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'First level reply',
        });

      const replyId = replyResponse.body.comment.id;

      // Try to reply to the reply
      await request(app)
        .post(`/api/comments/${replyId}/replies`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'Second level reply',
        })
        .expect(400);
    });
  });

  describe('GET /api/comments/:id', () => {
    it('should get comment with replies', async () => {
      const response = await request(app)
        .get(`/api/comments/${commentId}`)
        .expect(200);

      expect(response.body.comment.id).toBe(commentId);
      expect(response.body.comment).toHaveProperty('replies');
      expect(Array.isArray(response.body.comment.replies)).toBe(true);
    });

    it('should return 404 for non-existent comment', async () => {
      await request(app)
        .get('/api/comments/00000000-0000-0000-0000-000000000000')
        .expect(404);
    });
  });

  describe('DELETE /api/comments/:id', () => {
    let deleteCommentId: string;

    beforeEach(async () => {
      const response = await request(app)
        .post(`/api/posts/${postId}/comments`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'Comment to delete',
        });

      deleteCommentId = response.body.comment.id;
    });

    it('should delete own comment', async () => {
      await request(app)
        .delete(`/api/comments/${deleteCommentId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      // Verify deleted
      await request(app)
        .get(`/api/comments/${deleteCommentId}`)
        .expect(404);
    });

    it('should reject unauthorized deletion', async () => {
      const otherUserResponse = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'other2@example.com',
          username: 'other2user',
          password: 'Test@1234',
        });

      await request(app)
        .delete(`/api/comments/${deleteCommentId}`)
        .set('Authorization', `Bearer ${otherUserResponse.body.token}`)
        .expect(403);
    });
  });
});

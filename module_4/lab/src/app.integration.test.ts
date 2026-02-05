import request from 'supertest';
import app from '../app';
import prisma from '../lib/prisma';

describe('Full Blog API - Integration Tests', () => {
  beforeAll(async () => {
    await prisma.comment.deleteMany({});
    await prisma.post.deleteMany({});
    await prisma.user.deleteMany({});
  });

  afterAll(async () => {
    await prisma.comment.deleteMany({});
    await prisma.post.deleteMany({});
    await prisma.user.deleteMany({});
    await prisma.$disconnect();
  });

  describe('Complete User Journey', () => {
    it('should complete full blog workflow', async () => {
      // 1. Register author
      const authorResponse = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'author@example.com',
          username: 'author',
          password: 'Author@1234',
          name: 'Blog Author',
        })
        .expect(201);

      const authorToken = authorResponse.body.token;
      expect(authorToken).toBeDefined();

      // 2. Create draft post
      const postResponse = await request(app)
        .post('/api/posts')
        .set('Authorization', `Bearer ${authorToken}`)
        .send({
          title: 'My First Blog Post',
          content: 'This is the content of my first blog post. It contains valuable information.',
          publish: false,
        })
        .expect(201);

      const postId = postResponse.body.post.id;
      expect(postResponse.body.post.publishedAt).toBeNull();

      // 3. Update post
      await request(app)
        .put(`/api/posts/${postId}`)
        .set('Authorization', `Bearer ${authorToken}`)
        .send({
          title: 'My First Blog Post (Updated)',
          content: 'This is the updated content.',
        })
        .expect(200);

      // 4. Publish post
      await request(app)
        .patch(`/api/posts/${postId}/publish`)
        .set('Authorization', `Bearer ${authorToken}`)
        .expect(200);

      // 5. Register commenter
      const commenterResponse = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'commenter@example.com',
          username: 'commenter',
          password: 'Commenter@1234',
        })
        .expect(201);

      const commenterToken = commenterResponse.body.token;

      // 6. Add comment to post
      const commentResponse = await request(app)
        .post(`/api/posts/${postId}/comments`)
        .set('Authorization', `Bearer ${commenterToken}`)
        .send({
          content: 'Great post! Very informative.',
        })
        .expect(201);

      const commentId = commentResponse.body.comment.id;

      // 7. Reply to comment
      await request(app)
        .post(`/api/comments/${commentId}/replies`)
        .set('Authorization', `Bearer ${authorToken}`)
        .send({
          content: 'Thank you for reading!',
        })
        .expect(201);

      // 8. Get post with comments
      const fullPostResponse = await request(app)
        .get(`/api/posts/${postId}`)
        .expect(200);

      expect(fullPostResponse.body.post.comments).toBeDefined();
      expect(fullPostResponse.body.post.comments.length).toBeGreaterThan(0);
      expect(fullPostResponse.body.post.comments[0].replies).toBeDefined();

      // 9. Get all posts (public access)
      const allPostsResponse = await request(app)
        .get('/api/posts')
        .expect(200);

      expect(allPostsResponse.body.data.length).toBeGreaterThan(0);

      // 10. Delete comment
      await request(app)
        .delete(`/api/comments/${commentId}`)
        .set('Authorization', `Bearer ${commenterToken}`)
        .expect(200);

      // 11. Unpublish post
      await request(app)
        .patch(`/api/posts/${postId}/unpublish`)
        .set('Authorization', `Bearer ${authorToken}`)
        .expect(200);

      // 12. Verify unpublished post not visible publicly
      const publicPostsResponse = await request(app)
        .get('/api/posts')
        .expect(200);

      const unpublishedPost = publicPostsResponse.body.data.find(
        (p: any) => p.id === postId
      );
      expect(unpublishedPost).toBeUndefined();
    });
  });

  describe('Authorization Edge Cases', () => {
    it('should prevent user from editing another user\'s post', async () => {
      const user1Response = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'user1@example.com',
          username: 'user1',
          password: 'User1@1234',
        });

      const user2Response = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'user2@example.com',
          username: 'user2',
          password: 'User2@1234',
        });

      const postResponse = await request(app)
        .post('/api/posts')
        .set('Authorization', `Bearer ${user1Response.body.token}`)
        .send({
          title: 'User 1 Post',
          content: 'Content by user 1',
        });

      await request(app)
        .put(`/api/posts/${postResponse.body.post.id}`)
        .set('Authorization', `Bearer ${user2Response.body.token}`)
        .send({
          title: 'Hacked',
        })
        .expect(403);
    });

    it('should prevent user from deleting another user\'s comment', async () => {
      const user1Response = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'user3@example.com',
          username: 'user3',
          password: 'User3@1234',
        });

      const user2Response = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'user4@example.com',
          username: 'user4',
          password: 'User4@1234',
        });

      const postResponse = await request(app)
        .post('/api/posts')
        .set('Authorization', `Bearer ${user1Response.body.token}`)
        .send({
          title: 'Post',
          content: 'Content',
          publish: true,
        });

      const commentResponse = await request(app)
        .post(`/api/posts/${postResponse.body.post.id}/comments`)
        .set('Authorization', `Bearer ${user1Response.body.token}`)
        .send({
          content: 'Comment',
        });

      await request(app)
        .delete(`/api/comments/${commentResponse.body.comment.id}`)
        .set('Authorization', `Bearer ${user2Response.body.token}`)
        .expect(403);
    });
  });
});

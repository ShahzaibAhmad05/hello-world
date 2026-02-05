import express, { Application, Request, Response } from 'express';
import cors from 'cors';
import authRoutes from './routes/auth.routes';
import postRoutes from './routes/post.routes';
import commentRoutes from './routes/comment.routes';
import { errorHandler } from './middleware/errorHandler';
import { rateLimiter } from './middleware/rateLimiter';

const app: Application = express();

// Global rate limiting
app.use(rateLimiter);

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (_req: Request, res: Response) => {
  res.status(200).json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// API Documentation endpoint
app.get('/api/docs', (_req: Request, res: Response) => {
  res.status(200).json({
    name: 'Blog API with Comments',
    version: '1.0.0',
    description: 'RESTful API for blog posts with nested comments',
    endpoints: {
      auth: {
        'POST /api/auth/register': 'Register new user',
        'POST /api/auth/login': 'Login user',
        'GET /api/auth/profile': 'Get current user profile (auth required)'
      },
      posts: {
        'GET /api/posts': 'Get all published posts (paginated)',
        'GET /api/posts/:id': 'Get single post with comments',
        'POST /api/posts': 'Create new post (auth required)',
        'PUT /api/posts/:id': 'Update post (author only)',
        'DELETE /api/posts/:id': 'Delete post (author only)',
        'PATCH /api/posts/:id/publish': 'Publish post (author only)',
        'PATCH /api/posts/:id/unpublish': 'Unpublish post (author only)'
      },
      comments: {
        'POST /api/posts/:postId/comments': 'Add comment to post (auth required)',
        'POST /api/comments/:commentId/replies': 'Reply to comment (auth required)',
        'DELETE /api/comments/:id': 'Delete own comment (author only)',
        'GET /api/comments/:id': 'Get comment with replies'
      }
    }
  });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/posts', postRoutes);
app.use('/api/comments', commentRoutes);

// 404 Handler
app.use((_req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not Found',
    message: 'The requested resource was not found'
  });
});

// Error Handler
app.use(errorHandler);

export default app;

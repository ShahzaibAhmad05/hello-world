import { Request, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import {
  ValidationError,
  NotFoundError,
  ForbiddenError,
} from '../middleware/errorHandler';
import {
  parsePaginationParams,
  getPaginationSkipTake,
  buildPaginationResult,
} from '../utils/pagination';

interface CreatePostRequest {
  title: string;
  content: string;
  publish?: boolean;
}

interface UpdatePostRequest {
  title?: string;
  content?: string;
}

/**
 * Get all posts (published only for non-authors, all for authors)
 * Supports pagination
 */
export const getAllPosts = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const { page, limit } = parsePaginationParams(
      req.query.page as string,
      req.query.limit as string
    );
    const { skip, take } = getPaginationSkipTake({ page, limit });

    // Build where clause - only published posts for non-authenticated users
    const where = req.userId
      ? {} // Authenticated users see all posts
      : { publishedAt: { not: null } }; // Non-authenticated see only published

    const [posts, total] = await Promise.all([
      prisma.post.findMany({
        where,
        skip,
        take,
        orderBy: { createdAt: 'desc' },
        select: {
          id: true,
          title: true,
          content: true,
          author: true,
          authorId: true,
          publishedAt: true,
          createdAt: true,
          updatedAt: true,
          _count: {
            select: {
              comments: true,
            },
          },
        },
      }),
      prisma.post.count({ where }),
    ]);

    const result = buildPaginationResult(posts, total, { page, limit });

    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
};

/**
 * Get single post by ID with comments tree
 */
export const getPostById = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const { id } = req.params;

    const post = await prisma.post.findUnique({
      where: { id },
      include: {
        comments: {
          where: { parentId: null }, // Only top-level comments
          orderBy: { createdAt: 'desc' },
          include: {
            replies: {
              orderBy: { createdAt: 'asc' },
              select: {
                id: true,
                content: true,
                author: true,
                authorId: true,
                createdAt: true,
                updatedAt: true,
              },
            },
          },
        },
      },
    });

    if (!post) {
      throw new NotFoundError('Post not found');
    }

    // Check if post is published or user is the author
    if (!post.publishedAt && post.authorId !== req.userId) {
      throw new ForbiddenError('This post is not published');
    }

    res.status(200).json({ post });
  } catch (error) {
    next(error);
  }
};

/**
 * Create a new post
 */
export const createPost = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    if (!req.user) {
      throw new ForbiddenError('Authentication required');
    }

    const { title, content, publish }: CreatePostRequest = req.body;

    const post = await prisma.post.create({
      data: {
        title,
        content,
        author: req.user.username,
        authorId: req.user.id,
        publishedAt: publish ? new Date() : null,
      },
      select: {
        id: true,
        title: true,
        content: true,
        author: true,
        authorId: true,
        publishedAt: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    res.status(201).json({
      message: 'Post created successfully',
      post,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Update post (author only)
 */
export const updatePost = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    if (!req.user) {
      throw new ForbiddenError('Authentication required');
    }

    const { id } = req.params;
    const { title, content }: UpdatePostRequest = req.body;

    // Find post and check ownership
    const existingPost = await prisma.post.findUnique({
      where: { id },
    });

    if (!existingPost) {
      throw new NotFoundError('Post not found');
    }

    if (existingPost.authorId !== req.user.id) {
      throw new ForbiddenError('You can only edit your own posts');
    }

    // Update post
    const post = await prisma.post.update({
      where: { id },
      data: {
        ...(title && { title }),
        ...(content && { content }),
      },
      select: {
        id: true,
        title: true,
        content: true,
        author: true,
        authorId: true,
        publishedAt: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    res.status(200).json({
      message: 'Post updated successfully',
      post,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Delete post (author only)
 */
export const deletePost = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    if (!req.user) {
      throw new ForbiddenError('Authentication required');
    }

    const { id } = req.params;

    // Find post and check ownership
    const existingPost = await prisma.post.findUnique({
      where: { id },
    });

    if (!existingPost) {
      throw new NotFoundError('Post not found');
    }

    if (existingPost.authorId !== req.user.id) {
      throw new ForbiddenError('You can only delete your own posts');
    }

    await prisma.post.delete({
      where: { id },
    });

    res.status(200).json({
      message: 'Post deleted successfully',
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Publish post (author only)
 */
export const publishPost = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    if (!req.user) {
      throw new ForbiddenError('Authentication required');
    }

    const { id } = req.params;

    // Find post and check ownership
    const existingPost = await prisma.post.findUnique({
      where: { id },
    });

    if (!existingPost) {
      throw new NotFoundError('Post not found');
    }

    if (existingPost.authorId !== req.user.id) {
      throw new ForbiddenError('You can only publish your own posts');
    }

    if (existingPost.publishedAt) {
      throw new ValidationError('Post is already published');
    }

    const post = await prisma.post.update({
      where: { id },
      data: { publishedAt: new Date() },
    });

    res.status(200).json({
      message: 'Post published successfully',
      post,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Unpublish post (author only)
 */
export const unpublishPost = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    if (!req.user) {
      throw new ForbiddenError('Authentication required');
    }

    const { id } = req.params;

    // Find post and check ownership
    const existingPost = await prisma.post.findUnique({
      where: { id },
    });

    if (!existingPost) {
      throw new NotFoundError('Post not found');
    }

    if (existingPost.authorId !== req.user.id) {
      throw new ForbiddenError('You can only unpublish your own posts');
    }

    if (!existingPost.publishedAt) {
      throw new ValidationError('Post is already unpublished');
    }

    const post = await prisma.post.update({
      where: { id },
      data: { publishedAt: null },
    });

    res.status(200).json({
      message: 'Post unpublished successfully',
      post,
    });
  } catch (error) {
    next(error);
  }
};

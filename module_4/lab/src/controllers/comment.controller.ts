import { Request, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import {
  ValidationError,
  NotFoundError,
  ForbiddenError,
} from '../middleware/errorHandler';

interface CreateCommentRequest {
  content: string;
}

/**
 * Add comment to a post
 */
export const addCommentToPost = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    if (!req.user) {
      throw new ForbiddenError('Authentication required');
    }

    const { postId } = req.params;
    const { content }: CreateCommentRequest = req.body;

    // Verify post exists
    const post = await prisma.post.findUnique({
      where: { id: postId },
    });

    if (!post) {
      throw new NotFoundError('Post not found');
    }

    // Create comment
    const comment = await prisma.comment.create({
      data: {
        content,
        author: req.user.username,
        authorId: req.user.id,
        postId,
      },
      select: {
        id: true,
        content: true,
        author: true,
        authorId: true,
        postId: true,
        parentId: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    res.status(201).json({
      message: 'Comment added successfully',
      comment,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Reply to a comment (1 level deep only)
 */
export const replyToComment = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    if (!req.user) {
      throw new ForbiddenError('Authentication required');
    }

    const { commentId } = req.params;
    const { content }: CreateCommentRequest = req.body;

    // Verify parent comment exists
    const parentComment = await prisma.comment.findUnique({
      where: { id: commentId },
    });

    if (!parentComment) {
      throw new NotFoundError('Comment not found');
    }

    // Check if parent comment is already a reply (only 1 level deep allowed)
    if (parentComment.parentId) {
      throw new ValidationError('Cannot reply to a reply. Only 1 level of nesting allowed');
    }

    // Create reply
    const reply = await prisma.comment.create({
      data: {
        content,
        author: req.user.username,
        authorId: req.user.id,
        postId: parentComment.postId,
        parentId: commentId,
      },
      select: {
        id: true,
        content: true,
        author: true,
        authorId: true,
        postId: true,
        parentId: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    res.status(201).json({
      message: 'Reply added successfully',
      comment: reply,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get comment with its replies
 */
export const getComment = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const { id } = req.params;

    const comment = await prisma.comment.findUnique({
      where: { id },
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
    });

    if (!comment) {
      throw new NotFoundError('Comment not found');
    }

    res.status(200).json({ comment });
  } catch (error) {
    next(error);
  }
};

/**
 * Delete own comment
 */
export const deleteComment = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    if (!req.user) {
      throw new ForbiddenError('Authentication required');
    }

    const { id } = req.params;

    // Find comment and check ownership
    const comment = await prisma.comment.findUnique({
      where: { id },
    });

    if (!comment) {
      throw new NotFoundError('Comment not found');
    }

    if (comment.authorId !== req.user.id) {
      throw new ForbiddenError('You can only delete your own comments');
    }

    // Delete comment (cascade will delete replies)
    await prisma.comment.delete({
      where: { id },
    });

    res.status(200).json({
      message: 'Comment deleted successfully',
    });
  } catch (error) {
    next(error);
  }
};

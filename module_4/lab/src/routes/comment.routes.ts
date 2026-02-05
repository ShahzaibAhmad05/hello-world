import { Router } from 'express';
import {
  addCommentToPost,
  replyToComment,
  getComment,
  deleteComment,
} from '../controllers/comment.controller';
import { createCommentValidation } from '../validators/comment.validator';
import { handleValidationErrors } from '../middleware/validator';
import { authenticate } from '../middleware/auth';

const router = Router();

/**
 * @route   POST /api/posts/:postId/comments
 * @desc    Add comment to post
 * @access  Private
 */
router.post(
  '/posts/:postId/comments',
  authenticate,
  createCommentValidation,
  handleValidationErrors,
  addCommentToPost
);

/**
 * @route   POST /api/comments/:commentId/replies
 * @desc    Reply to a comment
 * @access  Private
 */
router.post(
  '/:commentId/replies',
  authenticate,
  createCommentValidation,
  handleValidationErrors,
  replyToComment
);

/**
 * @route   GET /api/comments/:id
 * @desc    Get comment with replies
 * @access  Public
 */
router.get('/:id', getComment);

/**
 * @route   DELETE /api/comments/:id
 * @desc    Delete own comment
 * @access  Private (author only)
 */
router.delete('/:id', authenticate, deleteComment);

export default router;

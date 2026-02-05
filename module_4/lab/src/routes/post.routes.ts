import { Router } from 'express';
import {
  getAllPosts,
  getPostById,
  createPost,
  updatePost,
  deletePost,
  publishPost,
  unpublishPost,
} from '../controllers/post.controller';
import {
  createPostValidation,
  updatePostValidation,
} from '../validators/post.validator';
import { handleValidationErrors } from '../middleware/validator';
import { authenticate, optionalAuthenticate } from '../middleware/auth';

const router = Router();

/**
 * @route   GET /api/posts
 * @desc    Get all posts (paginated)
 * @access  Public (shows published only) / Private (shows all)
 */
router.get('/', optionalAuthenticate, getAllPosts);

/**
 * @route   GET /api/posts/:id
 * @desc    Get single post with comments
 * @access  Public (published only) / Private (author can see unpublished)
 */
router.get('/:id', optionalAuthenticate, getPostById);

/**
 * @route   POST /api/posts
 * @desc    Create new post
 * @access  Private
 */
router.post(
  '/',
  authenticate,
  createPostValidation,
  handleValidationErrors,
  createPost
);

/**
 * @route   PUT /api/posts/:id
 * @desc    Update post
 * @access  Private (author only)
 */
router.put(
  '/:id',
  authenticate,
  updatePostValidation,
  handleValidationErrors,
  updatePost
);

/**
 * @route   DELETE /api/posts/:id
 * @desc    Delete post
 * @access  Private (author only)
 */
router.delete('/:id', authenticate, deletePost);

/**
 * @route   PATCH /api/posts/:id/publish
 * @desc    Publish post
 * @access  Private (author only)
 */
router.patch('/:id/publish', authenticate, publishPost);

/**
 * @route   PATCH /api/posts/:id/unpublish
 * @desc    Unpublish post
 * @access  Private (author only)
 */
router.patch('/:id/unpublish', authenticate, unpublishPost);

export default router;

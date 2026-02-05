import { Router } from 'express';
import { getAllUsers, getUserById } from '../controllers/user.controller';
import { authenticate } from '../middleware/auth';

const router = Router();

/**
 * @route   GET /api/users
 * @desc    Get all users
 * @access  Private
 */
router.get('/', authenticate, getAllUsers);

/**
 * @route   GET /api/users/:id
 * @desc    Get user by ID
 * @access  Private
 */
router.get('/:id', authenticate, getUserById);

export default router;

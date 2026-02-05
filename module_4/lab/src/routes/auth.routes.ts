import { Router } from 'express';
import { register, login, getProfile } from '../controllers/auth.controller';
import { registerValidation, loginValidation } from '../validators/auth.validator';
import { handleValidationErrors } from '../middleware/validator';
import { authenticate } from '../middleware/auth';

const router = Router();

/**
 * @route   POST /api/auth/register
 * @desc    Register a new user
 * @access  Public
 */
router.post('/register', registerValidation, handleValidationErrors, register);

/**
 * @route   POST /api/auth/login
 * @desc    Login user and get JWT token
 * @access  Public
 */
router.post('/login', loginValidation, handleValidationErrors, login);

/**
 * @route   GET /api/auth/profile
 * @desc    Get current user's profile
 * @access  Private
 */
router.get('/profile', authenticate, getProfile);

export default router;

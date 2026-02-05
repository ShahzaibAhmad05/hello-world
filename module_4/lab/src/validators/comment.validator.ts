import { body } from 'express-validator';

/**
 * Validation rules for creating a comment
 */
export const createCommentValidation = [
  body('content')
    .trim()
    .notEmpty()
    .withMessage('Content is required')
    .isLength({ min: 1, max: 2000 })
    .withMessage('Content must be between 1 and 2000 characters'),
];

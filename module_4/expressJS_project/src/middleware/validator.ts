import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';
import { ValidationError } from './errorHandler';

/**
 * Middleware to handle validation errors from express-validator
 */
export const handleValidationErrors = (
  req: Request,
  _res: Response,
  next: NextFunction
): void => {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    const errorMessages = errors.array().map((err) => err.msg).join(', ');
    throw new ValidationError(errorMessages);
  }

  next();
};

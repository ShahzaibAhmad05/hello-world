import { Request, Response, NextFunction } from 'express';

export interface AppError extends Error {
  statusCode?: number;
  isOperational?: boolean;
}

/**
 * ValidationError - For input validation failures
 */
export class ValidationError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string) {
    super(message);
    this.statusCode = 400;
    this.isOperational = true;
    this.name = 'ValidationError';
  }
}

/**
 * UnauthorizedError - For authentication failures
 */
export class UnauthorizedError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string = 'Unauthorized') {
    super(message);
    this.statusCode = 401;
    this.isOperational = true;
    this.name = 'UnauthorizedError';
  }
}

/**
 * ForbiddenError - For authorization failures
 */
export class ForbiddenError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string = 'Forbidden') {
    super(message);
    this.statusCode = 403;
    this.isOperational = true;
    this.name = 'ForbiddenError';
  }
}

/**
 * NotFoundError - For resource not found
 */
export class NotFoundError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string = 'Resource not found') {
    super(message);
    this.statusCode = 404;
    this.isOperational = true;
    this.name = 'NotFoundError';
  }
}

/**
 * Centralized error handler middleware
 */
export const errorHandler = (
  err: AppError,
  _req: Request,
  res: Response,
  _next: NextFunction
): void => {
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  // Log error for debugging (in production, use proper logging service)
  if (statusCode >= 500) {
    console.error('❌ Error:', {
      name: err.name,
      message: err.message,
      stack: err.stack
    });
  }

  res.status(statusCode).json({
    error: err.name || 'Error',
    message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

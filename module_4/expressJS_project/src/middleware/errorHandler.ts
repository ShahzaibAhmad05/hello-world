import { Request, Response, NextFunction } from 'express';

export interface AppError extends Error {
  statusCode?: number;
  isOperational?: boolean;
}

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
    console.error('Error:', err);
  }

  res.status(statusCode).json({
    error: err.name || 'Error',
    message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

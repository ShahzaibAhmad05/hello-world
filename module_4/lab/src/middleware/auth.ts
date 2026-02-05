import { Request, Response, NextFunction } from 'express';
import { JWTService } from '../services/jwt.service';
import { UnauthorizedError } from './errorHandler';
import prisma from '../lib/prisma';

/**
 * Middleware to authenticate requests using JWT
 * Verifies token and attaches user to request object
 */
export const authenticate = async (
  req: Request,
  _res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const token = JWTService.extractTokenFromHeader(req.headers.authorization);

    if (!token) {
      throw new UnauthorizedError('No token provided');
    }

    const decoded = JWTService.verifyToken(token);

    // Verify user still exists
    const user = await prisma.user.findUnique({
      where: { id: decoded.userId },
    });

    if (!user) {
      throw new UnauthorizedError('User not found');
    }

    // Attach user to request
    req.userId = user.id;
    req.user = user;

    next();
  } catch (error) {
    next(error);
  }
};

/**
 * Optional authentication - doesn't fail if no token provided
 * Used for endpoints that behave differently for authenticated users
 */
export const optionalAuthenticate = async (
  req: Request,
  _res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const token = JWTService.extractTokenFromHeader(req.headers.authorization);

    if (token) {
      const decoded = JWTService.verifyToken(token);
      const user = await prisma.user.findUnique({
        where: { id: decoded.userId },
      });

      if (user) {
        req.userId = user.id;
        req.user = user;
      }
    }

    next();
  } catch (error) {
    // Silently fail for optional auth
    next();
  }
};

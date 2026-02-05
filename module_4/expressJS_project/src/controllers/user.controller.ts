import { Request, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { NotFoundError } from '../middleware/errorHandler';

/**
 * Get all users (admin functionality)
 */
export const getAllUsers = async (
  _req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const users = await prisma.user.findMany({
      select: {
        id: true,
        email: true,
        username: true,
        firstName: true,
        lastName: true,
        isActive: true,
        createdAt: true,
        updatedAt: true,
      },
      orderBy: {
        createdAt: 'desc',
      },
    });

    res.status(200).json({
      count: users.length,
      users,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get user by ID
 */
export const getUserById = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const { id } = req.params;

    const user = await prisma.user.findUnique({
      where: { id },
      select: {
        id: true,
        email: true,
        username: true,
        firstName: true,
        lastName: true,
        isActive: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    if (!user) {
      throw new NotFoundError('User not found');
    }

    res.status(200).json({
      user,
    });
  } catch (error) {
    next(error);
  }
};

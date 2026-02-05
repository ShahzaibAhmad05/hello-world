import jwt from 'jsonwebtoken';
import { UnauthorizedError } from '../middleware/errorHandler';

interface TokenPayload {
  userId: string;
  email: string;
}

export class JWTService {
  private static readonly SECRET = process.env.JWT_SECRET || 'fallback-secret-key';
  private static readonly EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';

  /**
   * Generate a JWT token
   * @param payload - User data to encode in token
   * @returns JWT token string
   */
  static generateToken(payload: TokenPayload): string {
    return jwt.sign(payload, this.SECRET, {
      expiresIn: this.EXPIRES_IN,
    });
  }

  /**
   * Verify and decode a JWT token
   * @param token - JWT token to verify
   * @returns Decoded token payload
   */
  static verifyToken(token: string): TokenPayload {
    try {
      const decoded = jwt.verify(token, this.SECRET) as TokenPayload;
      return decoded;
    } catch (error) {
      if (error instanceof jwt.JsonWebTokenError) {
        throw new UnauthorizedError('Invalid token');
      }
      if (error instanceof jwt.TokenExpiredError) {
        throw new UnauthorizedError('Token has expired');
      }
      throw new UnauthorizedError('Token verification failed');
    }
  }

  /**
   * Extract token from Authorization header
   * @param authHeader - Authorization header value
   * @returns Token string or null
   */
  static extractTokenFromHeader(authHeader: string | undefined): string | null {
    if (!authHeader) {
      return null;
    }

    const parts = authHeader.split(' ');
    if (parts.length !== 2 || parts[0] !== 'Bearer') {
      return null;
    }

    return parts[1];
  }
}

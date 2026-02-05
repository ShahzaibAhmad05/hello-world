import { JWTService } from '../services/jwt.service';
import { UnauthorizedError } from '../middleware/errorHandler';

describe('JWTService', () => {
  const mockPayload = {
    userId: 'test-user-id',
    email: 'test@example.com',
  };

  describe('generateToken', () => {
    it('should generate a valid JWT token', () => {
      const token = JWTService.generateToken(mockPayload);
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.')).toHaveLength(3); // JWT has 3 parts
    });
  });

  describe('verifyToken', () => {
    it('should verify and decode a valid token', () => {
      const token = JWTService.generateToken(mockPayload);
      const decoded = JWTService.verifyToken(token);

      expect(decoded).toBeDefined();
      expect(decoded.userId).toBe(mockPayload.userId);
      expect(decoded.email).toBe(mockPayload.email);
    });

    it('should throw UnauthorizedError for invalid token', () => {
      const invalidToken = 'invalid.token.here';

      expect(() => JWTService.verifyToken(invalidToken)).toThrow(UnauthorizedError);
      expect(() => JWTService.verifyToken(invalidToken)).toThrow('Invalid token');
    });

    it('should throw UnauthorizedError for malformed token', () => {
      expect(() => JWTService.verifyToken('malformed')).toThrow(UnauthorizedError);
    });
  });

  describe('extractTokenFromHeader', () => {
    it('should extract token from valid Bearer header', () => {
      const token = 'test-token-123';
      const authHeader = `Bearer ${token}`;

      const extracted = JWTService.extractTokenFromHeader(authHeader);
      expect(extracted).toBe(token);
    });

    it('should return null for missing header', () => {
      const extracted = JWTService.extractTokenFromHeader(undefined);
      expect(extracted).toBeNull();
    });

    it('should return null for invalid format', () => {
      expect(JWTService.extractTokenFromHeader('InvalidFormat token')).toBeNull();
      expect(JWTService.extractTokenFromHeader('Bearer')).toBeNull();
      expect(JWTService.extractTokenFromHeader('token-only')).toBeNull();
    });
  });
});

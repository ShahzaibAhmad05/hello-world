import { JWTService } from '../jwt.service';
import { UnauthorizedError } from '../../middleware/errorHandler';

describe('JWTService - Unit Tests', () => {
  const mockPayload = {
    userId: 'test-user-id',
    email: 'test@example.com',
    username: 'testuser',
  };

  describe('generateToken', () => {
    it('should generate a valid JWT token', () => {
      const token = JWTService.generateToken(mockPayload);

      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.')).toHaveLength(3);
    });
  });

  describe('verifyToken', () => {
    it('should verify and decode valid token', () => {
      const token = JWTService.generateToken(mockPayload);
      const decoded = JWTService.verifyToken(token);

      expect(decoded).toBeDefined();
      expect(decoded.userId).toBe(mockPayload.userId);
      expect(decoded.email).toBe(mockPayload.email);
      expect(decoded.username).toBe(mockPayload.username);
    });

    it('should throw UnauthorizedError for invalid token', () => {
      expect(() => JWTService.verifyToken('invalid.token.here')).toThrow(UnauthorizedError);
    });

    it('should throw UnauthorizedError for malformed token', () => {
      expect(() => JWTService.verifyToken('malformed')).toThrow(UnauthorizedError);
    });
  });

  describe('extractTokenFromHeader', () => {
    it('should extract token from valid Bearer header', () => {
      const token = 'test-token-123';
      const extracted = JWTService.extractTokenFromHeader(`Bearer ${token}`);

      expect(extracted).toBe(token);
    });

    it('should return null for missing header', () => {
      expect(JWTService.extractTokenFromHeader(undefined)).toBeNull();
    });

    it('should return null for invalid format', () => {
      expect(JWTService.extractTokenFromHeader('InvalidFormat token')).toBeNull();
      expect(JWTService.extractTokenFromHeader('Bearer')).toBeNull();
      expect(JWTService.extractTokenFromHeader('token-only')).toBeNull();
    });
  });
});

import { hashPassword, comparePassword } from '../password';

describe('Password Utils - Unit Tests', () => {
  const plainPassword = 'TestPass123!';

  describe('hashPassword', () => {
    it('should hash a password', async () => {
      const hashed = await hashPassword(plainPassword);

      expect(hashed).toBeDefined();
      expect(typeof hashed).toBe('string');
      expect(hashed).not.toBe(plainPassword);
      expect(hashed.length).toBeGreaterThan(50);
    });

    it('should generate different hashes for same password', async () => {
      const hash1 = await hashPassword(plainPassword);
      const hash2 = await hashPassword(plainPassword);

      expect(hash1).not.toBe(hash2);
    });
  });

  describe('comparePassword', () => {
    it('should return true for matching password', async () => {
      const hashed = await hashPassword(plainPassword);
      const isMatch = await comparePassword(plainPassword, hashed);

      expect(isMatch).toBe(true);
    });

    it('should return false for non-matching password', async () => {
      const hashed = await hashPassword(plainPassword);
      const isMatch = await comparePassword('WrongPassword', hashed);

      expect(isMatch).toBe(false);
    });

    it('should return false for invalid hash', async () => {
      const isMatch = await comparePassword(plainPassword, 'invalid-hash');

      expect(isMatch).toBe(false);
    });
  });
});

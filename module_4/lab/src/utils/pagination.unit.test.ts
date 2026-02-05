import {
  parsePaginationParams,
  getPaginationSkipTake,
  buildPaginationResult,
} from '../pagination';

describe('Pagination Utils - Unit Tests', () => {
  describe('parsePaginationParams', () => {
    it('should parse valid pagination params', () => {
      const result = parsePaginationParams('2', '20');

      expect(result).toEqual({
        page: 2,
        limit: 20,
      });
    });

    it('should use default values when params are undefined', () => {
      const result = parsePaginationParams();

      expect(result).toEqual({
        page: 1,
        limit: 10,
      });
    });

    it('should enforce minimum page of 1', () => {
      const result = parsePaginationParams('0', '10');

      expect(result.page).toBe(1);
    });

    it('should enforce maximum limit of 100', () => {
      const result = parsePaginationParams('1', '200');

      expect(result.limit).toBe(100);
    });

    it('should enforce minimum limit of 1', () => {
      const result = parsePaginationParams('1', '0');

      expect(result.limit).toBe(1);
    });
  });

  describe('getPaginationSkipTake', () => {
    it('should calculate correct skip and take for first page', () => {
      const result = getPaginationSkipTake({ page: 1, limit: 10 });

      expect(result).toEqual({
        skip: 0,
        take: 10,
      });
    });

    it('should calculate correct skip and take for subsequent pages', () => {
      const result = getPaginationSkipTake({ page: 3, limit: 20 });

      expect(result).toEqual({
        skip: 40,
        take: 20,
      });
    });
  });

  describe('buildPaginationResult', () => {
    it('should build correct pagination result', () => {
      const data = [1, 2, 3, 4, 5];
      const result = buildPaginationResult(data, 50, { page: 2, limit: 5 });

      expect(result).toEqual({
        data: [1, 2, 3, 4, 5],
        pagination: {
          page: 2,
          limit: 5,
          total: 50,
          totalPages: 10,
          hasNext: true,
          hasPrev: true,
        },
      });
    });

    it('should indicate no next page on last page', () => {
      const data = [1, 2, 3];
      const result = buildPaginationResult(data, 13, { page: 3, limit: 5 });

      expect(result.pagination.hasNext).toBe(false);
      expect(result.pagination.hasPrev).toBe(true);
    });

    it('should indicate no prev page on first page', () => {
      const data = [1, 2, 3, 4, 5];
      const result = buildPaginationResult(data, 20, { page: 1, limit: 5 });

      expect(result.pagination.hasNext).toBe(true);
      expect(result.pagination.hasPrev).toBe(false);
    });
  });
});

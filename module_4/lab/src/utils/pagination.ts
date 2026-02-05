/**
 * Pagination utility for list endpoints
 */
export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginationResult<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

/**
 * Parse pagination parameters from request query
 * @param page - Page number (1-indexed)
 * @param limit - Items per page
 * @returns Validated pagination params
 */
export function parsePaginationParams(
  page?: string | number,
  limit?: string | number
): PaginationParams {
  const pageNum = Math.max(1, parseInt(String(page || '1'), 10));
  const limitNum = Math.min(100, Math.max(1, parseInt(String(limit || '10'), 10)));

  return {
    page: pageNum,
    limit: limitNum,
  };
}

/**
 * Calculate Prisma skip and take values
 * @param params - Pagination parameters
 * @returns Object with skip and take values
 */
export function getPaginationSkipTake(params: PaginationParams): {
  skip: number;
  take: number;
} {
  return {
    skip: (params.page - 1) * params.limit,
    take: params.limit,
  };
}

/**
 * Build pagination result with metadata
 * @param data - Array of items
 * @param total - Total number of items
 * @param params - Pagination parameters
 * @returns Pagination result with metadata
 */
export function buildPaginationResult<T>(
  data: T[],
  total: number,
  params: PaginationParams
): PaginationResult<T> {
  const totalPages = Math.ceil(total / params.limit);

  return {
    data,
    pagination: {
      page: params.page,
      limit: params.limit,
      total,
      totalPages,
      hasNext: params.page < totalPages,
      hasPrev: params.page > 1,
    },
  };
}

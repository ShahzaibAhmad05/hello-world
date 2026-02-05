"""Context-Rich Search Function Implementation

Based on context-rich prompt: Search function for e-commerce application with
advanced filtering, pagination, and performance optimization.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SortOrder(Enum):
    RELEVANCE = "relevance"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"


@dataclass
class Product:
    id: int
    name: str
    description: str
    category: str
    price: float
    availability: bool
    relevance_score: float = 0.0


@dataclass
class SearchResult:
    products: List[Product]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class ProductSearchEngine:
    """Advanced product search with filtering, sorting, and pagination."""

    def __init__(self, products: List[Product]):
        self.products = products

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: SortOrder = SortOrder.RELEVANCE,
        available_only: bool = False
    ) -> SearchResult:
        """
        Search products with advanced filtering and pagination.

        Args:
            query: Search query string (case-insensitive partial matching)
            category: Filter by category (optional)
            min_price: Minimum price filter (optional)
            max_price: Maximum price filter (optional)
            page: Page number (1-indexed)
            page_size: Number of results per page
            sort_by: Sort order for results
            available_only: Only return available products

        Returns:
            SearchResult with paginated products and metadata

        Raises:
            ValueError: If page or page_size are invalid
            ConnectionError: If database connection fails (simulated)
        """
        # Input validation
        if page < 1:
            raise ValueError("Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        try:
            # Filter products
            filtered_products = self._filter_products(
                query, category, min_price, max_price, available_only
            )

            # Calculate relevance scores
            if query:
                filtered_products = self._calculate_relevance(query, filtered_products)

            # Sort products
            sorted_products = self._sort_products(filtered_products, sort_by)

            # Apply pagination
            total_count = len(sorted_products)
            total_pages = (total_count + page_size - 1) // page_size
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_products = sorted_products[start_idx:end_idx]

            return SearchResult(
                products=paginated_products,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            # Simulate database connection error handling
            raise ConnectionError(f"Database error during search: {str(e)}")

    def _filter_products(
        self,
        query: str,
        category: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
        available_only: bool
    ) -> List[Product]:
        """Apply all filters to product list."""
        results = self.products

        # Handle empty query gracefully
        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if query_lower in p.name.lower() or query_lower in p.description.lower()
            ]

        if category:
            results = [p for p in results if p.category.lower() == category.lower()]

        if min_price is not None:
            results = [p for p in results if p.price >= min_price]

        if max_price is not None:
            results = [p for p in results if p.price <= max_price]

        if available_only:
            results = [p for p in results if p.availability]

        return results

    def _calculate_relevance(self, query: str, products: List[Product]) -> List[Product]:
        """Calculate relevance scores for search results."""
        query_lower = query.lower()
        for product in products:
            score = 0.0
            # Exact name match gets highest score
            if query_lower == product.name.lower():
                score += 100
            # Name contains query
            elif query_lower in product.name.lower():
                score += 50
            # Description contains query
            if query_lower in product.description.lower():
                score += 20
            # Boost for availability
            if product.availability:
                score += 10
            product.relevance_score = score
        return products

    def _sort_products(self, products: List[Product], sort_by: SortOrder) -> List[Product]:
        """Sort products based on specified order."""
        if sort_by == SortOrder.RELEVANCE:
            return sorted(products, key=lambda p: p.relevance_score, reverse=True)
        elif sort_by == SortOrder.PRICE_ASC:
            return sorted(products, key=lambda p: p.price)
        elif sort_by == SortOrder.PRICE_DESC:
            return sorted(products, key=lambda p: p.price, reverse=True)
        elif sort_by == SortOrder.NAME_ASC:
            return sorted(products, key=lambda p: p.name.lower())
        elif sort_by == SortOrder.NAME_DESC:
            return sorted(products, key=lambda p: p.name.lower(), reverse=True)
        return products


# Example usage
if __name__ == "__main__":
    # Sample product database
    sample_products = [
        Product(1, "Laptop Pro 15", "High-performance laptop with 16GB RAM", "Electronics", 1299.99, True),
        Product(2, "Wireless Mouse", "Ergonomic wireless mouse", "Electronics", 29.99, True),
        Product(3, "Laptop Bag", "Durable laptop carrying bag", "Accessories", 49.99, True),
        Product(4, "USB-C Cable", "Fast charging USB-C cable", "Electronics", 15.99, False),
        Product(5, "Laptop Stand", "Adjustable aluminum laptop stand", "Accessories", 39.99, True),
    ]

    search_engine = ProductSearchEngine(sample_products)

    # Search for laptops
    results = search_engine.search(
        query="laptop",
        category="Electronics",
        max_price=2000,
        page=1,
        page_size=10,
        available_only=True
    )

    print(f"Found {results.total_count} products:")
    for product in results.products:
        print(f"- {product.name}: ${product.price} (Score: {product.relevance_score})")

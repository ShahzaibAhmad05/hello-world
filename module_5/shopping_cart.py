"""
Shopping Cart Module

Implements a shopping cart system with the following features:
- Add items with quantity
- Update item quantities
- Remove items
- Calculate total price
- Enforce maximum 100 items limit
"""

from typing import Dict, Optional


class ShoppingCartError(Exception):
    """Base exception for shopping cart errors."""
    pass


class ItemLimitExceededError(ShoppingCartError):
    """Raised when cart exceeds maximum item limit."""
    pass


class ShoppingCart:
    """
    A shopping cart that manages items and their quantities.
    
    Attributes:
        MAX_ITEMS: Maximum total quantity of items allowed in cart (100)
    """
    
    MAX_ITEMS = 100
    
    def __init__(self) -> None:
        """Initialize an empty shopping cart."""
        self._items: Dict[str, Dict[str, float]] = {}
    
    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        """
        Add an item to the cart or increase its quantity if it already exists.
        
        Args:
            name: Name of the item
            price: Price per unit of the item
            quantity: Number of items to add (default: 1)
            
        Raises:
            ValueError: If price is negative or quantity is not positive
            ItemLimitExceededError: If adding items would exceed MAX_ITEMS limit
        """
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        current_total = self._get_total_quantity()
        new_total = current_total + quantity
        
        if new_total > self.MAX_ITEMS:
            raise ItemLimitExceededError(
                f"Cannot add {quantity} items. Cart would exceed maximum of {self.MAX_ITEMS} items. "
                f"Current total: {current_total}"
            )
        
        if name in self._items:
            self._items[name]['quantity'] += quantity
        else:
            self._items[name] = {'price': price, 'quantity': quantity}
    
    def update_quantity(self, name: str, quantity: int) -> None:
        """
        Update the quantity of an existing item in the cart.
        
        Args:
            name: Name of the item to update
            quantity: New quantity (must be positive)
            
        Raises:
            KeyError: If item is not in the cart
            ValueError: If quantity is not positive
            ItemLimitExceededError: If new quantity would exceed MAX_ITEMS limit
        """
        if name not in self._items:
            raise KeyError(f"Item '{name}' not found in cart")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        current_total = self._get_total_quantity()
        current_item_quantity = self._items[name]['quantity']
        new_total = current_total - current_item_quantity + quantity
        
        if new_total > self.MAX_ITEMS:
            raise ItemLimitExceededError(
                f"Cannot update to {quantity} items. Cart would exceed maximum of {self.MAX_ITEMS} items. "
                f"Current total: {current_total}"
            )
        
        self._items[name]['quantity'] = quantity
    
    def remove_item(self, name: str) -> None:
        """
        Remove an item completely from the cart.
        
        Args:
            name: Name of the item to remove
            
        Raises:
            KeyError: If item is not in the cart
        """
        if name not in self._items:
            raise KeyError(f"Item '{name}' not found in cart")
        
        del self._items[name]
    
    def get_total(self) -> float:
        """
        Calculate the total price of all items in the cart.
        
        Returns:
            Total price of all items (sum of price * quantity for each item)
        """
        total = sum(
            item['price'] * item['quantity']
            for item in self._items.values()
        )
        return round(total, 2)
    
    def get_item_quantity(self, name: str) -> Optional[int]:
        """
        Get the quantity of a specific item in the cart.
        
        Args:
            name: Name of the item
            
        Returns:
            Quantity of the item, or None if item is not in cart
        """
        if name in self._items:
            return self._items[name]['quantity']
        return None
    
    def get_items(self) -> Dict[str, Dict[str, float]]:
        """
        Get a copy of all items in the cart.
        
        Returns:
            Dictionary mapping item names to their details (price, quantity)
        """
        return {
            name: {'price': item['price'], 'quantity': item['quantity']}
            for name, item in self._items.items()
        }
    
    def clear(self) -> None:
        """Remove all items from the cart."""
        self._items.clear()
    
    def _get_total_quantity(self) -> int:
        """
        Get the total quantity of all items in the cart.
        
        Returns:
            Sum of quantities of all items
        """
        return sum(item['quantity'] for item in self._items.values())
    
    def is_empty(self) -> bool:
        """
        Check if the cart is empty.
        
        Returns:
            True if cart has no items, False otherwise
        """
        return len(self._items) == 0
    
    def __len__(self) -> int:
        """Return the total number of items in the cart."""
        return self._get_total_quantity()
    
    def __repr__(self) -> str:
        """Return string representation of the cart."""
        return f"ShoppingCart(items={len(self._items)}, total_quantity={self._get_total_quantity()}, total_price={self.get_total()})"

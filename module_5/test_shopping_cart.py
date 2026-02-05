"""
Test Suite for Shopping Cart Module

Tests all requirements:
1. Items can be added with quantity
2. Item quantity can be updated
3. Items can be removed
4. Total price is calculated correctly
5. Cart cannot exceed 100 items
"""

import pytest
from shopping_cart import ShoppingCart, ShoppingCartError, ItemLimitExceededError


class TestShoppingCartAddItems:
    """Test Requirement 1: Items can be added with quantity"""
    
    def test_add_single_item(self):
        """Test adding a single item to empty cart"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 1)
        
        assert cart.get_item_quantity("Apple") == 1
        assert len(cart) == 1
    
    def test_add_item_with_multiple_quantity(self):
        """Test adding an item with quantity > 1"""
        cart = ShoppingCart()
        cart.add_item("Banana", 0.75, 5)
        
        assert cart.get_item_quantity("Banana") == 5
        assert len(cart) == 5
    
    def test_add_multiple_different_items(self):
        """Test adding multiple different items"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.add_item("Banana", 0.75, 3)
        cart.add_item("Orange", 2.00, 1)
        
        assert cart.get_item_quantity("Apple") == 2
        assert cart.get_item_quantity("Banana") == 3
        assert cart.get_item_quantity("Orange") == 1
        assert len(cart) == 6
    
    def test_add_same_item_twice_increases_quantity(self):
        """Test adding the same item twice increases its quantity"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.add_item("Apple", 1.50, 3)
        
        assert cart.get_item_quantity("Apple") == 5
        assert len(cart) == 5
    
    def test_add_item_default_quantity(self):
        """Test adding item with default quantity of 1"""
        cart = ShoppingCart()
        cart.add_item("Grape", 3.00)
        
        assert cart.get_item_quantity("Grape") == 1
    
    def test_add_item_with_zero_quantity_raises_error(self):
        """Test that adding item with quantity 0 raises ValueError"""
        cart = ShoppingCart()
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            cart.add_item("Apple", 1.50, 0)
    
    def test_add_item_with_negative_quantity_raises_error(self):
        """Test that adding item with negative quantity raises ValueError"""
        cart = ShoppingCart()
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            cart.add_item("Apple", 1.50, -1)
    
    def test_add_item_with_negative_price_raises_error(self):
        """Test that adding item with negative price raises ValueError"""
        cart = ShoppingCart()
        
        with pytest.raises(ValueError, match="Price cannot be negative"):
            cart.add_item("Apple", -1.50, 1)
    
    def test_add_item_with_zero_price(self):
        """Test adding item with price of 0 (free item)"""
        cart = ShoppingCart()
        cart.add_item("Free Sample", 0.00, 1)
        
        assert cart.get_item_quantity("Free Sample") == 1
        assert cart.get_total() == 0.00


class TestShoppingCartUpdateQuantity:
    """Test Requirement 2: Item quantity can be updated"""
    
    def test_update_quantity_increase(self):
        """Test increasing the quantity of an item"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.update_quantity("Apple", 5)
        
        assert cart.get_item_quantity("Apple") == 5
        assert len(cart) == 5
    
    def test_update_quantity_decrease(self):
        """Test decreasing the quantity of an item"""
        cart = ShoppingCart()
        cart.add_item("Banana", 0.75, 10)
        cart.update_quantity("Banana", 3)
        
        assert cart.get_item_quantity("Banana") == 3
        assert len(cart) == 3
    
    def test_update_quantity_to_one(self):
        """Test updating quantity to 1"""
        cart = ShoppingCart()
        cart.add_item("Orange", 2.00, 5)
        cart.update_quantity("Orange", 1)
        
        assert cart.get_item_quantity("Orange") == 1
    
    def test_update_nonexistent_item_raises_error(self):
        """Test updating quantity of item not in cart raises KeyError"""
        cart = ShoppingCart()
        
        with pytest.raises(KeyError, match="Item 'Ghost' not found in cart"):
            cart.update_quantity("Ghost", 5)
    
    def test_update_quantity_to_zero_raises_error(self):
        """Test updating quantity to 0 raises ValueError"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            cart.update_quantity("Apple", 0)
    
    def test_update_quantity_to_negative_raises_error(self):
        """Test updating quantity to negative value raises ValueError"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            cart.update_quantity("Apple", -3)
    
    def test_update_quantity_multiple_times(self):
        """Test updating the same item quantity multiple times"""
        cart = ShoppingCart()
        cart.add_item("Mango", 2.50, 5)
        cart.update_quantity("Mango", 10)
        cart.update_quantity("Mango", 3)
        
        assert cart.get_item_quantity("Mango") == 3


class TestShoppingCartRemoveItems:
    """Test Requirement 3: Items can be removed"""
    
    def test_remove_existing_item(self):
        """Test removing an item from the cart"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.remove_item("Apple")
        
        assert cart.get_item_quantity("Apple") is None
        assert cart.is_empty()
    
    def test_remove_one_of_multiple_items(self):
        """Test removing one item while others remain"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.add_item("Banana", 0.75, 3)
        cart.add_item("Orange", 2.00, 1)
        
        cart.remove_item("Banana")
        
        assert cart.get_item_quantity("Apple") == 2
        assert cart.get_item_quantity("Banana") is None
        assert cart.get_item_quantity("Orange") == 1
        assert len(cart) == 3
    
    def test_remove_nonexistent_item_raises_error(self):
        """Test removing an item not in cart raises KeyError"""
        cart = ShoppingCart()
        
        with pytest.raises(KeyError, match="Item 'Ghost' not found in cart"):
            cart.remove_item("Ghost")
    
    def test_remove_all_items_individually(self):
        """Test removing all items one by one"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.add_item("Banana", 0.75, 3)
        
        cart.remove_item("Apple")
        cart.remove_item("Banana")
        
        assert cart.is_empty()
        assert cart.get_total() == 0.00
    
    def test_remove_item_twice_raises_error(self):
        """Test removing the same item twice raises error on second attempt"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.remove_item("Apple")
        
        with pytest.raises(KeyError):
            cart.remove_item("Apple")


class TestShoppingCartTotalPrice:
    """Test Requirement 4: Total price is calculated correctly"""
    
    def test_total_price_empty_cart(self):
        """Test total price of empty cart is 0"""
        cart = ShoppingCart()
        
        assert cart.get_total() == 0.00
    
    def test_total_price_single_item(self):
        """Test total price with single item"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 1)
        
        assert cart.get_total() == 1.50
    
    def test_total_price_single_item_multiple_quantity(self):
        """Test total price with single item but multiple quantity"""
        cart = ShoppingCart()
        cart.add_item("Banana", 0.75, 4)
        
        assert cart.get_total() == 3.00
    
    def test_total_price_multiple_items(self):
        """Test total price with multiple different items"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)   # 3.00
        cart.add_item("Banana", 0.75, 4)  # 3.00
        cart.add_item("Orange", 2.00, 1)  # 2.00
        
        assert cart.get_total() == 8.00
    
    def test_total_price_after_adding_same_item(self):
        """Test total price after adding the same item multiple times"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)  # 3.00
        cart.add_item("Apple", 1.50, 3)  # +4.50 = 7.50
        
        assert cart.get_total() == 7.50
    
    def test_total_price_after_update_quantity(self):
        """Test total price after updating quantity"""
        cart = ShoppingCart()
        cart.add_item("Apple", 2.00, 5)  # 10.00
        cart.update_quantity("Apple", 3)  # 6.00
        
        assert cart.get_total() == 6.00
    
    def test_total_price_after_removing_item(self):
        """Test total price after removing an item"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)   # 3.00
        cart.add_item("Banana", 0.75, 4)  # 3.00
        cart.remove_item("Apple")         # 3.00
        
        assert cart.get_total() == 3.00
    
    def test_total_price_with_decimal_prices(self):
        """Test total price calculation with decimal values"""
        cart = ShoppingCart()
        cart.add_item("Item1", 1.99, 3)   # 5.97
        cart.add_item("Item2", 0.50, 5)   # 2.50
        
        assert cart.get_total() == 8.47
    
    def test_total_price_rounded_to_two_decimals(self):
        """Test that total price is rounded to 2 decimal places"""
        cart = ShoppingCart()
        cart.add_item("Item", 0.33, 3)  # 0.99
        
        total = cart.get_total()
        assert isinstance(total, float)
        # Check it's rounded to 2 decimal places
        assert total == 0.99
    
    def test_total_price_after_clearing_cart(self):
        """Test total price after clearing the cart"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.add_item("Banana", 0.75, 3)
        cart.clear()
        
        assert cart.get_total() == 0.00


class TestShoppingCartItemLimit:
    """Test Requirement 5: Cart cannot exceed 100 items"""
    
    def test_add_exactly_100_items(self):
        """Test adding exactly 100 items is allowed"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.00, 100)
        
        assert len(cart) == 100
        assert cart.get_item_quantity("Apple") == 100
    
    def test_add_101_items_raises_error(self):
        """Test adding 101 items raises ItemLimitExceededError"""
        cart = ShoppingCart()
        
        with pytest.raises(ItemLimitExceededError, match="Cannot add 101 items"):
            cart.add_item("Apple", 1.00, 101)
    
    def test_add_items_exceeding_limit_in_steps_raises_error(self):
        """Test adding items in multiple steps that exceed limit raises error"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.00, 50)
        cart.add_item("Banana", 0.75, 40)
        
        with pytest.raises(ItemLimitExceededError, match="Cannot add 11 items"):
            cart.add_item("Orange", 2.00, 11)
    
    def test_add_to_existing_item_exceeding_limit_raises_error(self):
        """Test adding to existing item that would exceed limit raises error"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.00, 60)
        
        with pytest.raises(ItemLimitExceededError):
            cart.add_item("Apple", 1.00, 41)
    
    def test_update_quantity_exceeding_limit_raises_error(self):
        """Test updating quantity beyond limit raises error"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.00, 50)
        
        with pytest.raises(ItemLimitExceededError):
            cart.update_quantity("Apple", 101)
    
    def test_update_quantity_with_multiple_items_exceeding_limit(self):
        """Test updating quantity with other items that would exceed limit"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.00, 30)
        cart.add_item("Banana", 0.75, 40)
        
        with pytest.raises(ItemLimitExceededError):
            cart.update_quantity("Apple", 71)  # 71 + 40 = 111
    
    def test_update_quantity_to_100_with_other_items(self):
        """Test updating quantity is allowed if total stays at or under 100"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.00, 30)
        cart.add_item("Banana", 0.75, 40)
        cart.update_quantity("Apple", 60)  # 60 + 40 = 100
        
        assert len(cart) == 100
    
    def test_error_message_includes_current_total(self):
        """Test error message includes helpful information about current state"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.00, 80)
        
        with pytest.raises(ItemLimitExceededError, match="Current total: 80"):
            cart.add_item("Banana", 0.75, 25)
    
    def test_can_add_items_after_removing_to_make_space(self):
        """Test can add items after removing items to free up space"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.00, 60)
        cart.add_item("Banana", 0.75, 40)  # Total: 100
        
        cart.remove_item("Banana")  # Total: 60
        cart.add_item("Orange", 2.00, 40)  # Total: 100
        
        assert len(cart) == 100
        assert cart.get_item_quantity("Orange") == 40
    
    def test_max_items_constant(self):
        """Test that MAX_ITEMS constant is set to 100"""
        assert ShoppingCart.MAX_ITEMS == 100


class TestShoppingCartAdditionalFeatures:
    """Test additional helper methods and features"""
    
    def test_get_items_returns_copy(self):
        """Test get_items returns a copy of items dict"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        
        items = cart.get_items()
        assert "Apple" in items
        assert items["Apple"]["price"] == 1.50
        assert items["Apple"]["quantity"] == 2
    
    def test_is_empty_on_new_cart(self):
        """Test is_empty returns True for new cart"""
        cart = ShoppingCart()
        assert cart.is_empty()
    
    def test_is_empty_after_adding_items(self):
        """Test is_empty returns False after adding items"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 1)
        assert not cart.is_empty()
    
    def test_clear_method(self):
        """Test clear method removes all items"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.add_item("Banana", 0.75, 3)
        
        cart.clear()
        
        assert cart.is_empty()
        assert len(cart) == 0
    
    def test_len_method(self):
        """Test __len__ returns total quantity"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        cart.add_item("Banana", 0.75, 3)
        
        assert len(cart) == 5
    
    def test_repr_method(self):
        """Test __repr__ returns useful string representation"""
        cart = ShoppingCart()
        cart.add_item("Apple", 1.50, 2)
        
        repr_str = repr(cart)
        assert "ShoppingCart" in repr_str
        assert "items=" in repr_str
        assert "total_quantity=" in repr_str
        assert "total_price=" in repr_str


class TestShoppingCartEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_high_price_item(self):
        """Test handling items with very high prices"""
        cart = ShoppingCart()
        cart.add_item("Diamond", 999999.99, 1)
        
        assert cart.get_total() == 999999.99
    
    def test_many_different_items(self):
        """Test cart with many different types of items"""
        cart = ShoppingCart()
        for i in range(20):
            cart.add_item(f"Item{i}", 1.00, 1)
        
        assert len(cart) == 20
        assert cart.get_total() == 20.00
    
    def test_item_names_case_sensitive(self):
        """Test that item names are case-sensitive"""
        cart = ShoppingCart()
        cart.add_item("apple", 1.00, 1)
        cart.add_item("Apple", 1.50, 1)
        
        assert cart.get_item_quantity("apple") == 1
        assert cart.get_item_quantity("Apple") == 1
        assert len(cart) == 2
    
    def test_item_names_with_special_characters(self):
        """Test items with special characters in names"""
        cart = ShoppingCart()
        cart.add_item("Ben & Jerry's", 5.99, 1)
        cart.add_item("Häagen-Dazs", 6.99, 1)
        
        assert cart.get_item_quantity("Ben & Jerry's") == 1
        assert cart.get_item_quantity("Häagen-Dazs") == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

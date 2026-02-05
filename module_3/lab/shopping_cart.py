"""Complete Shopping Cart System Implementation

Based on comprehensive context-aware prompt for e-commerce application.
Includes: Add, remove, update items, calculate totals, apply discounts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from enum import Enum
import json


class DiscountType(Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    BOGO = "bogo"  # Buy One Get One
    BULK = "bulk"  # Quantity-based
    LOYALTY = "loyalty"  # User tier


class UserTier(Enum):
    GUEST = "guest"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


@dataclass
class Product:
    id: int
    name: str
    price: Decimal
    stock: int
    max_quantity: int = 10
    min_quantity: int = 1


@dataclass
class Discount:
    code: str
    type: DiscountType
    value: Decimal
    min_purchase: Decimal = Decimal('0')
    applicable_tiers: List[UserTier] = field(default_factory=lambda: list(UserTier))
    expiry: Optional[datetime] = None
    stackable: bool = True


@dataclass
class CartItem:
    product: Product
    quantity: int
    gift_wrap: bool = False
    special_instructions: Optional[str] = None

    @property
    def subtotal(self) -> Decimal:
        return self.product.price * Decimal(self.quantity)


@dataclass
class ShippingOption:
    id: str
    name: str
    cost: Decimal
    estimated_days: int


class CartError(Exception):
    """Base exception for cart operations."""
    pass


class InsufficientStockError(CartError):
    """Raised when product stock is insufficient."""
    pass


class InvalidQuantityError(CartError):
    """Raised when quantity is invalid."""
    pass


class DiscountNotApplicableError(CartError):
    """Raised when discount cannot be applied."""
    pass


class ShoppingCart:
    """Complete shopping cart system with discounts and persistence."""

    def __init__(
        self,
        user_id: Optional[int] = None,
        user_tier: UserTier = UserTier.GUEST,
        tax_rate: Decimal = Decimal('0.08'),  # 8% tax
        currency: str = 'USD'
    ):
        self.user_id = user_id
        self.user_tier = user_tier
        self.tax_rate = tax_rate
        self.currency = currency
        self.items: List[CartItem] = []
        self.applied_discounts: List[Discount] = []
        self.shipping_option: Optional[ShippingOption] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_item(
        self,
        product: Product,
        quantity: int = 1,
        gift_wrap: bool = False,
        special_instructions: Optional[str] = None
    ) -> None:
        """
        Add item to cart with validation.

        Args:
            product: Product to add
            quantity: Quantity to add
            gift_wrap: Whether to gift wrap
            special_instructions: Special delivery instructions

        Raises:
            InsufficientStockError: If not enough stock
            InvalidQuantityError: If quantity is invalid
        """
        # Validate quantity
        if quantity < product.min_quantity:
            raise InvalidQuantityError(
                f"Minimum quantity for {product.name} is {product.min_quantity}"
            )
        if quantity > product.max_quantity:
            raise InvalidQuantityError(
                f"Maximum quantity for {product.name} is {product.max_quantity}"
            )

        # Check if item already in cart
        existing_item = self._find_item(product.id)
        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if new_quantity > product.max_quantity:
                raise InvalidQuantityError(
                    f"Total quantity would exceed maximum of {product.max_quantity}"
                )
            # Check stock
            if new_quantity > product.stock:
                raise InsufficientStockError(
                    f"Only {product.stock} units of {product.name} available"
                )
            existing_item.quantity = new_quantity
        else:
            # Check stock for new item
            if quantity > product.stock:
                raise InsufficientStockError(
                    f"Only {product.stock} units of {product.name} available"
                )
            cart_item = CartItem(
                product=product,
                quantity=quantity,
                gift_wrap=gift_wrap,
                special_instructions=special_instructions
            )
            self.items.append(cart_item)

        self.updated_at = datetime.now()

    def remove_item(self, product_id: int) -> bool:
        """
        Remove item from cart.

        Args:
            product_id: ID of product to remove

        Returns:
            True if item was removed, False if not found
        """
        for i, item in enumerate(self.items):
            if item.product.id == product_id:
                self.items.pop(i)
                self.updated_at = datetime.now()
                return True
        return False

    def update_quantity(self, product_id: int, quantity: int) -> None:
        """
        Update item quantity with validation.

        Args:
            product_id: ID of product to update
            quantity: New quantity

        Raises:
            CartError: If item not found
            InvalidQuantityError: If quantity is invalid
            InsufficientStockError: If not enough stock
        """
        item = self._find_item(product_id)
        if not item:
            raise CartError(f"Product {product_id} not in cart")

        if quantity < item.product.min_quantity:
            raise InvalidQuantityError(
                f"Minimum quantity is {item.product.min_quantity}"
            )
        if quantity > item.product.max_quantity:
            raise InvalidQuantityError(
                f"Maximum quantity is {item.product.max_quantity}"
            )
        if quantity > item.product.stock:
            raise InsufficientStockError(
                f"Only {item.product.stock} units available"
            )

        item.quantity = quantity
        self.updated_at = datetime.now()

    def apply_discount(self, discount: Discount) -> None:
        """
        Apply discount code with validation.

        Args:
            discount: Discount to apply

        Raises:
            DiscountNotApplicableError: If discount cannot be applied
        """
        # Check expiry
        if discount.expiry and datetime.now() > discount.expiry:
            raise DiscountNotApplicableError("Discount has expired")

        # Check user tier eligibility
        if discount.applicable_tiers and self.user_tier not in discount.applicable_tiers:
            raise DiscountNotApplicableError(
                f"Discount only available for {[t.value for t in discount.applicable_tiers]}"
            )

        # Check minimum purchase
        subtotal = self.calculate_subtotal()
        if subtotal < discount.min_purchase:
            raise DiscountNotApplicableError(
                f"Minimum purchase of {self._format_currency(discount.min_purchase)} required"
            )

        # Check stacking rules
        if not discount.stackable and self.applied_discounts:
            raise DiscountNotApplicableError(
                "This discount cannot be combined with other discounts"
            )

        self.applied_discounts.append(discount)
        self.updated_at = datetime.now()

    def set_shipping(self, shipping_option: ShippingOption) -> None:
        """Set shipping method."""
        self.shipping_option = shipping_option
        self.updated_at = datetime.now()

    def calculate_subtotal(self) -> Decimal:
        """Calculate subtotal before discounts and tax."""
        return sum(item.subtotal for item in self.items)

    def calculate_discount_amount(self) -> Decimal:
        """Calculate total discount amount."""
        subtotal = self.calculate_subtotal()
        total_discount = Decimal('0')

        for discount in self.applied_discounts:
            if discount.type == DiscountType.PERCENTAGE:
                total_discount += subtotal * (discount.value / Decimal('100'))
            elif discount.type == DiscountType.FIXED_AMOUNT:
                total_discount += discount.value
            elif discount.type == DiscountType.LOYALTY:
                # Loyalty discount based on user tier
                tier_discounts = {
                    UserTier.BRONZE: Decimal('5'),
                    UserTier.SILVER: Decimal('10'),
                    UserTier.GOLD: Decimal('15'),
                    UserTier.PLATINUM: Decimal('20'),
                }
                tier_percent = tier_discounts.get(self.user_tier, Decimal('0'))
                total_discount += subtotal * (tier_percent / Decimal('100'))

        return total_discount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def calculate_tax(self) -> Decimal:
        """Calculate tax on subtotal after discounts."""
        taxable_amount = self.calculate_subtotal() - self.calculate_discount_amount()
        tax = taxable_amount * self.tax_rate
        return tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def calculate_shipping(self) -> Decimal:
        """Calculate shipping cost."""
        if not self.shipping_option:
            return Decimal('0')
        return self.shipping_option.cost

    def calculate_total(self) -> Decimal:
        """Calculate final total including tax and shipping."""
        subtotal = self.calculate_subtotal()
        discount = self.calculate_discount_amount()
        tax = self.calculate_tax()
        shipping = self.calculate_shipping()
        total = subtotal - discount + tax + shipping
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def get_summary(self) -> Dict:
        """Get complete cart summary."""
        return {
            'items': [
                {
                    'product_id': item.product.id,
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'quantity': item.quantity,
                    'subtotal': str(item.subtotal),
                    'gift_wrap': item.gift_wrap,
                    'special_instructions': item.special_instructions
                }
                for item in self.items
            ],
            'subtotal': str(self.calculate_subtotal()),
            'discount': str(self.calculate_discount_amount()),
            'tax': str(self.calculate_tax()),
            'shipping': str(self.calculate_shipping()),
            'total': str(self.calculate_total()),
            'currency': self.currency,
            'applied_discounts': [d.code for d in self.applied_discounts],
            'user_tier': self.user_tier.value,
        }

    def to_json(self) -> str:
        """Serialize cart for persistence."""
        return json.dumps(self.get_summary(), indent=2)

    def _find_item(self, product_id: int) -> Optional[CartItem]:
        """Find cart item by product ID."""
        for item in self.items:
            if item.product.id == product_id:
                return item
        return None

    def _format_currency(self, amount: Decimal) -> str:
        """Format amount as currency string."""
        return f"${amount:.2f}"


# Example usage
if __name__ == "__main__":
    # Sample products
    laptop = Product(1, "Laptop Pro 15", Decimal('1299.99'), stock=5, max_quantity=3)
    mouse = Product(2, "Wireless Mouse", Decimal('29.99'), stock=50)
    keyboard = Product(3, "Mechanical Keyboard", Decimal('89.99'), stock=20)

    # Create cart for a Silver tier user
    cart = ShoppingCart(user_id=12345, user_tier=UserTier.SILVER)

    # Add items
    print("=== Adding Items ===")
    cart.add_item(laptop, quantity=1, gift_wrap=True)
    cart.add_item(mouse, quantity=2)
    cart.add_item(keyboard, quantity=1, special_instructions="Leave at front door")
    print(f"Items in cart: {len(cart.items)}")

    # Apply discounts
    print("\n=== Applying Discounts ===")
    loyalty_discount = Discount(
        code="LOYALTY",
        type=DiscountType.LOYALTY,
        value=Decimal('10'),  # 10% for Silver
        applicable_tiers=[UserTier.SILVER, UserTier.GOLD, UserTier.PLATINUM]
    )
    cart.apply_discount(loyalty_discount)

    promo_discount = Discount(
        code="SAVE20",
        type=DiscountType.FIXED_AMOUNT,
        value=Decimal('20'),
        min_purchase=Decimal('100')
    )
    cart.apply_discount(promo_discount)

    # Set shipping
    standard_shipping = ShippingOption(
        "standard", "Standard Shipping (5-7 days)", Decimal('9.99'), 7
    )
    cart.set_shipping(standard_shipping)

    # Display summary
    print("\n=== Cart Summary ===")
    summary = cart.get_summary()
    print(f"Subtotal: ${summary['subtotal']}")
    print(f"Discount: -${summary['discount']}")
    print(f"Tax (8%): ${summary['tax']}")
    print(f"Shipping: ${summary['shipping']}")
    print(f"Total: ${summary['total']}")
    print(f"\nApplied discounts: {', '.join(summary['applied_discounts'])}")

    # Serialize cart
    print("\n=== Serialized Cart (for persistence) ===")
    print(cart.to_json())

    # Test error handling
    print("\n=== Testing Error Handling ===")
    try:
        cart.add_item(laptop, quantity=10)  # Exceeds max_quantity
    except InvalidQuantityError as e:
        print(f"✓ Caught error: {e}")

    try:
        cart.update_quantity(999, 1)  # Non-existent product
    except CartError as e:
        print(f"✓ Caught error: {e}")

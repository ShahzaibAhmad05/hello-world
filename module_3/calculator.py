# Example 1
def calculate_order_total(items, tax_rate):
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    tax = subtotal * tax_rate
    return {'subtotal': subtotal, 'tax': tax, 'total': subtotal + tax}

# Example 2
def calculate_shipping_cost(weight, distance, priority):
    base_cost = weight * 0.5
    distance_cost = distance * 0.1
    priority_multiplier = 2.0 if priority else 1.0
    return {
        'base_cost': base_cost,
        'distance_cost': distance_cost,
        'total': (base_cost + distance_cost) * priority_multiplier
    }

# Create a similar function for:
# calculate_discount(items, loyalty_level, coupon_code)
def calculate_discount(items, loyalty_level, coupon_code):
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    
    # Loyalty discount
    if loyalty_level == 'gold':
        loyalty_discount = 0.20
    elif loyalty_level == 'silver':
        loyalty_discount = 0.10
    else:
        loyalty_discount = 0.0
    
    # Coupon discount
    if coupon_code == 'SAVE10':
        coupon_discount = 0.10
    elif coupon_code == 'SAVE20':
        coupon_discount = 0.20
    else:
        coupon_discount = 0.0
    
    total_discount_rate = loyalty_discount + coupon_discount
    total_discount = subtotal * total_discount_rate
    total_after_discount = subtotal - total_discount
    
    return {
        'subtotal': subtotal,
        'loyalty_discount': subtotal * loyalty_discount,
        'coupon_discount': subtotal * coupon_discount,
        'total_discount': total_discount,
        'total_after_discount': total_after_discount
    }

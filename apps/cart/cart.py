# apps/cart/cart.py
from decimal import Decimal
from django.conf import settings
from apps.products.models import Product

class Cart:
    def __init__(self, request):
        """Initialize the cart."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """Add a product to the cart or update its quantity."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """Mark the session as modified to ensure it gets saved."""
        self.session.modified = True

    def remove(self, product_id):
        """Remove a product from the cart by its ID."""
        product_id = str(product_id)  # Ensure correct ID usage
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Iterate over the items in the cart and get the products from the database."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])  # Ensure price is Decimal
            item['total_price'] = item['price'] * item['quantity']  # Calculate total price
            yield item

    def __len__(self):
        """Count all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate the total cost of the items in the cart."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Remove the cart from the session."""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_total_items(self):
        """Get the total number of items in the cart."""
        return len(self)

    def update(self, product, quantity):
        """Update the quantity of a product in the cart."""
        product_id = str(product.id)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.remove(product)
        self.save()
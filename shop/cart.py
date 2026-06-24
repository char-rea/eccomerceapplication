from decimal import Decimal
from shop.models import Product


class Cart:
    """
    Cart class to manage shopping cart operations using Django sessions.
    """

    def __init__(self, request):
        """
        Initialize the cart using the current user's session.

        If a cart does not already exist in the session, an empty one is created.
        """
        self.session = request.session
        cart = self.session.get('cart')

        # Create a new cart in session if it does not exist
        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.

        :param product: Product instance to be added
        :param quantity: Number of items to add
        :param update_quantity: If True, replace the quantity instead of adding
        """
        product_id = str(product.id)

        # Add product to cart if it does not exist
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)  # Store price as string for session serialization
            }

        # Update or increment product quantity
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def remove(self, product):
        """
        Remove a product from the cart.

        :param product: Product instance to be removed
        """
        product_id = str(product.id)

        # Delete product from cart if it exists
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """
        Mark the session as modified to ensure changes are saved.
        """
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over cart items and attach product objects.

        Converts prices to Decimal and calculates total price per item.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        # Attach product objects to cart items
        for product in products:
            self.cart[str(product.id)]['product'] = product

        # Yield each cart item with calculated total price
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Return the total number of items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate and return the total price of all items in the cart.
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """
        Remove the cart from the session entirely.
        """
        del self.session['cart']
        self.save()
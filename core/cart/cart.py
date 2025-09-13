from shop.models import Product
from cart.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist


class CartSession:
    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault("cart", {"items": []})

    def add_product(self, product_id, quantity=1):
        product_id = int(product_id)
        quantity = int(quantity)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return

        quantity = max(1, min(quantity, product.stock))

        for item in self._cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] = min(item["quantity"] + quantity, product.stock)
                break
        else:
            self._cart["items"].append({"product_id": product_id, "quantity": quantity})

        self.save()

    def update_product_quantity(self, product_id, quantity):
        product_id = int(product_id)
        quantity = int(quantity)
        for item in self._cart["items"]:
            if item["product_id"] == product_id:
                if quantity > 0:
                    item["quantity"] = quantity
                else:
                    self._cart["items"].remove(item)
                break
        self.save()

    def remove_product(self, product_id):
        product_id = int(product_id)
        self._cart["items"] = [
            item for item in self._cart["items"] if item["product_id"] != product_id
        ]
        self.save()

    def clear(self):
        self._cart = self.session["cart"] = {"items": []}
        self.save()

    def save(self):
        self.session.modified = True

    def get_cart_dict(self):
        """Raw session cart dict (without product objects)."""
        return self._cart

    def get_cart_items(self):
        """Return enriched cart items (with product object + total_price)."""
        items = []
        for item in self._cart["items"]:
            try:
                product_obj = Product.objects.get(
                    id=item["product_id"],
                )
                items.append(
                    {
                        "product_id": item["product_id"],
                        "quantity": item["quantity"],
                        "product_obj": product_obj,
                        "total_price": item["quantity"] * product_obj.get_price(),
                    }
                )
            except ObjectDoesNotExist:
                continue
        return items

    def get_total_payment_amount(self):
        return sum(item["total_price"] for item in self.get_cart_items())

    def get_total_quantity(self):
        return sum(item["quantity"] for item in self.get_cart_items())

    def sync_cart_items_from_db(self, user):
        """
        Load DB cart into session, but keep session priority.
        """
        cart, _ = Cart.objects.get_or_create(user=user)
        db_items = CartItem.objects.filter(cart=cart)

        session_product_ids = {item["product_id"] for item in self._cart["items"]}

        for db_item in db_items:
            if db_item.product.id not in session_product_ids:
                self._cart["items"].append(
                    {"product_id": db_item.product.id, "quantity": db_item.quantity}
                )

        self.merge_session_cart_in_db(user)
        self.save()

    def merge_session_cart_in_db(self, user):
        """
        Save session cart into DB (override DB quantities).
        """
        cart, _ = Cart.objects.get_or_create(user=user)

        session_product_ids = []
        for item in self._cart["items"]:
            try:
                product_obj = Product.objects.get(id=item["product_id"])
            except ObjectDoesNotExist:
                continue

            cart_item, _ = CartItem.objects.get_or_create(
                cart=cart, product=product_obj
            )
            cart_item.quantity = item["quantity"]
            cart_item.save()
            session_product_ids.append(product_obj.id)

        CartItem.objects.filter(cart=cart).exclude(
            product__id__in=session_product_ids
        ).delete()

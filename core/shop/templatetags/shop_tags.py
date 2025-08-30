# shop/templatetags/shop_tags.py
from django import template
from shop.models import Product

register = template.Library()


@register.inclusion_tag("shop/product_latest.html")
def show_latest_products(limit=6, category=None):
    """
    Inclusion tag to render latest products.
    :param limit: number of products to show
    :param category: optional category slug to filter
    """
    products = Product.objects.filter(is_active=True).order_by("-created_at")
    if category:
        products = products.filter(category__slug=category)

    return {"products": products[:limit]}

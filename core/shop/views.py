from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from shop.models import Product, Category, Brand


class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        brand_slug = self.request.GET.get("brand")
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)

        sort_option = self.request.GET.get("sort", "")
        if sort_option == "price_asc":
            queryset = queryset.order_by("price")
        elif sort_option == "price_desc":
            queryset = queryset.order_by("-price")
        elif sort_option == "name_asc":
            queryset = queryset.order_by("name")
        elif sort_option == "name_desc":
            queryset = queryset.order_by("-name")
        elif sort_option == "newest":
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["brands"] = Brand.objects.filter(is_active=True)
        context["search_query"] = self.request.GET.get("search", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_brand"] = self.request.GET.get("brand", "")
        context["sort_option"] = self.request.GET.get("sort", "")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_single.html"
    context_object_name = "product"

    # This tells Django to use the slug instead of the default pk lookup
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        # Only active products
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Related products: same category, excluding the current product
        context["related_products"] = (
            Product.objects.filter(category=product.category, is_active=True)
            .exclude(id=product.id)
            .order_by("-created_at")[:4]  # Limit to 4
        )

        # Add brand and category to the context for easy template access
        context["brand"] = product.brand
        context["category"] = product.category
        return context

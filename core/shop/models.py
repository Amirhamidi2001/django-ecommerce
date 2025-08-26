from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from decimal import Decimal
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class Brand(models.Model):
    """
    Brand model to represent product manufacturers or labels.
    """

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/logos/", blank=True, null=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("brand_detail", args=[self.slug])


class Category(models.Model):
    """
    Category model for organizing products.
    Supports slug URLs and optional parent category for hierarchy.
    """

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="subcategories",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
        ]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category_detail", args=[self.slug])

    @property
    def full_path(self):
        """Return full category hierarchy name."""
        names = [self.name]
        parent = self.parent
        while parent:
            names.append(parent.name)
            parent = parent.parent
        return " > ".join(reversed(names))


class Product(models.Model):
    """
    Product model for eCommerce application.
    Stores details such as name, description, price, stock,
    category, brand, and product images.
    """

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="products"
    )
    brand = models.ForeignKey(
        "Brand",
        on_delete=models.SET_NULL,
        related_name="products",
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to="products/%Y/%m/%d",
        default="products/default.jpg",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:product-single", args=[self.slug])

    def get_price(self, include_tax=False, discount=None):
        """
        Returns the final price of the product.
        :param include_tax: If True, add tax (example: 10%).
        :param discount: A Decimal or percentage (e.g., 0.1 for 10%).
        """
        final_price = Decimal(self.price)

        if discount:
            if discount < 1:
                final_price = final_price * (1 - Decimal(discount))
            else:
                final_price = final_price - Decimal(discount)

        if include_tax:
            tax_rate = Decimal("0.10")
            final_price = final_price * (1 + tax_rate)

        return final_price.quantize(Decimal("0.01"))

    @property
    def in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    """
    Stores additional images for a product.
    Each image belongs to one product.
    """

    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images"
    )
    alt = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Alternative text for SEO and accessibility.",
    )
    image = ProcessedImageField(
        upload_to="products/gallery/",
        format="JPEG",
        options={"quality": 90},
        processors=[ResizeToFill(800, 800)],
    )

    def __str__(self):
        return f"Image for {self.product.name}" if self.product else "No Product"

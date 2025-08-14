from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Category, Product, ProductImage


class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active", "created_at")
    list_filter = ("is_active", "created_at", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "Preview"


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "category",
        "brand",
        "price",
        "stock",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "category", "brand", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)
    inlines = [ProductImageInline]


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "alt", "image_preview")
    search_fields = ("product__name", "alt")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "Preview"


admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)

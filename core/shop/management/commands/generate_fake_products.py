from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
import random

from shop.models import Product, Category, Brand


class Command(BaseCommand):
    help = "🛒 Generate fake products for eCommerce testing"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Step 1: Ensure categories exist
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(
                self.style.ERROR("❌ No categories found! Please create some first.")
            )
            return

        # Step 2: Ensure brands exist
        brands = list(Brand.objects.all())
        if not brands:
            self.stdout.write(
                self.style.WARNING("⚠️ No brands found. Products will be brandless.")
            )

        # Step 3: Create products
        product_count = random.randint(30, 50)
        self.stdout.write(f"🛍️ Creating {product_count} fake products...")

        for _ in range(product_count):
            name = fake.unique.sentence(nb_words=3).replace(".", "")
            category = random.choice(categories)
            brand = random.choice(brands) if brands else None

            product = Product.objects.create(
                name=name,
                slug=slugify(name),
                category=category,
                brand=brand,
                description=fake.paragraph(nb_sentences=5),
                price=round(random.uniform(5.00, 500.00), 2),
                stock=random.randint(0, 100),
                is_active=random.choice([True, True, False]),  # 2/3 chance active
            )

        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully created {product_count} products!")
        )

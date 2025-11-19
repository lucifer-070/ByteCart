from decimal import Decimal
from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductVariant, Inventory


class Command(BaseCommand):
    help = "Load demo categories, products, variants, and inventory for manual testing."

    def handle(self, *args, **options):
        catalog = {
            "Synthesizers": [
                {
                    "name": "ACID-101 Mono Synth",
                    "slug": "acid-101-mono",
                    "price": "299.99",
                    "variants": [
                        {"sku": "ACID-101-BLK", "attrs": {"color": "black"}, "stock": 15},
                        {"sku": "ACID-101-RED", "attrs": {"color": "red"}, "stock": 5},
                    ],
                },
                {
                    "name": "Bassline 303",
                    "slug": "bassline-303",
                    "price": "399.00",
                    "variants": [
                        {"sku": "BL303-SLV", "attrs": {"color": "silver"}, "stock": 8},
                    ],
                },
            ],
            "Keyboards": [
                {
                    "name": "Alpha 61",
                    "slug": "alpha-61",
                    "price": "199.99",
                    "variants": [
                        {"sku": "ALPHA-61-BLK", "attrs": {"color": "black"}, "stock": 12},
                        {"sku": "ALPHA-61-WHT", "attrs": {"color": "white"}, "stock": 6},
                    ],
                },
                {
                    "name": "Beta 88 Hammer",
                    "slug": "beta-88-hammer",
                    "price": "549.00",
                    "variants": [
                        {"sku": "BETA-88-DARK", "attrs": {"finish": "dark wood"}, "stock": 4},
                    ],
                },
            ],
            "Drum Machines": [
                {
                    "name": "Rhythm XR-8",
                    "slug": "rhythm-xr8",
                    "price": "249.00",
                    "variants": [
                        {"sku": "XR8-STD", "attrs": {"edition": "standard"}, "stock": 10},
                        {"sku": "XR8-LTD", "attrs": {"edition": "limited"}, "stock": 3},
                    ],
                },
            ],
        }

        created_categories = 0
        created_products = 0
        created_variants = 0
        created_inventories = 0

        for cat_name, products in catalog.items():
            cat, cat_created = Category.objects.get_or_create(
                name=cat_name,
                defaults={"slug": cat_name.lower().replace(" ", "-")},
            )
            if cat_created:
                created_categories += 1

            for p in products:
                product, prod_created = Product.objects.get_or_create(
                    slug=p["slug"],
                    defaults={
                        "category": cat,
                        "name": p["name"],
                        "base_price": Decimal(p["price"]),
                        "description": f"{p['name']} for studio and live use.",
                    },
                )
                if prod_created:
                    created_products += 1

                for v in p["variants"]:
                    variant, var_created = ProductVariant.objects.get_or_create(
                        sku=v["sku"],
                        defaults={
                            "product": product,
                            "attrs": v.get("attrs", {}),
                        },
                    )
                    if var_created:
                        created_variants += 1

                    inventory, inv_created = Inventory.objects.get_or_create(
                        variant=variant,
                        defaults={"qty_available": v["stock"]},
                    )
                    if not inv_created:
                        inventory.qty_available = v["stock"]
                        inventory.save()
                    else:
                        created_inventories += 1

        self.stdout.write(self.style.SUCCESS("Demo data loaded successfully."))
        self.stdout.write(f"Categories created: {created_categories}")
        self.stdout.write(f"Products created: {created_products}")
        self.stdout.write(f"Variants created: {created_variants}")
        self.stdout.write(f"Inventories created or updated: {created_inventories}")

#!/usr/bin/env python3
"""Initialize DB + seed sneaker data."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.app import create_app
from backend.extensions import db
from backend.models import User, Category, Brand, Product, ProductVariant


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        users = [
            ("admin@sneakerstore.com", "admin123", "System Admin", "admin"),
            ("shop@sneakerstore.com", "shop123", "Shop Keeper", "shopkeeper"),
            ("staff@sneakerstore.com", "staff123", "Store Staff", "staff"),
            ("customer@sneakerstore.com", "cust123", "Alex Customer", "customer"),
        ]
        for email, pwd, name, role in users:
            u = User(email=email, full_name=name, role=role)
            u.set_password(pwd)
            db.session.add(u)

        cats = [
            ("Running", "running", "Performance running shoes"),
            ("Basketball", "basketball", "Court shoes"),
            ("Lifestyle", "lifestyle", "Everyday sneakers"),
            ("Training", "training", "Gym & training"),
            ("Skate", "skate", "Skateboarding shoes"),
        ]
        cat_map = {}
        for name, slug, desc in cats:
            c = Category(name=name, slug=slug, description=desc)
            db.session.add(c)
            cat_map[slug] = c

        brands = [
            ("Nike", "nike"),
            ("Adidas", "adidas"),
            ("Jordan", "jordan"),
            ("New Balance", "new-balance"),
            ("Puma", "puma"),
            ("Vans", "vans"),
        ]
        brand_map = {}
        for name, slug in brands:
            b = Brand(name=name, slug=slug)
            db.session.add(b)
            brand_map[slug] = b

        db.session.flush()

        # image paths are relative to Flask static folder
        products = [
            ("Air Max 90", "air-max-90", 12999, 40, "lifestyle", "nike", "9", "White/Black",
             "Classic Air Max cushioning and timeless design.",
             "/static/images/products/air-max-90.jpg"),
            ("Ultraboost 22", "ultraboost-22", 15999, 25, "running", "adidas", "10", "Core Black",
             "Energy-returning Boost midsole for daily runs.",
             "/static/images/products/ultraboost.jpg"),
            ("Air Jordan 1 Retro High", "aj1-retro-high", 18999, 15, "basketball", "jordan", "9", "Chicago",
             "Iconic high-top with premium leather.",
             "/static/images/products/jordan-1.jpg"),
            ("550 White Green", "nb-550", 11999, 30, "lifestyle", "new-balance", "8", "White/Green",
             "Retro basketball-inspired lifestyle sneaker.",
             "/static/images/products/nb-550.jpg"),
            ("RS-X Efekt", "puma-rsx", 9999, 35, "lifestyle", "puma", "10", "Black/Red",
             "Chunky silhouette with bold color blocking.",
             "/static/images/products/puma-rsx.jpg"),
            ("Old Skool", "vans-old-skool", 6999, 50, "skate", "vans", "9", "Black/White",
             "The original side-stripe skate shoe.",
             "/static/images/products/vans-old-skool.jpg"),
            ("Pegasus 40", "pegasus-40", 10999, 28, "running", "nike", "10", "Grey",
             "Reliable daily trainer with responsive cushioning.",
             "/static/images/products/pegasus.jpg"),
            ("Samba OG", "samba-og", 8999, 45, "lifestyle", "adidas", "9", "Black/White",
             "Timeless indoor soccer silhouette.",
             "/static/images/products/samba.jpg"),
            ("Dunk Low", "dunk-low", 10999, 20, "lifestyle", "nike", "8", "Panda",
             "Low-top classic with clean two-tone look.",
             "/static/images/products/dunk-low.jpg"),
            ("Metcon 9", "metcon-9", 12999, 22, "training", "nike", "11", "Black",
             "Stable training shoe for lifts and HIIT.",
             "/static/images/products/metcon.jpg"),
        ]

        for name, slug, price, stock, cat, brand, size, color, desc, image_url in products:
            # Seed three gallery slots. Replace image_url_2/image_url_3 from the admin page
            # whenever dedicated product photos are available.
            p = Product(
                name=name,
                slug=slug,
                price=price,
                stock=stock,
                category_id=cat_map[cat].id,
                brand_id=brand_map[brand].id,
                size=size,
                color=color,
                description=desc,
                image_url=image_url,
                image_url_2=image_url,
                image_url_3=image_url,
            )
            db.session.add(p)
            db.session.flush()

            # Create selectable combinations. The seeded total is distributed across
            # a few practical options while keeping the original product stock close.
            sizes = sorted({size, "8", "9", "10", "11"})
            colors = [color, "White/Black"] if color != "White/Black" else [color, "Black"]
            variant_stock = max(1, stock // (len(sizes) * len(colors)))
            p.stock = variant_stock * len(sizes) * len(colors)
            for variant_size in sizes:
                for variant_color in colors:
                    db.session.add(ProductVariant(
                        product_id=p.id,
                        size=variant_size,
                        color=variant_color,
                        stock=variant_stock,
                    ))

        db.session.commit()
        print("✅ Database seeded successfully!")
        print("   admin@sneakerstore.com / admin123")
        print("   shop@sneakerstore.com / shop123")
        print("   staff@sneakerstore.com / staff123")
        print("   customer@sneakerstore.com / cust123")


if __name__ == "__main__":
    seed()

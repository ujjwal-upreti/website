#!/usr/bin/env python3
"""One-time migration for existing Sneaky Point SQLite databases.

Run this once if database/sneakers.db was created before the product
variant/wishlist/gallery changes. New installations can run init_db.py instead.
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "database" / "sneakers.db"


def column_exists(conn, table, column):
    return any(row[1] == column for row in conn.execute(f"PRAGMA table_info({table})"))


def migrate():
    conn = sqlite3.connect(DB_PATH)
    try:
        if not column_exists(conn, "products", "image_url_2"):
            conn.execute("ALTER TABLE products ADD COLUMN image_url_2 VARCHAR(255)")
        if not column_exists(conn, "products", "image_url_3"):
            conn.execute("ALTER TABLE products ADD COLUMN image_url_3 VARCHAR(255)")
        if not column_exists(conn, "cart_items", "variant_id"):
            conn.execute("ALTER TABLE cart_items ADD COLUMN variant_id INTEGER")
        if not column_exists(conn, "order_items", "variant_id"):
            conn.execute("ALTER TABLE order_items ADD COLUMN variant_id INTEGER")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS product_variants (
                id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                size VARCHAR(20) NOT NULL,
                color VARCHAR(40) NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(product_id) REFERENCES products(id),
                UNIQUE(product_id, size, color)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wishlists (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                created_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(product_id) REFERENCES products(id),
                UNIQUE(user_id, product_id)
            )
        """)

        # Give legacy products one variant based on their old size/color fields.
        rows = conn.execute("SELECT id, size, color, stock FROM products").fetchall()
        for product_id, size, color, stock in rows:
            exists = conn.execute(
                "SELECT 1 FROM product_variants WHERE product_id=? LIMIT 1", (product_id,)
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO product_variants(product_id, size, color, stock) VALUES (?, ?, ?, ?)",
                    (product_id, size or "9", color or "Black", stock or 0),
                )
            conn.execute(
                "UPDATE products SET image_url_2=COALESCE(image_url_2, image_url), image_url_3=COALESCE(image_url_3, image_url) WHERE id=?",
                (product_id,),
            )

        conn.commit()
        print(f"Migrated {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()

from flask import Blueprint, render_template, request
from flask_login import current_user
from backend.models import Product, Category, Brand, Wishlist, ProductVariant
from backend.config import Config
from backend.extensions import db

products_bp = Blueprint("products", __name__)


@products_bp.route("/")
def list_products():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    category_slug = request.args.get("category")
    brand_slug = request.args.get("brand")
    size = request.args.get("size")

    query = Product.query.filter_by(is_active=True)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%") | Product.description.ilike(f"%{q}%"))
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    if brand_slug:
        br = Brand.query.filter_by(slug=brand_slug).first()
        if br:
            query = query.filter_by(brand_id=br.id)
    if size:
        query = query.join(Product.variants).filter(ProductVariant.size == size, ProductVariant.stock > 0).distinct()

    pagination = query.order_by(Product.name).paginate(
        page=page, per_page=Config.PRODUCTS_PER_PAGE, error_out=False
    )
    wishlist_ids = set()
    if current_user.is_authenticated:
        wishlist_ids = {
            item.product_id
            for item in Wishlist.query.filter_by(user_id=current_user.id).all()
        }
    return render_template(
        "products/list.html",
        products=pagination.items,
        pagination=pagination,
        categories=Category.query.all(),
        brands=Brand.query.all(),
        current_q=q,
        current_category=category_slug,
        current_brand=brand_slug,
        current_size=size,
        wishlist_ids=wishlist_ids,
    )


@products_bp.route("/<slug>")
def detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = (
        Product.query.filter(
            Product.brand_id == product.brand_id,
            Product.id != product.id,
            Product.is_active == True,
        ).limit(4).all()
    )
    is_wishlisted = False
    if current_user.is_authenticated:
        is_wishlisted = Wishlist.query.filter_by(
            user_id=current_user.id, product_id=product.id
        ).first() is not None
    return render_template(
        "products/detail.html",
        product=product,
        related=related,
        is_wishlisted=is_wishlisted,
        variant_data=[{"id": v.id, "size": v.size, "color": v.color, "stock": v.stock} for v in product.variants],
    )

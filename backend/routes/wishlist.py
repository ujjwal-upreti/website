from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models import Product, Wishlist

wishlist_bp = Blueprint("wishlist", __name__, url_prefix="/wishlist")


@wishlist_bp.route("/toggle/<int:product_id>", methods=["POST"])
@login_required
def toggle(product_id):
    product = Product.query.get_or_404(product_id)
    item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if item:
        db.session.delete(item)
        saved = False
    else:
        db.session.add(Wishlist(user_id=current_user.id, product_id=product.id))
        saved = True
    db.session.commit()
    return jsonify({"saved": saved})

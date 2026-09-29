from flask import Flask
from backend.config import Config
from backend.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from backend.routes.main import main_bp
    from backend.routes.auth import auth_bp
    from backend.routes.products import products_bp
    from backend.routes.cart import cart_bp
    from backend.routes.orders import orders_bp
    from backend.routes.admin import admin_bp
    from backend.routes.wishlist import wishlist_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(wishlist_bp)

    with app.app_context():
        db.create_all()

    return app

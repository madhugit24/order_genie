# app.py
from controllers.customer import customer
from controllers.menu_item import menu_item
from controllers.order_item import order_item
from controllers.order import order
from controllers.payment import payment


def register_routes(app):
    app.register_blueprint(customer, url_prefix="/customer")
    app.register_blueprint(menu_item, url_prefix="/menu_item")
    app.register_blueprint(order_item, url_prefix="/order_item")
    app.register_blueprint(order, url_prefix="/order")
    app.register_blueprint(payment, url_prefix="/payment")

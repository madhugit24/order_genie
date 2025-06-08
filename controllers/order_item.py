from datetime import datetime, timezone
from flask import request, jsonify, g
from db.models import OrderItem
from pydantic import BaseModel, ValidationError
from flask import Blueprint

order_item = Blueprint("order_item", __name__)


class OrderItemRequest(BaseModel):
    order_id: int
    menu_item_id: int
    quantity: int


class OrderItemSchema(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


class OrderItemResponse(BaseModel):
    data: list[OrderItemSchema]
    count: int


@order_item.route("/<int:order_id>", methods=["GET"])
def get_order_items(order_id):
    """
    Retrieve the order items of a given order ID.

    :param order_id: The ID of the order to retrieve the order items for.
    :return: A JSON representation of the order items if found; otherwise, an error message.
    :rtype: dict
    :statuscode 200: Order items found
    :statuscode 404: Order items not found
    """
    g.logger.debug("Fetching order items for order id: %s", order_id)
    order_items = (
        g.session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    )
    if order_items:
        order_items_list = [
            order_item_detail.__dict__ for order_item_detail in order_items
        ]
        return OrderItemResponse(
            data=order_items_list, count=len(order_items_list)
        ).model_dump_json()
    return jsonify({"data": [], "error": "Order item not found"}), 404


@order_item.route("/", methods=["POST"])
def add_order_item():
    """
    Add a new order item to the database.

    :return: The newly created order item if added; otherwise, an error message.
    :rtype: dict
    :statuscode 201: Order item created successfully
    :statuscode 400: Bad request due to validation errors
    """
    try:
        data = OrderItemRequest(**request.get_json())
        order_item = OrderItem(**data.model_dump())
        g.session.add(order_item)
        g.session.commit()
        order_item_list = [order_item.__dict__]
        return (
            OrderItemResponse(
                data=order_item_list, count=len(order_item_list)
            ).model_dump_json(),
            201,
        )
    except ValidationError as e:
        return jsonify({"data": [], "error": e.errors()}), 400


@order_item.route("/<int:order_id>", methods=["PUT"])
def update_order_item(order_id):
    """
    Update an existing order item in the database.

    :param order_id: The ID of the order item to update.
    :return: The updated order item if successful; otherwise, an error message.
    :rtype: dict
    :statuscode 200: Order item updated successfully.
    :statuscode 400: Bad request due to validation errors.
    :statuscode 404: Order item not found for update.
    """
    order_item = g.session.query(OrderItem).get(order_id)
    if order_item:
        try:
            data = OrderItem(**request.get_json())
            order_item.order_id = data.order_id
            order_item.menu_item_id = data.menu_item_id
            order_item.quantity = data.quantity
            order_item.updated_at = datetime.now(timezone.utc)
            g.session.commit()
            order_item_list = [order_item.__dict__]
            return OrderItemResponse(
                data=order_item_list, count=len(order_item_list)
            ).model_dump_json()
        except ValidationError as e:
            return jsonify({"data": [], "error": e.errors()}), 400
    return jsonify({"data": [], "error": "Order item not found for update"}), 404


@order_item.route("/<int:order_id>/<int:menu_item_id>", methods=["DELETE"])
def delete_order_item(order_id, menu_item_id):
    """
    Delete an order item from the database.

    :param order_id: The ID of the order to which the order item belongs.
    :param menu_item_id: The ID of the menu item to delete.
    :return: A JSON representation of the deleted order item if successful;
             otherwise, an error message.
    :rtype: dict
    :statuscode 200: Order item deleted successfully.
    :statuscode 404: Order item not found for delete.
    """
    order_item = (
        g.session.query(OrderItem)
        .filter_by(order_id=order_id, menu_item_id=menu_item_id)
        .first()
    )
    if order_item:
        g.session.delete(order_item)
        g.session.commit()
        return jsonify({"data": [], "message": "Order item deleted"})
    return jsonify({"data": [], "error": "Order item not found for delete"}), 404

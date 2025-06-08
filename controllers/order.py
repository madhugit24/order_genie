from flask import request, jsonify, g
from db.models import Order
from pydantic import BaseModel, ValidationError
from flask import Blueprint
from datetime import datetime, timezone

order = Blueprint("order", __name__)


class OrderRequest(BaseModel):
    customer_id: int
    order_date: datetime = datetime.now(timezone.utc)
    status: str = "PENDING"


class OrderSchema(BaseModel):
    id: int
    customer_id: int
    order_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


class OrderResponse(BaseModel):
    data: list[OrderSchema]
    count: int


@order.route("/<int:order_id>", methods=["GET"])
def get_order_detail(order_id):
    """
    Retrieve the details of an order by its ID.

    :param order_id: The ID of the order to retrieve
    :return: A JSON representation of the order details if found; otherwise, an error message.
    :rtype: dict
    :statuscode 200: Order detail found
    :statuscode 404: Order detail not found
    """
    g.logger.debug("Fetching details for order id: %s", order_id)
    order_detail = g.session.query(Order).get(order_id)
    if order_detail:
        order_detail_list = [order_detail.__dict__]
        return OrderResponse(
            data=order_detail_list, count=len(order_detail_list)
        ).model_dump_json()
    return jsonify({"data": [], "error": "Order detail not found"}), 404


@order.route("/", methods=["POST"])
def add_order_detail():
    """
    Add a new order to the database.

    :return: The newly created order details as a dictionary or an error message.
    :rtype: dict
    :statuscode 201: Order created successfully
    :statuscode 400: Bad request due to validation errors
    """
    try:
        data = OrderRequest(**request.get_json())
        order = Order(**data.model_dump())
        g.session.add(order)
        g.session.commit()
        order_detail_list = [order.__dict__]
        return (
            OrderResponse(
                data=order_detail_list, count=len(order_detail_list)
            ).model_dump_json(),
            201,
        )
    except ValidationError as e:
        return jsonify({"data": [], "error": e.errors()}), 400


@order.route("/<int:order_id>", methods=["PUT"])
def update_order_detail(order_id):
    """
    Update an existing order in the database.

    :param order_id: The ID of the order to update
    :return: The updated order details as a dictionary or an error message
    :rtype: dict
    :statuscode 200: Order updated
    :statuscode 400: Bad request due to validation errors
    :statuscode 404: Order detail not found
    """
    order = g.session.query(Order).get(order_id)
    if order:
        try:
            data = OrderRequest(**request.get_json())
            order.customer_id = data.customer_id
            order.status = data.status
            order.updated_at = datetime.now(timezone.utc)
            g.session.commit()
            order_detail_list = [order.__dict__]
            return OrderResponse(
                data=order_detail_list, count=len(order_detail_list)
            ).model_dump_json()
        except ValidationError as e:
            return jsonify({"data": [], "error": e.errors()}), 400
    return jsonify({"data": [], "error": "Order detail not found for update"}), 404

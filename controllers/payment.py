from datetime import datetime, timezone
from flask import request, jsonify, g
from db.models import PaymentTransaction
from pydantic import BaseModel, ValidationError

from flask import Blueprint

payment = Blueprint("payment", __name__)


class PaymentRequest(BaseModel):
    order_id: int
    payment_date: datetime = datetime.now(timezone.utc)
    amount: float
    payment_method: str = "OTHERS"
    paid: bool


class PaymentSchema(BaseModel):
    id: int
    order_id: int
    payment_date: datetime
    amount: float
    payment_method: str = "OTHERS"
    paid: bool = False


class PaymentResponse(BaseModel):
    data: list[PaymentSchema]
    count: int


@payment.route("/<int:order_id>", methods=["GET"])
def get_payment_status(order_id):
    """
    Retrieve the payment status for a given order ID.

    :param order_id: The ID of the order to retrieve the payment status for.
    :return: A JSON representation of the payment status if found; otherwise, an error message.
    :rtype: dict
    :statuscode 200: Payment status found
    :statuscode 404: Payment transaction not found
    """
    payment_status = g.session.query(PaymentTransaction).get(order_id)
    if payment_status:
        payment_status_list = [payment_status.__dict__]
        return PaymentResponse(
            data=payment_status_list, count=len(payment_status_list)
        ).model_dump_json()
    return jsonify({"data": [], "error": "Payment transaction not found"}), 404


@payment.route("/", methods=["POST"])
def add_payment_status():
    """
    Add a new payment status to the database.

    :param order_id: Not used
    :return: The newly created payment status
    :rtype: dict
    :statuscode 201: Payment status created
    :statuscode 400: Bad request due to validation errors
    """
    try:
        data = PaymentRequest(**request.get_json())
        payment_status = PaymentTransaction(**data.model_dump())
        g.session.add(payment_status)
        g.session.commit()
        payment_status_list = [payment_status.__dict__]
        return (
            PaymentResponse(
                data=payment_status_list, count=len(payment_status_list)
            ).model_dump_json(),
            201,
        )
    except ValidationError as e:
        return jsonify({"data": [], "error": e.errors()}), 400


@payment.route("/<int:order_id>", methods=["PUT"])
def update_payment_status(order_id):
    """
    Update the payment status for a given order ID.

    :param order_id: The ID of the order to update the payment status for.
    :return: The updated payment status if found; otherwise, an error message.
    :rtype: dict
    :statuscode 200: Payment status updated
    :statuscode 400: Bad request due to validation errors
    :statuscode 404: Payment transaction not found
    """
    payment_status = g.session.query(PaymentTransaction).get(order_id)
    if payment_status:
        try:
            data = PaymentRequest(**request.get_json())
            payment_status.order_id = data.order_id
            payment_status.amount = data.amount
            payment_status.payment_method = data.payment_method
            payment_status.paid = data.paid
            payment_status.updated_at = datetime.now(timezone.utc)
            g.session.commit()
            payment_status_list = [payment_status.__dict__]
            return PaymentResponse(
                data=payment_status_list, count=len(payment_status_list)
            ).model_dump_json()
        except ValidationError as e:
            return jsonify({"error": e.errors()}), 400
    return (
        jsonify({"data": [], "error": "Payment transaction not found for update"}),
        404,
    )

from datetime import datetime, timezone
from flask import request, jsonify, g
from db.models import Customer
from pydantic import BaseModel, ValidationError

from flask import Blueprint

customer = Blueprint("customer", __name__)


class CustomerRequest(BaseModel):
    name: str
    phone_number: str
    email: str = None


class CustomerSchema(BaseModel):
    id: int
    name: str
    phone_number: str
    email: str = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


class CustomerResponse(BaseModel):
    data: list[CustomerSchema]
    count: int


@customer.route("/", methods=["GET"])
def get_customers():
    """
    Return a list of all customers in the database.

    :param id: Not used
    :return: A list of customer dictionaries
    :rtype: dict
    :statuscode 200: Customers found
    :statuscode 404: Customers not found
    """
    customers = g.session.query(Customer).all()
    if customers:
        customers_list = [customer.__dict__ for customer in customers]
        return CustomerResponse(
            data=customers_list, count=len(customers_list)
        ).model_dump_json()
    return jsonify({"data": [], "error": "Customers not found"}), 404


@customer.route("/<int:id>", methods=["GET"])
def get_customer(id):
    """
    Return a customer by id.

    :param id: The id of the customer to retrieve
    :return: A customer dictionary
    :rtype: dict
    :statuscode 200: Customer found
    :statuscode 404: Customer not found
    """
    g.logger.debug("Fetching details for Customer id: %s", id)
    customer = g.session.query(Customer).get(id)
    if customer:
        customer_list = [customer.__dict__]
        return CustomerResponse(
            data=customer_list, count=len(customer_list)
        ).model_dump_json()
    return jsonify({"data": [], "error": "Customer not found"}), 404


@customer.route("/", methods=["POST"])
def add_customer():
    """
    Add a customer to the database.

    :param id: Not used
    :return: The newly created customer
    :rtype: dict
    :statuscode 201: Customer created
    :statuscode 400: Bad request
    """
    try:
        data = CustomerRequest(**request.get_json())
        customer = Customer(**data.model_dump())
        g.session.add(customer)
        g.session.commit()
        customer_list = [customer.__dict__]
        return (
            CustomerResponse(
                data=customer_list, count=len(customer_list)
            ).model_dump_json(),
            201,
        )
    except ValidationError as e:
        return jsonify({"data": [], "error": e.errors()}), 400


@customer.route("/<int:id>", methods=["PUT"])
def update_customer(id):
    """
    Update an existing customer in the database.

    :param id: The id of the customer to update
    :return: The updated customer dictionary or an error message
    :rtype: dict
    :statuscode 200: Customer updated
    :statuscode 400: Bad request due to validation errors
    :statuscode 404: Customer not found
    """
    customer = g.session.query(Customer).get(id)
    if customer:
        try:
            data = CustomerRequest(**request.get_json())
            customer.name = data.name
            customer.phone_number = data.phone_number
            customer.email = data.email
            customer.updated_at = datetime.now(timezone.utc)
            g.session.commit()
            customer_list = [customer.__dict__]
            return CustomerResponse(
                data=customer_list, count=len(customer_list)
            ).model_dump_json()
        except ValidationError as e:
            return jsonify({"data": [], "error": e.errors()}), 400
    return jsonify({"data": [], "error": "Customer not found for update"}), 404


@customer.route("/<int:id>", methods=["DELETE"])
def delete_customer(id):
    """
    Delete a customer from the database by id.

    :param id: The id of the customer to delete
    :return: A success message or an error message
    :rtype: dict
    :statuscode 200: Customer deleted
    :statuscode 404: Customer not found
    """

    customer = g.session.query(Customer).get(id)
    if customer:
        g.session.delete(customer)
        g.session.commit()
        return jsonify({"data": [], "message": "Customer deleted"})
    return jsonify({"data": [], "error": "Customer not found for delete"}), 404

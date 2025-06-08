from datetime import datetime, timezone
from flask import request, jsonify, g
from sqlalchemy import func
from db.models import MenuItem
from pydantic import BaseModel, ValidationError
from pydantic import BaseModel
from flask import Blueprint

menu_item = Blueprint("menu_item", __name__)


class MenuItemRequest(BaseModel):
    active: bool
    name: str
    description: str = None
    price: float


class MenuItemSchema(BaseModel):
    id: int
    name: str
    description: str
    price: float
    active: bool
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


class MenuItemResponse(BaseModel):
    data: list[MenuItemSchema]
    count: int


@menu_item.route("/", methods=["GET"])
def get_menu_items():
    """
    Retrieve all menu items from the database.

    :return: A list of all menu items or an error message
    :rtype: dict
    :statuscode 200: Returns a list of menu items
    :statuscode 404: Menu items not found
    """

    menu_items = g.session.query(MenuItem).filter(MenuItem.active).all()
    if menu_items:
        menu_items_list = [menu_item.__dict__ for menu_item in menu_items]
        return MenuItemResponse(
            data=menu_items_list, count=len(menu_items_list)
        ).model_dump_json()
    return jsonify({"data": [], "error": "Menu items not found"}), 404


@menu_item.route("/<string:item_name>", methods=["GET"])
def get_menu_item_details(item_name):
    """
    Retrieve details of a menu item by name.

    :param item_name: The name of the menu item to retrieve
    :return: A menu item dictionary or an error message
    :rtype: dict
    :statuscode 200: Menu item found
    :statuscode 404: Menu item detail not found
    """

    g.logger.debug("Fetching details for menu item: %s", item_name)
    menu_item_details = (
        g.session.query(MenuItem)
        .filter(func.lower(MenuItem.name) == func.lower(item_name))
        .first()
    )
    if menu_item_details:
        menu_item_detail_list = [menu_item_details.__dict__]
        return MenuItemResponse(
            data=menu_item_detail_list, count=len(menu_item_detail_list)
        ).model_dump_json()
    return jsonify({"data": [], "error": "Menu item detail not found"}), 404


@menu_item.route("/", methods=["POST"])
def add_menu_item():
    """
    Add a new menu item to the database.

    :return: The newly created menu item dictionary or an error message
    :rtype: dict
    :statuscode 201: Menu item created successfully
    :statuscode 400: Bad request due to validation errors
    """

    try:
        data = MenuItemRequest(**request.get_json())
        menu_item_detail = MenuItem(**data.model_dump())
        g.session.add(menu_item_detail)
        g.session.commit()
        menu_item_detail_list = [menu_item_detail.__dict__]
        return (
            MenuItemResponse(
                data=menu_item_detail_list, count=len(menu_item_detail_list)
            ).model_dump_json(),
            201,
        )
    except ValidationError as e:
        return jsonify({"data": [], "error": e.errors()}), 400


@menu_item.route("/<string:item_name>", methods=["PUT"])
def update_menu_item(item_name):
    """
    Update the details of a menu item.

    :param item_name: The name of the menu item to update
    :return: The updated menu item dictionary or an error message
    :rtype: dict
    :statuscode 200: Menu item updated successfully
    :statuscode 400: Bad request due to validation errors
    :statuscode 404: Menu item detail not found for update
    """
    menu_item_detail = (
        g.session.query(MenuItem)
        .filter(func.lower(MenuItem.name) == func.lower(item_name))
        .first()
    )
    if menu_item_detail:
        try:
            data = MenuItemRequest(**request.get_json())
            menu_item_detail.name = data.name
            menu_item_detail.description = data.description
            menu_item_detail.price = data.price
            menu_item_detail.active = data.active
            menu_item_detail.updated_at = datetime.now(timezone.utc)
            g.session.commit()
            menu_item_detail_list = [menu_item_detail.__dict__]
            return MenuItemResponse(
                data=menu_item_detail_list, count=len(menu_item_detail_list)
            ).model_dump_json()
        except ValidationError as e:
            return jsonify({"data": [], "error": e.errors()}), 400
    return jsonify({"data": [], "error": "Menu item detail not found for update"}), 404

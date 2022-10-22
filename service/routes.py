"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, abort
from service.models import DataValidationError, Inventory, Condition
from .common import status  # HTTP Status Codes


# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """
    Root URL response
    This sends a basic list of endpoints available from the Flask App
    """
    routes = {}
    for r in app.url_map._rules:
        routes[r.rule] = {}
        routes[r.rule]["functionName"] = r.endpoint
        routes[r.rule]["methods"] = list(r.methods)
    routes.pop("/static/<path:filename>")

    return (
        jsonify(name="Inventory Service REST API", version="1.0", paths=routes),
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL INVENTORY ITEMS
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Returns all of the inventory"""
    app.logger.info("Request for inventory list")
    inventory = Inventory.all()
    results = [inventory_item.serialize() for inventory_item in inventory]
    app.logger.info(results)

    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE AN INVENTORY ITEM
######################################################################
@app.route("/inventory/pid/<int:pid>/condition/<int:condition_id>", methods=["GET"])
def get_inventory(pid, condition_id):
    """
    Retrieve a single inventory item

    This endpoint will return an inventory item based on it's id
    """

    app.logger.info("Request for inventory item with id: %s and condition %s", pid, condition_id)
    if Condition.has_value(condition_id) is False:
        app.logger.info("Condition %s not in value map", condition_id)
        abort(status.HTTP_400_BAD_REQUEST, "Condition id not supported")
    inventory = Inventory.find_by_pid_condition(pid, Condition(condition_id))
    if not inventory:
        abort(status.HTTP_404_NOT_FOUND, f"Inventory with id '{pid}' and condition '{Condition(condition_id)}' was not found.")

    app.logger.info("Returning inventory: %s", inventory.pid)
    return jsonify(inventory.serialize()), status.HTTP_200_OK


######################################################################
# ADD A NEW INVENTORY ITEM
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Creates an inventory item
    This endpoint will create an inventory item based the data in the body that is posted
    """
    check_content_type("application/json")
    app.logger.info("Request to create inventory item")
    payload = request.get_json()
    try:
        pid = payload["pid"]
    except KeyError:
        app.logger.info("Payload has missing pid")
        abort(status.HTTP_400_BAD_REQUEST, "Missing pid in request")
    try:
        condition_id = payload["condition"]
    except KeyError:
        app.logger.info("Payload has missing condition id")
        abort(status.HTTP_400_BAD_REQUEST, "Missing condition id in request")

    app.logger.info(
        "Request details are id: %s and condition id %s",
        pid,
        condition_id,
    )
    # Check if Condition ID is in range of values, or if PID is integer or not
    if Condition.has_value(condition_id) is False :
        app.logger.info("Condition %d not in value map", condition_id)
        abort(status.HTTP_400_BAD_REQUEST, "Condition id not supported")
    if not isinstance(pid, int):
        app.logger.info("Product id %d is not an integer", pid)
        abort(status.HTTP_400_BAD_REQUEST, "Product id not supported")

    item = Inventory.find_by_pid_condition(pid=pid, condition=Condition(condition_id))

    if item is not None:
        abort(
            status.HTTP_409_CONFLICT,
            f"Item with Product ID '{pid}' and Condition '{Condition(condition_id)}' already exists",
        )

    try:
        item = Inventory(pid, Condition(condition_id),None, None, None, None)
        item.deserialize(request.get_json())
        item.create()
    except DataValidationError as err:
        abort(status.HTTP_400_BAD_REQUEST, err)

    return item.serialize(), status.HTTP_201_CREATED


######################################################################
# UPDATE AN EXISTING INVENTORY ITEM
######################################################################
@app.route("/inventory/pid/<int:pid>/condition/<int:condition_id>", methods=["PUT"])
def update_inventory(pid, condition_id):
    """
    Update an inventory item

    This endpoint will update an inventory item based the body that is posted
    """
    app.logger.info(
        "Request to update inventory item with id: %s and condition id",
        pid,
        condition_id,
    )
    check_content_type("application/json")
    if Condition.has_value(condition_id) is False:
        app.logger.info("Condition %s not in value map", condition_id)
        abort(status.HTTP_400_BAD_REQUEST, "Condition id not supported")

    item = Inventory.find_by_pid_condition(pid=pid, condition=Condition(condition_id))
    if item is None:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with Product ID '{pid}' and Condition '{Condition(condition_id)}' not found",
        )

    try:
        item.deserialize(request.get_json())
        item.pid = pid
        item.condition = Condition(condition_id)
        item.update()
    except DataValidationError as err:
        abort(status.HTTP_400_BAD_REQUEST, err)

    return item.serialize(), status.HTTP_200_OK


######################################################################
# DELETE A INVENTORY ITEM
######################################################################
@app.route("/inventory/pid/<int:pid>/condition/<int:condition>", methods=["DELETE"])
def delete_inventory(pid, condition):
    """
    Delete an inventory item

    This endpoint will delete an inventory item based the id specified in the path
    """
    if Condition.has_value(condition) is True:
        app.logger.info(
            "Request to delete inventory item with pid: %s and condition: %s",
            pid,
            Condition(condition),
        )
        item = Inventory.find_by_pid_condition(pid, Condition(condition))
        if item:
            item.delete()
        app.logger.info(
            "Inventory item with pid: %s and condition: %s successfully deleted",
            pid,
            Condition(condition),
        )
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """Initializes the SQLAlchemy app"""
    global app
    Inventory.init_db(app)


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )

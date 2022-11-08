""" Inventory Routes """

from flask import jsonify, request, abort, url_for
from service.models import Inventory, Condition
from .common import status

from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response sends a basic list of endpoints available from the Flask App """
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Inventory Service REST API",
            version="1.0",
            paths =url_for("list_inventory", _external=True)
            ),
        status.HTTP_200_OK
    )


######################################################################
# LIST ALL INVENTORY ITEMS
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Returns all of the items in the Inventory"""
    app.logger.info("Request for Inventory list")
    inventory = Inventory.all()
    results = [item.serialize() for item in inventory]
    app.logger.info("Returning %d items", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE AN INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:pid>", methods=["GET"])
def get_inventory(pid):
    """ Retrieves a single Inventory item """
    results = []
    condition = request.args.get("condition")
    if condition:
        app.logger.info(f"Request for item {pid} with condition {condition}")
        results = Inventory.find_by_pid_condition(pid, Condition(int(condition)))
    else:
        app.logger.info(f"Request for item {pid}")
        results = Inventory.find_by_pid(pid)

    items = [item.serialize() for item in results]
    if not items:
        message = f"No items could be found for ID: {pid}"
        if condition:
            message += f" with condition: {condition}"
        app.logger.info(message)
        abort(status.HTTP_404_NOT_FOUND, message)

    app.logger.info("Returning %d Inventory items", len(items))
    return jsonify(items), status.HTTP_200_OK


######################################################################
# CREATE A NEW INVENTORY ITEM
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """ Creates an Inventory item """
    app.logger.info("Request to create an Inventory item")
    check_content_type("application/json")
    item = Inventory(pid = -100, condition = Condition(0))
    arguments = request.get_json()
    item = item.deserialize(arguments)
    item.create()
    location_url = url_for("get_inventory", pid=item.pid,
        condition=item.condition.value, _external=True)

    app.logger.info(
        "Inventory item with PID [%s] and condition [%s] created", item.pid, item.condition.name)
    return jsonify(item.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:pid>", methods=["PUT"])
def update_inventory(pid):
    """ Updates an Inventory item """
    app.logger.info("Request to update Inventory item with PID: %s", pid)
    check_content_type("application/json")
    arguments = []
    arguments = request.get_json()

    try:
        condition = Condition(arguments["condition"])
    except ValueError:
        abort(status.HTTP_404_NOT_FOUND, f"Condition {arguments['condition']} is invalid")

    items = []
    items = Inventory.find_by_pid_condition(pid, condition)

    if not items:
        abort(status.HTTP_404_NOT_FOUND,
        f"Item with PID '{pid}' and condition {condition.name} does not exist")

    item = items[0].deserialize(request.get_json())
    item.update()
    location_url = url_for("get_inventory", pid=pid, condition=condition, _external=True)
    app.logger.info("Inventory item with PID [%s] and condition [%s] updated", pid, condition.name)
    return jsonify(item.serialize()), status.HTTP_200_OK, {"Location": location_url}


######################################################################
# DELETE A INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:pid>", methods=["DELETE"])
def delete_inventory(pid):
    """ Delete an Inventory item"""
    app.logger.info("Request to delete Inventory item with PID: %s", pid)
    arguments = []
    arguments = request.get_json()

    message = f"Inventory item with PID {pid}"

    try:
        condition = Condition(arguments["condition"])
        item = Inventory.find_by_pid_condition(pid, condition)
        message += f" and Condition: {condition}"
    except ValueError:
        item = Inventory.find_by_pid(pid)

    if item:
        item.delete()
        message += " deleted"
        app.logger.info(message)

    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """Initializes the SQLAlchemy app"""
    # pylint: disable=global-variable-not-assigned
    # pylint: disable=invalid-name
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

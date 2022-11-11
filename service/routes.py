""" Inventory Routes """

from flask import jsonify, request, abort, url_for
from service.models import Inventory, Condition # DataValidationError
from .common import status  # HTTP Status Codes

from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response sends a basic list of endpoints available from the Flask App """
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
    inventory = Inventory.all()
    results = [item.serialize() for item in inventory]
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
        results = Inventory.find_by_pid_condition(pid, condition)
    else:
        results = Inventory.find_by_pid(pid)

    items = [item.serialize() for item in results]

    if not items:
        abort(status.HTTP_404_NOT_FOUND)

    return jsonify(items), status.HTTP_200_OK


######################################################################
# CREATE A NEW INVENTORY ITEM
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """ Creates an Inventory item """

    item = Inventory(pid = -100, condition = Condition(0))
    arguments = []
    arguments = request.get_json()
    item = item.deserialize(arguments)
    item.create()
    location_url = url_for("get_inventory", pid=item.pid,
        condition=item.condition.name, _external=True)

    return jsonify(item.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:pid>", methods=["PUT"])
def update_inventory(pid):
    """ Updates an Inventory item """
    arguments = []
    arguments = request.get_json()

    try:
        condition = Condition(arguments["condition"])
    except ValueError:
        abort(status.HTTP_404_NOT_FOUND)

    items = []
    items = Inventory.find_by_pid_condition(pid, condition)

    item = items[0].deserialize(request.get_json())
    item.update()
    location_url = url_for("get_inventory", pid=pid, condition=condition, _external=True)
    return jsonify(item.serialize()), status.HTTP_200_OK, {"Location": location_url}


######################################################################
# DELETE A INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:pid>", methods=["DELETE"])
def delete_inventory(pid):
    """ Delete an Inventory item"""
    arguments = []
    arguments = request.get_json()

    try:
        condition = Condition(arguments["condition"])
    except ValueError:
        abort(status.HTTP_404_NOT_FOUND)

    item = Inventory.find_by_pid_condition(pid, condition)
    if item:
        item.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# HEALTH CHECK FOR APP
######################################################################
@app.route("/health", methods=["GET"])
def health():
    """Get Shallow Health of the current Service"""
    return jsonify(status="OK"),status.HTTP_200_OK

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """Initializes the SQLAlchemy app"""
    global app
    Inventory.init_db(app)

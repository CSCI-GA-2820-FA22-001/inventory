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
    """Returns a list of the items in the Inventory"""
    app.logger.info("Request for Inventory list")

    pid = request.args.get("pid")
    condition = request.args.get("condition")
    active = request.args.get("active")

    if pid:
        app.logger.info("filtered by pid")
        items = Inventory.find_by_pid(pid)
    elif condition:
        app.logger.info("filtered by condition")
        items = Inventory.find_by_condition(condition)
    elif active:
        app.logger.info("filtered by active")
        active = active in ["true", "True", "TRUE"]
        items = Inventory.find_by_active(active)
    else:
        app.logger.info("find all")
        items = Inventory.all()

    results = [item.serialize() for item in items]
    app.logger.info("Returning %d items", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE AN INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:pid>", methods=["GET"])
def get_inventory(pid):
    """ Retrieves Inventory items """

    condition = None
    condition = request.args.get("condition")
    if condition:
        app.logger.info(f"Request for item {pid} with condition {condition}")
        results = Inventory.find_by_pid_condition(pid, condition)

        if not results:
            message = f"No items could be found for PID: {pid} and Condition {condition}"
            app.logger.info(message)
            abort(status.HTTP_404_NOT_FOUND, message)

        items = results.serialize()

    else:
        app.logger.info(f"Request for items with {pid}")
        results = Inventory.find_by_pid(pid)

        if results.count() == 0:
            message = f"No items could be found for PID: {pid}"
            app.logger.info(message)
            abort(status.HTTP_404_NOT_FOUND, message)

        items = [item.serialize() for item in results]


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
    arguments = request.get_json()

    item = Inventory.find_by_pid_condition(arguments["pid"], arguments["condition"])

    if item:
        abort(status.HTTP_409_CONFLICT,
        f"Item with PID {arguments['pid']} and condition {arguments['condition']} already exists")

    item = Inventory(pid = -100, condition = Condition(0))
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
    arguments = request.get_json()

    item = Inventory.find_by_pid_condition(pid, arguments["condition"])

    if not item:
        abort(status.HTTP_404_NOT_FOUND,
        f"Item with PID '{pid}' and condition {arguments['condition']} does not exist")

    item = item.deserialize(request.get_json())
    item.update()

    app.logger.info(f"Inventory item with PID {pid} and condition {arguments['condition']} updated")
    return jsonify(item.serialize()), status.HTTP_200_OK

######################################################################
# DELETE INVENTORY ITEMS BY PID
######################################################################
@app.route("/inventory/<int:pid>", methods=["DELETE"])
def delete_inventory_pid(pid):
    """ Delete an Inventory item"""
    app.logger.info("Request to delete all Inventory items with PID: %s", pid)


    items = Inventory.find_by_pid(pid)
    if items.count() != 0:
        for i in items:
            i.delete()

        app.logger.info(f"All Inventory items with PID {pid} deleted")

    return "", status.HTTP_204_NO_CONTENT

######################################################################
# DELETE A SINGLE INVENTORY ITEM
######################################################################


@app.route("/inventory/<int:pid>/<int:condition>", methods=["DELETE"])
def delete_inventory_pid_condition(pid, condition):
    """ Delete an Inventory item"""
    app.logger.info(f"Request to delete Inventory item with PID: {pid} and Condition {condition}")

    item = Inventory.find_by_pid_condition(pid, condition)
    if item:
        item.delete()
        app.logger.info(f"Inventory item with PID {pid}"
        f" and Condition {condition} deleted")

        app.logger.info(f"All Inventory items with PID: {pid} and Condition {condition} deleted")

    return "", status.HTTP_204_NO_CONTENT



############################################################
# ACTIVATE
############################################################

@app.route("/inventory/activate/<int:pid>/<int:condition>", methods=["PUT"])
def activate_inventory(pid, condition):
    """ Activates an Inventory item """

    app.logger.info(f"Request to activate item with PID {pid} and condition {condition}")

    item = Inventory.find_by_pid_condition(pid, condition)
    if not item:
        abort(status.HTTP_404_NOT_FOUND,
              f"Item with PID {pid} and Condition {condition} not found.")

    item.activate()
    app.logger.info(f"Item with PID {pid}: active status is set to true.")
    return jsonify(item.serialize()), status.HTTP_200_OK


############################################################
# DE-ACTIVATE
############################################################
@app.route("/inventory/deactivate/<int:pid>/<int:condition>", methods=["PUT"])
def deactivate_inventory(pid, condition):
    """ Dectivates an Inventory item """

    app.logger.info(f"Request to activate item with PID {pid} and condition {condition}")

    item = Inventory.find_by_pid_condition(pid, condition)
    if not item:
        abort(status.HTTP_404_NOT_FOUND,
              f"Item with PID {pid} and Condition {condition} not found.")

    item.deactivate()
    app.logger.info(f"Item with PID {pid}: active status is set to true.")
    return jsonify(item.serialize()), status.HTTP_200_OK



######################################################################
# HEALTH CHECK
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

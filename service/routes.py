"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from .common import status  # HTTP Status Codes
from service.models import Inventory

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL INVENTORY ITEMS
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Returns all of the inventory"""
    app.logger.info("Request for inventory list")
    return {}, status.HTTP_200_OK


######################################################################
# RETRIEVE AN INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory(item_id):
    """
    Retrieve a single inventory item

    This endpoint will return an inventory item based on it's id
    """
    app.logger.info("Request for inventory item with id: %s", item_id)
    return {}, status.HTTP_200_OK


######################################################################
# ADD A NEW INVENTORY ITEM
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Creates an inventory item
    This endpoint will create an inventory item based the data in the body that is posted
    """
    app.logger.info("Request to create an inventory item")
    return {}, status.HTTP_201_CREATED, {"Location": "location_url"}


######################################################################
# UPDATE AN EXISTING INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:item_id>", methods=["PUT"])
def update_inventory(item_id):
    """
    Update an inventory item

    This endpoint will update an inventory item based the body that is posted
    """
    app.logger.info("Request to update inventory item with id: %s", item_id)
    return {}, status.HTTP_200_OK


######################################################################
# DELETE A INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory(item_id):
    """
    Delete an inventory item

    This endpoint will delete an inventory item based the id specified in the path
    """
    app.logger.info("Request to delete inventory item with id: %s", item_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Inventory.init_db(app)

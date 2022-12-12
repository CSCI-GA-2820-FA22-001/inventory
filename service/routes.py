""" Inventory Routes """

from flask import jsonify, request, abort, url_for
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import Inventory, Condition
from .common import status

from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response sends a basic list of endpoints available from the Flask App"""
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")
    
######################################################################
# Configure Swagger before initializing it
######################################################################

api = Api(app,
          version='1.0.0',
          title='Inventory REST API Service',
          description='This is an Inventory server.',
          default='inventory',
          default_label='Inventory operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
          prefix='/'
         )

#Define the create model so that the docs define what can be sent
create_model = api.model(
    'Inventory',
    {
        'condition': fields.Integer(description='The type of inventory [NEW | OPEN | USED]'),  #this may be wrong 
        'name': fields.String(
            required=False, 
            description='The name of Inventory'
        ),
        'quantity': fields.Integer(
            required=False,
            description='The quantity of the Inventory',
        ),
        'restock_level': fields.Integer(
            required=False, description='The restock level of the inventory'
        ),
        'active': fields.Boolean(required=False,
                                description='Is the inventory active?')
    }
)

inventory_model = api.inherit(
    'InventoryModel',
    create_model,
    {
        'pid': fields.Integer(
            readOnly=True, description='The unique id assigned internally by service'
        ),
    },
)

# query string arguments
# --------------------------------------------------------------------------------------------------
inventory_args = reqparse.RequestParser()
inventory_args.add_argument('condition', type=int, required=True, location='args', help='The type of inventory [NEW | OPEN | USED]')
inventory_args.add_argument('name', type=str, required=False, location='args', help='The name of Inventory')
inventory_args.add_argument('quantity', type=int, required=False, location='args', help='The quantity of the Inventory')
inventory_args.add_argument('restock_level', type=int, required=False, location='args', help='The restock level of the inventory')
inventory_args.add_argument('active', type=inputs.boolean, required=False, location='args', help='List inventorys by active status')





######################################################################
#  PATH: /inventory
######################################################################

@api.route('/inventory', strict_slashes=False)
class InventoryCollection(Resource):
    """ Handles all interactions with collections of inventory """

    # ------------------------------------------------------------------
    # LIST ALL inventory
    # ------------------------------------------------------------------
    @api.doc('list_inventory')
    @api.expect(inventory_args, validate=True)
    @api.marshal_list_with(inventory_model)
    def get(self):
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
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A NEW INVENTORY ITEM
    # ------------------------------------------------------------------

    @api.doc('create_inventory')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """Creates an Inventory item"""
        app.logger.info("Request to create an Inventory item")
        check_content_type("application/json")
        arguments = api.payload

        item = Inventory.find_by_pid_condition(arguments["pid"], arguments["condition"])

        if item:
            abort(
                status.HTTP_409_CONFLICT,
                f"Item with PID {arguments['pid']} and condition {arguments['condition']} already exists",
            )

        item = Inventory(pid=-100, condition=Condition(0))
        item = item.deserialize(arguments)
        item.create()
        location_url = url_for(
            "inventory_resource", pid=item.pid, condition=item.condition.value, _external=True
        )

        app.logger.info(
            "Inventory item with PID [%s] and condition [%s] created",
            item.pid,
            item.condition.name,
        )
        return (
            item.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )

######################################################################
# PATH /inventory/{inventory}
######################################################################
@api.route('/inventory/<int:pid>')
@api.param('pid', 'The Inventory identifier')
class InventoryResource(Resource):
    """
    InventoryResource class
    Allows the manipulation of a single inventory
    GET /inventory{id} - Returns a inventory with the id
    PUT /inventory{id} - Update a inventory with the id
    DELETE /inventory{id} -  Deletes a inventory with the id
    """
    #------------------------------------------------------------------
    # RETRIEVE A inventory
    #------------------------------------------------------------------
    @api.doc('get_inventory')
    @api.response(404, 'inventory not found')
    @api.marshal_with(inventory_model)
    def get(self, pid):
        """Retrieves Inventory items"""

        condition = None
        condition = request.args.get("condition")
        if condition:
            app.logger.info(f"Request for item {pid} with condition {condition}")
            results = Inventory.find_by_pid_condition(pid, condition)

            if not results:
                message = (
                    f"No items could be found for PID: {pid} and Condition {condition}"
                )
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
        return items, status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING INVENTORY ITEM
    #------------------------------------------------------------------

    @api.doc('update_inventory')
    @api.response(404, 'Inventory not found')
    @api.response(400, 'The posted Inventory data was not valid')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, pid):
        
        """Updates an Inventory item"""
        app.logger.info("Request to update Inventory item with PID: %s", pid)
        check_content_type("application/json")
        arguments = api.payload

        item = Inventory.find_by_pid_condition(pid, arguments["condition"])

        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with PID '{pid}' and condition {arguments['condition']} does not exist",
            )

        item = item.deserialize(api.payload)
        item.update()

        app.logger.info(
            f"Inventory item with PID {pid} and condition {arguments['condition']} updated"
        )
        return item.serialize(), status.HTTP_200_OK


    #------------------------------------------------------------------
    # DELETE A INVENTORY
    #------------------------------------------------------------------
    @api.doc('delete_inventory_pid')
    @api.response(204, 'Inventory deleted')
    def delete(self, pid):
        """Delete an Inventory item"""
        app.logger.info("Request to delete all Inventory items with PID: %s", pid)

        items = Inventory.find_by_pid(pid)
        if items.count() != 0:
            for i in items:
                i.delete()

            app.logger.info(f"All Inventory items with PID {pid} deleted")

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# PATH /inventory/<int:pid>/<int:condition>
######################################################################
@api.route('/inventory/<int:pid>/<int:condition>')
@api.param('pid', 'The Inventory identifier')
@api.param('condition', 'The Inventory Condition identifier')
class InventoryDelResource(Resource):
    """
    InventoryDelResource class
   
    DELETE /InventoryDel{pid,condition} -  Deletes a Inventory with id and condition 
    """
    #------------------------------------------------------------------
    # Delete a inventory based on pid and condition
    #------------------------------------------------------------------
    @api.doc('delete_inventory_pid_condition')
    @api.response(404, 'Inventory not found')
    @api.marshal_with(inventory_model)
    def delete(self, pid, condition):
        """Delete an Inventory item"""
        app.logger.info(
            f"Request to delete Inventory item with PID: {pid} and Condition {condition}"
        )

        item = Inventory.find_by_pid_condition(pid, condition)
        if item:
            item.delete()
            app.logger.info(
                f"Inventory item with PID {pid}" f" and Condition {condition} deleted"
            )

            app.logger.info(
                f"All Inventory items with PID: {pid} and Condition {condition} deleted"
            )

        return "", status.HTTP_204_NO_CONTENT




######################################################################
# PATH /inventory/activate/<int:pid>/<int:condition>
######################################################################
@api.route('/inventory/activate/<int:pid>/<int:condition>')
@api.param('pid', 'The Inventory identifier')
@api.param('condition', 'The Inventory Condition identifier')
class ActivateResource(Resource):
    "Activate action for a Inventory"
    @api.doc('activate_inventory')
    def put(self, pid, condition):
        """Activates an Inventory item"""

        app.logger.info(
            f"Request to activate item with PID {pid} and condition {condition}"
        )

        item = Inventory.find_by_pid_condition(pid, condition)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with PID {pid} and Condition {condition} not found.",
            )

        item.activate()
        app.logger.info(f"Item with PID {pid}: active status is set to true.")
        return item.serialize(), status.HTTP_200_OK


######################################################################
# PATH /inventory/deactivate/<int:pid>/<int:condition>
######################################################################
@api.route('/inventory/deactivate/<int:pid>/<int:condition>')
@api.param('pid', 'The Inventory identifier')
@api.param('condition', 'The Inventory Condition identifier')
class DeactivateResource(Resource):
    "Deactivate action for a Inventory"
    @api.doc('deactivate_inventory')
    def put(self, pid, condition):
        """Dectivates an Inventory item"""

        app.logger.info(
            f"Request to activate item with PID {pid} and condition {condition}"
        )

        item = Inventory.find_by_pid_condition(pid, condition)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with PID {pid} and Condition {condition} not found.",
            )

        item.deactivate()
        app.logger.info(f"Item with PID {pid}: active status is set to true.")
        return item.serialize(), status.HTTP_200_OK



######################################################################
# HEALTH CHECK
######################################################################

@app.route("/health", methods=["GET"])
def health():
    """Get Shallow Health of the current Service"""
    return jsonify(status="OK"), status.HTTP_200_OK


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

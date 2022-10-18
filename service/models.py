"""
Models for Inventory

All of the models are stored in this module
"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Inventory.init_db(app)

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

class Condition(Enum):
    """Enumeration of different product conditions"""
    NEW = 0
    OLD = 1
    USED = 2


class Inventory(db.Model):
    """
    Class that represents a Inventory
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.String(63), primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    restock_level = db.Column(db.Integer)
    minimum_amount = db.Column(db.Integer)
    

    def __init__(self, id:int, name: str, quantity: int, restock_level: int, minimum_amount: int):
        """Constructor for Item in Inventory""" 
        self.id = id
        self.name = name
        self.quantity = quantity
        self.restock_level = restock_level
        self.minimum_amount = minimum_amount

    def __repr__(self):
        return "<Inventory Item id=[%s], Item name=[%s], Item Quantity=[%s], Item Description=[%s]>" % (self.id, self.name, self.quantity, self.description)

    def create(self):
        """
        Creates an Item in the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Item to the database
        """
        if(self.id is None):
            raise DataValidationError("No ID present for item in update")# Should not update an item with no ID
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Inventory from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Inventory into a dictionary """
        return {"id": self.id, "name": self.name, "quantity": self.quantity, "description": self.description}

    def deserialize(self, data):
        """
        Deserializes a Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.quantity = data["quantity"]
            self.description = data["description"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Inventory: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Inventory: body of request contained bad or no data - "
                "Error message: " + error
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Inventory in the database """
        logger.info("Processing all Inventory")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Inventory by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Inventory with the given name

        Args:
            name (string): the name of the Inventory you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

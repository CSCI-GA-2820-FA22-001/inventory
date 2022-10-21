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
    """Used for an data validation errors when deserializing"""


class Condition(Enum):
    """Enumeration of different product conditions"""

    NEW = 0
    USED = 1
    OPEN_BOX = 2

    @classmethod
    def has_value(cls, condition_id):
        return condition_id in cls._value2member_map_


class Inventory(db.Model):
    """
    Class that represents a Inventory
    """

    app = None

    # Table Schema
    pid = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.Enum(Condition), primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    restock_level = db.Column(db.Integer)
    available = db.Column(db.Integer)

    def __init__(
        self,
        pid: int,
        condition: Condition,
        name: str,
        quantity: int,
        restock_level: int,
        available: int,
    ):
        """Constructor for Item in Inventory"""
        self.pid = pid
        self.condition = condition
        self.name = name
        self.quantity = quantity
        self.restock_level = restock_level
        self.available = available

    def __repr__(self):
        return (
            "<Inventory Product id=[%s], Condition=[%s], Name=[%s], Quantity=[%s], Restock_level=[%d], Available=[%d]>"
            % (
                self.pid,
                Condition(self.condition),
                self.name,
                self.quantity,
                self.restock_level,
                self.available,
            )
        )

    def create(self):
        """
        Creates an Item in the database
        """
        logger.info(
            "Creating item with pid: %d, name: %s, condition: %s",
            self.pid,
            self.name,
            Condition(self.condition)
        )
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Item to the database
        """
        if self.pid is None:
            raise DataValidationError(
                "No ID present for item in update"
            )  # Should not update an item with no ID
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """Removes a Inventory from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes a Inventory into a dictionary"""
        return {
            "pid": self.pid,
            "condition": self.condition.value,
            "name": self.name,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
            "available": self.available,
        }

    def deserialize(self, data):
        """
        Deserializes an Inventory Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            if(isinstance(data["name"], str)):
                self.name = data["name"]
            else:
                raise DataValidationError(
                    "Invalid type for string [name]" + str(type(data["name"]))
                )
            if isinstance(data["quantity"], int):
                self.quantity = data["quantity"]
            else:
                raise DataValidationError(
                    "Invalid type for int [quantity]" + str(type(data["quantity"]))
                )
            if isinstance(data["restock_level"], int):
                self.restock_level = data["restock_level"]
            else:
                raise DataValidationError(
                    "Invalid type for int [restock_level]"
                    + str(type(data["restock_level"]))
                )
            if isinstance(data["available"], int):
                self.available = data["available"]
            else:
                raise DataValidationError(
                    "Invalid type for int [available]" + str(type(data["available"]))
                )
        except KeyError as error:
            raise DataValidationError("Invalid Inventory: missing " + error.args[0])
        return self

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the Inventory in the database"""
        logger.info("Processing all Inventory")
        return cls.query.all()

    @classmethod
    def find(cls, pid):
        """Finds a Inventory by it's ID"""
        logger.info("Processing lookup for id %s ...", pid)
        return cls.query.filter(cls.pid == pid)

    @classmethod
    def find_by_pid_condition(cls, pid, condition):
        """Finds a Inventory by it's ID and condition"""
        logger.info(
            "Processing lookup for pid %s with condition %s  ...", pid, condition
        )
        return cls.query.get((pid, condition))

    @classmethod
    def find_by_name(cls, name):
        """Returns all Inventory with the given name

        Args:
            name (string): the name of the Inventory you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

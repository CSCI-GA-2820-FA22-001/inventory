""" Inventory Models """
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

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


class Inventory(db.Model):
    """
    Class that represents a Inventory
    """

    app = None

    # Table Schema
    pid = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.Enum(Condition), primary_key=True)
    name = db.Column(db.String(63))
    quantity = db.Column(db.Integer)
    restock_level = db.Column(db.Integer)
    active = db.Column(db.Boolean)


    def __init__(
        self,
        pid: int,
        condition: Condition,
        name = "",
        quantity = 1,
        restock_level = 10,
        active = True,
    ):
        """Constructor for Item in Inventory"""
        self.pid = pid
        self.condition = condition
        self.name = name
        self.quantity = quantity
        self.restock_level = restock_level
        self.active = active


    def create(self):
        """ Creates an Inventory item in the database """

        self.id = None
        db.session.add(self)
        db.session.commit()

    def update(self):
        """ Updates an Inventory Item in the database"""
        if self.pid is None:
            raise DataValidationError("pid must be provided")
        if self.condition is None:
            raise DataValidationError("condition must be provided")
        db.session.commit()

    def delete(self):
        """ Removes a Inventory item from database"""
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes an Inventory item into a dictionary"""
        return {
            "pid": self.pid,
            "condition": self.condition.value,
            "name": self.name,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
            "active": self.active,
        }

    def deserialize(self, data: dict):
        """ Creates an Inventory item from a dictionary """
        try:
            self.pid = data["pid"]
            self.condition = Condition(data["condition"])
            self.name = data["name"]
            self.quantity = data["quantity"]
            self.restock_level = data["restock_level"]
            self.active = data["active"]
        except ValueError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid item: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid item: body of request contained bad or no data " + str(error)
            ) from error

        return self

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        cls.app = app
        db.init_app(app)
        app.app_context().push()
        db.create_all()

    @classmethod
    def all(cls):
        """Returns all of the Inventory items in the database"""
        return cls.query.all()

    @classmethod
    def find_by_pid(cls, pid) -> list:
        """Finds a Inventory item by it's PID"""
        return cls.query.filter(cls.pid == pid)

    @classmethod
    def find_by_pid_condition(cls, pid, condition):
        """Finds a Inventory by it's ID and condition"""
        return cls.query.filter(cls.pid == pid, cls.condition == condition)

"""
Test cases for Inventory Model

"""
import os
import logging
import unittest
from service import app
from service.models import Inventory, DataValidationError, db, Condition
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  INVENTORY   M O D E L   T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """Test Cases for Inventory Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Inventory).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_item(self):
        """It should Create an item and assert that it exists"""
        item = Inventory(
            pid=1,
            condition=Condition.NEW,
            name="Test",
            quantity=1,
            restock_level=2,
            available=3,
        )
        self.assertTrue(item is not None)
        self.assertEqual(item.pid, 1)
        self.assertEqual(item.condition, Condition.NEW)
        self.assertEqual(item.name, "Test")
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.restock_level, 2)
        self.assertEqual(item.available, 3)

    def test_add_an_item(self):
        """It should Create an item and add it to the database"""
        items = Inventory.all()
        self.assertEqual(items, [])
        item = Inventory(
            pid=1,
            condition=Condition.NEW,
            name="Test",
            quantity=1,
            restock_level=2,
            available=3,
        )
        self.assertTrue(item is not None)
        self.assertEqual(item.pid, 1)
        item.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(item.pid)
        items = Inventory.all()
        self.assertEqual(len(items), 1)

    def test_read_an_item(self):
        """It should Read a Inventory"""
        item = InventoryFactory()
        logging.debug(item)
        item.create()
        self.assertIsNotNone(item.pid)
        # Fetch it back
        found_item = Inventory.find_by_pid_condition(
            pid=item.pid, condition=item.condition
        )
        self.assertEqual(found_item.pid, item.pid)
        self.assertEqual(found_item.condition, item.condition)
        self.assertEqual(found_item.name, item.name)
        self.assertEqual(found_item.quantity, item.quantity)

    def test_update_an_item(self):
        """It should Update an Item in the Inventory"""
        item = InventoryFactory()
        logging.debug(item)
        item.create()
        logging.debug(item)
        self.assertIsNotNone(item.pid)
        # Change it an save it
        item.quantity = 100
        item.update()
        self.assertEqual(item.quantity, 100)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        items = Inventory.all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].quantity, 100)

    def test_update_no_id(self):
        """It should not Update a Inventory with no id"""
        item = InventoryFactory()
        logging.debug(item)
        item.pid = None
        self.assertRaises(DataValidationError, item.update)

    def test_delete_an_item(self):
        """It should Delete an Inventory Item"""
        item = InventoryFactory()
        item.create()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the item and make sure it isn't in the database
        item.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_list_all_items(self):
        """It should List all Items in the Inventory database"""
        items = Inventory.all()
        self.assertEqual(items, [])
        # Create 3 Items
        for _ in range(3):
            item = InventoryFactory()
            item.create()
        # See if we get back 3 items
        items = Inventory.all()
        self.assertEqual(len(items), 3)

    def test_serialize_an_item(self):
        """It should serialize an Item"""
        item = InventoryFactory()
        data = item.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("pid", data)
        self.assertEqual(data["pid"], item.pid)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], item.condition.value)
        self.assertIn("name", data)
        self.assertEqual(data["name"], item.name)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertIn("restock_level", data)
        self.assertEqual(data["restock_level"], item.restock_level)
        self.assertIn("available", data)
        self.assertEqual(data["available"], item.available)

    def test_deserialize_an_item(self):
        """It should de-serialize an Item"""
        data = InventoryFactory().serialize()
        item = Inventory(
            pid=1,
            condition=Condition.NEW,
            name="Test",
            quantity=1,
            restock_level=2,
            available=3,
        )
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.pid, 1)
        self.assertEqual(item.name, data["name"])
        self.assertEqual(item.quantity, data["quantity"])
        self.assertEqual(item.restock_level, data["restock_level"])
        self.assertEqual(item.available, data["available"])

    def test_deserialize_missing_data(self):
        """It should not deserialize an Item with missing data"""
        data = {"id": 1, "name": "Test Name"}
        item = Inventory(
            pid=1,
            condition=Condition.NEW,
            name="Test",
            quantity=1,
            restock_level=2,
            available=3,
        )
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_name(self):
        """It should not deserialize a bad Name attribute"""
        test_item = InventoryFactory()
        data = test_item.serialize()
        data["name"] = True
        item = Inventory(
            pid=1,
            condition=Condition.NEW,
            name="Test",
            quantity=1,
            restock_level=2,
            available=3,
        )
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_quantity(self):
        """It should not deserialize a bad Quantity attribute"""
        test_item = InventoryFactory()
        data = test_item.serialize()
        data["quantity"] = "true"
        item = Inventory(
            pid=1,
            condition=Condition.NEW,
            name="Test",
            quantity=1,
            restock_level=2,
            available=3,
        )
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_restock_level(self):
        """It should not deserialize a bad Restock Level attribute"""
        test_item = InventoryFactory()
        data = test_item.serialize()
        data["restock_level"] = "true"
        item = Inventory(
            pid=1,
            condition=Condition.NEW,
            name="Test",
            quantity=1,
            restock_level=2,
            available=3,
        )
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not deserialize a bad available attribute"""
        test_item = InventoryFactory()
        data = test_item.serialize()
        data["available"] = "true"
        item = Inventory(
            pid=1,
            condition=Condition.NEW,
            name="Test",
            quantity=1,
            restock_level=2,
            available=3,
        )
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_find_item_pid_condition(self):
        """It should Find an Item in the Inventory by PID"""
        items = InventoryFactory.create_batch(5)
        for item in items:
            item.create()
        logging.debug(items)
        # make sure they got saved
        self.assertEqual(len(Inventory.all()), 5)
        # find the 2nd item in the list
        item = Inventory.find_by_pid_condition(items[1].pid, items[1].condition)
        self.assertIsNot(item, None)
        self.assertEqual(item.pid, items[1].pid)
        self.assertEqual(item.name, items[1].name)
        self.assertEqual(item.quantity, items[1].quantity)
        self.assertEqual(item.condition, items[1].condition)

    def test_find_by_name(self):
        """It should Find a Item by Name"""
        items = InventoryFactory.create_batch(1)
        for item in items:
            item.create()
        name = items[0].name
        found = Inventory.find_by_name(name)
        self.assertEqual(found.count(), 1)
        self.assertEqual(found[0].pid, items[0].pid)
        self.assertEqual(found[0].quantity, items[0].quantity)

    def test_find(self):
        """Find function should work"""
        items = InventoryFactory.create_batch(1)
        for item in items:
            item.create()
        pid = items[0].pid
        found = Inventory.find(pid)
        self.assertEqual(found.count(), 1)
        self.assertEqual(found[0].pid, items[0].pid)

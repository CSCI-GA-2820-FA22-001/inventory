""" Inventory Models Test Suite """
import os
import logging
import unittest
from service import app
# from service.common import status
from service.models import Inventory, db, DataValidationError
#Condition
from tests.factories import InventoryFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory"

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
        test_item = InventoryFactory()

        self.assertIsNotNone(test_item.name)
        self.assertIsNotNone(test_item.pid)
        self.assertIsNotNone(test_item.condition)
        self.assertIsNotNone(test_item.quantity)
        self.assertIsNotNone(test_item.restock_level)
        self.assertIsNotNone(test_item.active)


    def test_add_an_item(self):
        """It should Create an item and add it to the Inventory"""

        inventory = Inventory.all()
        self.assertEqual(inventory, [])
        item = InventoryFactory()
        item.create()
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)

    def test_read_an_item(self):
        """It should Read an item in the Inventory"""
        item = InventoryFactory()
        item.create()

        found_item = []
        found_item = Inventory.find_by_pid_condition(pid=item.pid, condition=item.condition)
        self.assertEqual(found_item[0].pid, item.pid)
        self.assertEqual(found_item[0].condition, item.condition)
        self.assertEqual(found_item[0].name, item.name)
        self.assertEqual(found_item[0].quantity, item.quantity)
        self.assertEqual(found_item[0].active, item.active)

    def test_update_an_item(self):
        """It should Update an Item in the Inventory"""
        item = InventoryFactory()
        item.create()
        self.assertIsNotNone(item.pid)

        item.quantity = 200
        item.update()
        self.assertEqual(item.quantity, 200)

        items = Inventory.all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].quantity, 200)

    def test_update_an_item_no_pid(self):
        """It should not Update an Item if there is no condition"""
        item = InventoryFactory()
        item.create()
        item.pid = None
        self.assertIsNone(item.pid)

        item.quantity = 200
        self.assertRaises(DataValidationError, item.update)

    def test_update_an_item_no_condition(self):
        """It should not Update an Item if there is no condition"""
        item = InventoryFactory()
        item.create()
        item.condition = None
        self.assertIsNone(item.condition)

        item.quantity = 200
        self.assertRaises(DataValidationError, item.update)



    def test_delete_an_item(self):
        """It should Delete an item in the Inventory"""
        item = InventoryFactory()
        item.create()
        self.assertEqual(len(Inventory.all()), 1)

        item.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_list_all_items(self):
        """It should List all items in the Inventory"""
        items = Inventory.all()
        self.assertEqual(items, [])

        for _ in range(3):
            item = InventoryFactory()
            item.create()

        items = Inventory.all()
        self.assertEqual(len(items), 3)

    def test_serialize_an_item(self):
        """It should Serialize an item"""
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
        self.assertIn("active", data)
        self.assertEqual(data["active"], item.active)

    def test_deserialize_an_item(self):
        """It should Deserialize an item"""
        item = InventoryFactory()
        data = item.serialize()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.pid, data["pid"])
        self.assertEqual(item.name, data["name"])
        self.assertEqual(item.quantity, data["quantity"])
        self.assertEqual(item.restock_level, data["restock_level"])
        self.assertEqual(item.active, data["active"])

    def test_deserialize_an_item_invalid_attribute(self):
        """It should raise a DataValidationError """
        item = InventoryFactory()
        data = item.serialize()
        data["condition"] = "Test"
        self.assertRaises(DataValidationError, item.deserialize, data)


    def test_deserialize_an_item_missing_data(self):
        """It should raise a DataValidationError """
        item = InventoryFactory()
        data = item.serialize()
        data.pop('quantity')
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_an_item_bad_data(self):
        """It should raise a DataValidationError """
        item = InventoryFactory()
        data = "Test"
        self.assertRaises(DataValidationError, item.deserialize, data)



    def test_find_item_pid_condition(self):
        """It should Find an item by PID and Condition"""
        items = []
        items = InventoryFactory.create_batch(5)
        for i in items:
            i.create()

        self.assertEqual(len(Inventory.all()), 5)

        item = items[1]
        found_item = []
        found_item = Inventory.find_by_pid_condition(item.pid, item.condition)
        self.assertIsNot(found_item[0], None)
        self.assertEqual(found_item[0].pid, item.pid)
        self.assertEqual(found_item[0].name, item.name)
        self.assertEqual(found_item[0].quantity, item.quantity)
        self.assertEqual(found_item[0].condition, item.condition)

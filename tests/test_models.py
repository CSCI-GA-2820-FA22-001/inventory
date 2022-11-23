""" Inventory Models Test Suite """
import os
import logging
import unittest
from service import app
from service.models import Inventory, db, DataValidationError #, Condition
from tests.factories import InventoryFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory"


######################################################################
#  I N V E N T O R Y   M O D E L   T E S T   C A S E S
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

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------

    def test_add_an_item(self):
        """It should Add an item to the Inventory"""

        inventory = Inventory.all()
        self.assertEqual(inventory, [])
        item = InventoryFactory()
        item.create()
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------

    def test_read_an_item(self):
        """It should Read an item in the Inventory"""
        item = InventoryFactory()
        item.create()

        found_item = Inventory.find_by_pid_condition(item.pid, item.condition.value)
        self.assertEqual(found_item.pid, item.pid)
        self.assertEqual(found_item.condition, item.condition)
        self.assertEqual(found_item.name, item.name)
        self.assertEqual(found_item.quantity, item.quantity)
        self.assertEqual(found_item.restock_level, item.restock_level)
        self.assertEqual(found_item.active, item.active)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------

    def test_update_an_item(self):
        """It should Update an item in the Inventory"""
        item = InventoryFactory()
        item.create()
        original_pid = item.pid
        self.assertIsNotNone(original_pid)

        item.quantity = 200
        item.update()
        self.assertEqual(item.pid, original_pid)
        self.assertEqual(item.quantity, 200)

        items = Inventory.all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].pid, item.pid)
        self.assertEqual(items[0].quantity, 200)

    def test_update_an_item_no_pid(self):
        """It should not Update an item if there is no PID"""
        item = InventoryFactory()
        item.create()
        item.pid = None
        self.assertIsNone(item.pid)
        self.assertRaises(DataValidationError, item.update)

    def test_update_an_item_no_condition(self):
        """It should not Update an item if there is no Condition"""
        item = InventoryFactory()
        item.create()
        item.condition = None
        self.assertIsNone(item.condition)

        item.quantity = 200
        self.assertRaises(DataValidationError, item.update)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------


    def test_delete_an_item(self):
        """It should Delete an item in the Inventory"""
        item = InventoryFactory()
        item.create()
        self.assertEqual(len(Inventory.all()), 1)

        item.delete()
        self.assertEqual(len(Inventory.all()), 0)


    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------

    def test_list_all_items(self):
        """It should List all items in the Inventory"""
        items = Inventory.all()
        self.assertEqual(items, [])

        for _ in range(3):
            item = InventoryFactory()
            item.create()

        items = Inventory.all()
        self.assertEqual(len(items), 3)


    # ----------------------------------------------------------
    # TEST SERIALIZE
    # ----------------------------------------------------------

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


    # ----------------------------------------------------------
    # TEST DESERIALIZE
    # ----------------------------------------------------------

    def test_deserialize_an_item(self):
        """It should Deserialize an item"""
        item = InventoryFactory()
        data = item.serialize()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.pid, data["pid"])
        self.assertEqual(item.name, data["name"])
        self.assertEqual(item.condition.value, data["condition"])
        self.assertEqual(item.quantity, data["quantity"])
        self.assertEqual(item.restock_level, data["restock_level"])
        self.assertEqual(item.active, data["active"])

    def test_deserialize_an_item_missing_data(self):
        """It should not Deserialize an item with missing data"""
        item = InventoryFactory()
        data = item.serialize()
        data.pop("quantity")
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_an_item_bad_data(self):
        """It should not Deserialize an item with bad data"""
        item = InventoryFactory()
        data = "Test"
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_an_item_bad_pid(self):
        """It should not Deserialize an item with bad PID"""
        item = InventoryFactory()
        item.pid = "Test"
        data = item.serialize()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_an_item_bad_condition(self):
        """It should not Deserialize an item with bad Condition"""
        item = InventoryFactory()
        data = item.serialize()
        data["condition"] = "Test"
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_an_item_bad_name(self):
        """It should not Deserialize an item with bad Name"""
        item = InventoryFactory()
        item.name = 0
        data = item.serialize()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_an_item_bad_quantity(self):
        """It should not Deserialize an item with bad Quantity"""
        item = InventoryFactory()
        item.quantity = "Test"
        data = item.serialize()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_an_item_bad_restock_level(self):
        """It should not Deserialize an item with bad Restock Level"""
        item = InventoryFactory()
        item.restock_level = "Test"
        data = item.serialize()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_an_item_bad_active(self):
        """It should not Deserialize an item with bad Active"""
        item = InventoryFactory()
        item.active = "Test"
        data = item.serialize()
        self.assertRaises(DataValidationError, item.deserialize, data)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------


    def test_find_item_pid_condition(self):
        """It should Find an item by PID and Condition"""
        items = InventoryFactory.create_batch(5)
        for i in items:
            i.create()

        self.assertEqual(len(Inventory.all()), 5)

        item = items[1]
        found_item = Inventory.find_by_pid_condition(item.pid, item.condition.value)
        self.assertIsNot(found_item, None)
        self.assertEqual(found_item.pid, item.pid)
        self.assertEqual(found_item.name, item.name)
        self.assertEqual(found_item.condition, item.condition)
        self.assertEqual(found_item.quantity, item.quantity)
        self.assertEqual(found_item.restock_level, item.restock_level)
        self.assertEqual(found_item.active, item.active)

    def test_find_item_pid(self):
        """It should Find a list of items by PID"""
        items = InventoryFactory.create_batch(5)
        for item in items:
            item.create()
        pid = items[0].pid
        count = len([item for item in items if item.pid == pid])

        found = Inventory.find_by_pid(pid)
        self.assertEqual(found.count(), count)
        for item in found:
            self.assertEqual(item.pid, pid)


    def test_find_item_bad_pid(self):
        """It should not Find a list of items with a bad PID"""
        self.assertRaises(DataValidationError, Inventory.find_by_pid, "Test")

    def test_find_item_condition(self):
        """It should Find a list of items by Condition"""
        items = InventoryFactory.create_batch(5)
        for item in items:
            item.create()
        condition = items[0].condition
        count = len([item for item in items if item.condition == condition])

        found = Inventory.find_by_condition(condition.value)
        self.assertEqual(found.count(), count)
        for item in found:
            self.assertEqual(item.condition, condition)

    def test_find_item_bad_condition(self):
        """It should not Find a list of items with a bad Condition"""
        self.assertRaises(DataValidationError, Inventory.find_by_condition, "Test")

    def test_find_item_active(self):
        """It should Find a list of items by Active """
        items = InventoryFactory.create_batch(5)
        for item in items:
            item.create()
        active = items[0].active
        count = len([item for item in items if item.active == active])

        found = Inventory.find_by_active(active)
        self.assertEqual(found.count(), count)
        for item in found:
            self.assertEqual(item.active, active)


    def test_find_item_bad_active(self):
        """It should not Find a list of items with a bad Active"""
        self.assertRaises(DataValidationError, Inventory.find_by_active, "Test")

"""
Test cases for Inventory Model

"""
import os
import logging
import unittest
from service import app
from service.models import Inventory, DataValidationError, db
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  INVENTORY   M O D E L   T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """ Test Cases for Inventory Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Inventory).delete()
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_item(self):
        """It should Create an item and assert that it exists"""
        item = Inventory(id=1, name='Test', quantity=5, description='Test Description')
        self.assertTrue(item is not None)
        self.assertEqual(item.id, 1)
        self.assertEqual(item.name, 'Test')
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.description, 'Test Description')

    def test_add_an_item(self):
        """It should Create an item and add it to the database"""
        items = Inventory.all()
        self.assertEqual(items, [])
        item = Inventory(id=1, name='Test', quantity=5, description='Test Description')
        self.assertTrue(item is not None)
        self.assertEqual(item.id, 1)
        item.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(item.id)
        items = Inventory.all()
        self.assertEqual(len(items), 1)

    def test_read_an_item(self):
        """It should Read a Inventory"""
        item = InventoryFactory()
        logging.debug(item)
        item.id = None
        item.create()
        self.assertIsNotNone(item.id)
        # Fetch it back
        found_item = Inventory.find(item.id)
        self.assertEqual(found_item.id, item.id)
        self.assertEqual(found_item.name, item.name)
        self.assertEqual(found_item.quantity, item.quantity)

    def test_update_a_item(self):
        """It should Update an Item in the Inventory"""
        item = InventoryFactory()
        logging.debug(item)
        item.id = None
        item.create()
        logging.debug(item)
        self.assertIsNotNone(item.id)
        # Change it an save it
        item.quantity = 100
        original_id = item.id
        item.update()
        self.assertEqual(item.id, original_id)
        self.assertEqual(item.quantity, 100)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        items = Inventory.all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, original_id)
        self.assertEqual(items[0].quantity, 100)

    def test_update_no_id(self):
        """It should not Update a Inventory with no id"""
        item = InventoryFactory()
        logging.debug(item)
        item.id = None
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
        self.assertIn("id", data)
        self.assertEqual(data["id"], item.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], item.name)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertIn("description", data)
        self.assertEqual(data["description"], item.description)

    def test_deserialize_an_item(self):
        """It should de-serialize an Item"""
        data = InventoryFactory().serialize()
        item = Inventory(id=1, name='Test', quantity=1, description='Test')
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.id, 1)
        self.assertEqual(item.name, data["name"])
        self.assertEqual(item.quantity, data["quantity"])
        self.assertEqual(item.description, data["description"])

    def test_deserialize_missing_data(self):
        """It should not deserialize ar Item with missing data"""
        data = {"id": 1, "name": "Test Name"}
        item = Inventory(id=1, name='Test', quantity=1, description='Test')
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_find_item(self):
        """It should Find an Item in the Inventory by ID"""
        items = InventoryFactory.create_batch(5)
        for item in items:
            item.create()
        logging.debug(items)
        # make sure they got saved
        self.assertEqual(len(Inventory.all()), 5)
        # find the 2nd item in the list
        item = Inventory.find(items[1].id)
        self.assertIsNot(item, None)
        self.assertEqual(item.id, items[1].id)
        self.assertEqual(item.name, items[1].name)
        self.assertEqual(item.quantity, items[1].quantity)
        self.assertEqual(item.description, items[1].description)

    def test_find_by_name(self):
        """It should Find a Item by Name"""
        items = InventoryFactory.create_batch(1)
        for item in items:
            item.create()
        name = items[0].name
        found = Inventory.find_by_name(name)
        self.assertEqual(found.count(), 1)
        self.assertEqual(found[0].description, items[0].description)
        self.assertEqual(found[0].quantity, items[0].quantity)

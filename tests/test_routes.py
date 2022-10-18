"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db, init_db, Inventory
from service.common import status
from tests.factories import InventoryFactory  # HTTP Status Codes


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory"

######################################################################
#  T E S T   I N V E N T O R Y   S E R V I C E
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_inventory_list(self):
        """It should Get a list of Inventory"""
        self.client.get(BASE_URL)
        # do some asserts

    def test_get_inventory(self):
        """It should Get a single Inventory item"""
        self.client.get(f"{BASE_URL}/1")
        # do some asserts

    def test_create_inventory(self):
        """It should Create a new Inventory item"""
        self.client.post(BASE_URL, json={})
        # do some asserts

    def test_update_inventory(self):
        """It should Update an existing Inventory item"""
        self.client.put(f"{BASE_URL}/1", json={})
        # do some asserts

    def test_delete_inventory(self):
        """It should Delete a Inventory item"""
        test_item = InventoryFactory()
        test_item.create()
        self.assertEqual(Inventory.find_by_pid_condition(test_item.pid, test_item.condition), test_item)
        
        response = self.client.delete(f"{BASE_URL}/pid/{test_item.pid}/condition/{test_item.condition.value}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Inventory.find_by_pid_condition(test_item.pid, test_item.condition), None)

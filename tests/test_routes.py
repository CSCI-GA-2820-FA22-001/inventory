""" Inventory API Service Test Suite """
import os
import logging
from unittest import TestCase
from service import app
from service.models import db, init_db, Inventory, Condition
from service.common import status
from tests.factories import InventoryFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
HEALTH_BASE_URL = "/health"
BASE_URL = "/inventory"


######################################################################
#  T E S T   I N V E N T O R Y   S E R V I C E
######################################################################
class TestInventoryServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
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
        db.session.query(Inventory).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_inventory_list(self):
        """It should Get a list of Inventory"""
        test_item_number = 3
        for _ in range(test_item_number):
            test_item = InventoryFactory()
            test_item.create()
        response = self.client.get(BASE_URL)
        data = response.get_json()
        self.assertEqual(test_item_number, len(data))

    def test_get_inventory_with_condition(self):
        """It should Get a single Inventory item"""
        test_item = InventoryFactory()
        test_item.create()
        response = self.client.get(
            f"{BASE_URL}/{test_item.pid}",
            query_string= f"condition={test_item.condition.name}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data[0]["pid"], test_item.pid)
        self.assertEqual(Condition(data[0]["condition"]), test_item.condition)


    def test_get_inventory_without_condition(self):
        """It should Get a single Inventory item"""
        test_item = InventoryFactory()
        test_item.create()
        response = self.client.get( f"{BASE_URL}/{test_item.pid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data[0]["pid"], test_item.pid)

    def test_get_inventory_bad_pid(self):
        """It should raise a 404 error"""

        pid = "Test"
        response = self.client.get(f"{BASE_URL}/{pid}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_create_inventory(self):
        """It should Create a new Inventory item"""
        test_item = []
        test_item = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_item.serialize())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        new_item = response.get_json()
        self.assertEqual(new_item["name"], test_item.name)
        self.assertEqual(new_item["condition"], test_item.condition.value)
        self.assertEqual(new_item["pid"], test_item.pid)
        self.assertEqual(new_item["quantity"], test_item.quantity)
        self.assertEqual(new_item["restock_level"], test_item.restock_level)
        self.assertEqual(new_item["active"], test_item.active)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        found_item = response.get_json()
        self.assertEqual(found_item[0]["pid"], test_item.pid)
        self.assertEqual(found_item[0]["condition"], test_item.condition.value)
        self.assertEqual(found_item[0]["name"], test_item.name)
        self.assertEqual(found_item[0]["quantity"], test_item.quantity)
        self.assertEqual(found_item[0]["restock_level"], test_item.restock_level)
        self.assertEqual(found_item[0]["active"], test_item.active)



    def test_update_inventory(self):
        """It should Update an Inventory item"""
        test_item = []
        test_item = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_item.serialize())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        new_item = []
        new_item = response.get_json()
        new_item["name"] = "Test"
        pid = new_item["pid"]
        response = self.client.put(f"{BASE_URL}/{pid}", json=new_item)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_item = response.get_json()
        self.assertEqual(updated_item["name"], "Test")

    def test_update_inventory_bad_item(self):
        """It should throw a 404 error"""
        test_item = []
        test_item = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_item.serialize())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        new_item = []
        new_item = response.get_json()
        new_item["condition"] = "Test"
        pid = new_item["pid"]
        response = self.client.put(f"{BASE_URL}/{pid}", json=new_item)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory_does_not_exist(self):
        """It should throw a 404 error"""
        test_item = []
        test_item = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_item.serialize())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        new_item = []
        new_item = response.get_json()
        new_item["condition"] = "Test"
        new_item["pid"] = -5
        pid = new_item["pid"]
        response = self.client.put(f"{BASE_URL}/{pid}", json=new_item)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recommendation(self):
        """It should Delete an Inventory item"""
        test_item = []
        test_item = InventoryFactory()
        self.client.post(BASE_URL, json=test_item.serialize())
        pid = test_item.pid

        response = self.client.delete(f"{BASE_URL}/{pid}", json=test_item.serialize())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(
            f"{BASE_URL}/{test_item.pid}",
            query_string= f"condition={test_item.condition.name}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recommendation_bad_condition(self):
        """It should throw a 404 error"""
        test_item = []
        test_item = InventoryFactory()
        self.client.post(BASE_URL, json=test_item.serialize())

        test_item = test_item.serialize()
        test_item["condition"] = "Test"
        response = self.client.delete(f"{BASE_URL}/{test_item['pid']}", json=test_item)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_health_check(self):
        """It should return a 200 OK status"""
        response = self.client.get(f"{HEALTH_BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
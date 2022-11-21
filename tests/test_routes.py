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
    # T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_inventory_list(self):
        """It should Get a list of all Inventory items"""
        test_item_number = 3
        for _ in range(test_item_number):
            test_item = InventoryFactory()
            test_item.create()
        response = self.client.get(BASE_URL)
        data = response.get_json()
        self.assertEqual(test_item_number, len(data))


    def test_get_inventory_list_filter_pid(self):
        """It should Get a list of Inventory items filtered by PID"""

        items = InventoryFactory.create_batch(5)
        for i in items:
            i.create()

        pid = items[0].pid
        response = self.client.get(BASE_URL, query_string= f"pid={pid}")
        data = response.get_json()
        self.assertEqual(1, len(data))

    def test_get_inventory_list_filter_condition(self):
        """It should Get a list of Inventory items filtered by Condition"""

        items = InventoryFactory.create_batch(5)
        items[0].condition = Condition(0)
        items[1].condition = Condition(0)
        items[2].condition = Condition(1)
        items[3].condition = Condition(1)
        items[4].condition = Condition(1)
        for i in items:
            i.create()

        response = self.client.get(BASE_URL, query_string= f"condition={0}")
        data = response.get_json()
        self.assertEqual(2, len(data))

    def test_get_inventory_list_filter_active(self):
        """It should Get a list of Inventory items filtered by Active"""

        items = InventoryFactory.create_batch(5)
        items[0].active = True
        items[1].active = True
        items[2].active = True
        items[3].active = False
        items[4].active = False
        for i in items:
            i.create()

        response = self.client.get(BASE_URL, query_string= f"active={True}")
        data = response.get_json()
        self.assertEqual(3, len(data))

    def test_get_inventory_with_pid_with_condition(self):
        """It should Get a single Inventory item with the given PID and Condition"""
        test_item = InventoryFactory()
        test_item.create()
        response = self.client.get(
            f"{BASE_URL}/{test_item.pid}",
            query_string= f"condition={test_item.condition.value}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["pid"], test_item.pid)
        self.assertEqual(Condition(data["condition"]), test_item.condition)


    def test_get_inventory_with_pid_without_condition(self):
        """It should Get all Inventory items with the given PID"""
        test_item_one = InventoryFactory()
        test_item_one.condition = Condition(0)
        test_item_one.create()

        test_item_two = InventoryFactory()
        test_item_two.pid = test_item_one.pid
        test_item_two.condition = Condition(1)
        test_item_two.create()

        response = self.client.get( f"{BASE_URL}/{test_item_one.pid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data[0]["pid"], test_item_one.pid)
        self.assertEqual(data[0]["condition"], test_item_one.condition.value)


    def test_get_inventory_does_not_exist_with_condition(self):
        """It should not Get an item that does not exist, with Condition"""
        response = self.client.get(BASE_URL)
        data = response.get_json()
        self.assertEqual(0, len(data))

        test_item = InventoryFactory()
        response = self.client.get(
            f"{BASE_URL}/{test_item.pid}",
            query_string= f"condition={test_item.condition.value}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_get_inventory_does_not_exist_without_condition(self):
        """It should not Get an item that does not exist, without Condition"""
        response = self.client.get(BASE_URL)
        data = response.get_json()
        self.assertEqual(0, len(data))

        test_item = InventoryFactory()
        response = self.client.get(f"{BASE_URL}/{test_item.pid}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_create_inventory(self):
        """It should Create a new Inventory item"""
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

        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        found_item = response.get_json()
        self.assertEqual(found_item["pid"], test_item.pid)
        self.assertEqual(found_item["condition"], test_item.condition.value)
        self.assertEqual(found_item["name"], test_item.name)
        self.assertEqual(found_item["quantity"], test_item.quantity)
        self.assertEqual(found_item["restock_level"], test_item.restock_level)
        self.assertEqual(found_item["active"], test_item.active)

    def test_create_bad_pid(self):
        """It should not Create an item with a bad PID"""
        test_item = InventoryFactory()
        test_item.pid = "Test"
        response = self.client.post(BASE_URL, json=test_item.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bad_condition(self):
        """It should not Create a item with bad Condition"""
        item = InventoryFactory()
        test_item = item.serialize()
        test_item["condition"] = "Test"
        response = self.client.post(BASE_URL, json=test_item)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_duplicate(self):
        """It should not Create a duplicate item"""
        test_item = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_item.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(BASE_URL, json=test_item.serialize())

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_item_no_content_type(self):
        """It should not Create an item with no Content-Type"""
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_item_wrong_content_type(self):
        """It should not Create a item with wrong Content-Type"""
        response = self.client.post(BASE_URL, data={}, content_type="plain/text")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_call_create_with_an_id(self):
        """It should not allow calling endpoint incorrectly"""
        response = self.client.post(f"{BASE_URL}/0", json={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)



    def test_update_inventory(self):
        """It should Update an Inventory item"""
        test_item = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_item.serialize())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        new_item = response.get_json()
        new_item["name"] = "Test"
        pid = new_item["pid"]
        response = self.client.put(f"{BASE_URL}/{pid}", json=new_item)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_item = response.get_json()
        self.assertEqual(updated_item["name"], "Test")


    def test_update_inventory_does_not_exist(self):
        """It should not Update an item that does not exist """
        test_item = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_item.serialize())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        new_item = response.get_json()
        new_item["pid"] = -5
        response = self.client.put(f"{BASE_URL}/{new_item['pid']}", json=new_item)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory_bad_condition(self):
        """It should not Update an item with an invalid Condition """
        test_item = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_item.serialize())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        new_item = response.get_json()
        new_item["condition"] = "Test"
        response = self.client.put(f"{BASE_URL}/{new_item['pid']}", json=new_item)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_update_inventory_empty_inventory(self):
        """It should not Update an item when the Inventory is empty """
        test_item = InventoryFactory()
        response = self.client.put(f"{BASE_URL}/{test_item.pid}", json=test_item.serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_with_condition(self):
        """It should Delete an Inventory item with Condition"""
        test_item_one = InventoryFactory()
        test_item_one.condition = Condition(0)
        self.client.post(BASE_URL, json=test_item_one.serialize())

        test_item_two = InventoryFactory()
        test_item_two.pid = test_item_one.pid
        test_item_two.condition = Condition(1)
        self.client.post(BASE_URL, json=test_item_two.serialize())
        pid = test_item_one.pid

        response = self.client.delete(f"{BASE_URL}/{pid}/{0}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(BASE_URL)
        data = response.get_json()
        self.assertEqual(1, len(data))



    def test_delete_item_without_condition(self):
        """It should Delete an Inventory item without Condition"""
        test_item_one = InventoryFactory()
        test_item_one.condition = Condition(0)
        self.client.post(BASE_URL, json=test_item_one.serialize())

        test_item_two = InventoryFactory()
        test_item_two.pid = test_item_one.pid
        test_item_two.condition = Condition(1)
        self.client.post(BASE_URL, json=test_item_two.serialize())
        pid = test_item_one.pid

        response = self.client.delete(f"{BASE_URL}/{pid}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(f"{BASE_URL}/{pid}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_activate(self):
        """ It should Activate an Inventory item"""
        test_item = InventoryFactory()
        test_item.active = False
        test_item.create()
        self.client.put(f"{BASE_URL}/activate/{test_item.pid}/{test_item.condition.value}")
        response = self.client.get(
            f"{BASE_URL}/{test_item.pid}",
            query_string= f"condition={test_item.condition.value}")

        data = response.get_json()
        self.assertEqual(data["active"], True)


    def test_deactivate(self):
        """ It should Deactivate an Inventory item"""
        test_item = InventoryFactory()
        test_item.active = True
        test_item.create()
        self.client.put(f"{BASE_URL}/deactivate/{test_item.pid}/{test_item.condition.value}")
        response = self.client.get(
            f"{BASE_URL}/{test_item.pid}",
            query_string= f"condition={test_item.condition.value}")
        data = response.get_json()
        self.assertEqual(data["active"], False)


    def test_health_check(self):
        """It should return a 200 OK status"""
        response = self.client.get(f"{HEALTH_BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

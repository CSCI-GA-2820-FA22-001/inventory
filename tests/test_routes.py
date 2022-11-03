"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
# from unittest.mock import MagicMock, patch
from service import app
from service.models import db, init_db, Inventory, Condition
from service.common import status
from tests.factories import InventoryFactory  # HTTP Status Codes


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
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

    def test_get_inventory(self):
        """It should Get a single Inventory item"""

        test_inventory = InventoryFactory()
        test_inventory.create()
        response = self.client.get(f"{BASE_URL}/pid/{test_inventory.pid}/condition/{test_inventory.condition.value}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_inventory.name)

    def test_get_inventory_invalid_condition_id(self):
        """It should return an invalid Condition ID error for Get Inventory"""

        test_inventory = InventoryFactory()
        test_inventory.create()
        response = self.client.get(f"{BASE_URL}/pid/{test_inventory.pid}/condition/10")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_inventory_invalid_pid_condition_id(self):
        """It should return an 404 Not Found on Get Inventory"""

        test_inventory = InventoryFactory()
        test_inventory.create()
        response = self.client.get(f"{BASE_URL}/pid/{test_inventory.pid + 1}/condition/{test_inventory.condition.value}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_create_inventory_happy_path(self):
        """It should Create a new Inventory item"""
        test_item = InventoryFactory()
        logging.debug("Test Item: %s", test_item.serialize())
        response = self.client.post(BASE_URL, json=test_item.serialize())
        logging.debug("response: %s", response.text)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_item = response.get_json()
        self.assertEqual(new_item["name"], test_item.name)
        self.assertEqual(new_item["condition"], test_item.condition.value)
        self.assertEqual(new_item["pid"], test_item.pid)
        self.assertEqual(new_item["quantity"], test_item.quantity)
        self.assertEqual(new_item["restock_level"], test_item.restock_level)
        self.assertEqual(new_item["active"], test_item.active.value)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_item = response.get_json()
        self.assertEqual(new_item["name"], test_item.name)
        self.assertEqual(new_item["condition"], test_item.condition.value)
        self.assertEqual(new_item["pid"], test_item.pid)
        self.assertEqual(new_item["quantity"], test_item.quantity)
        self.assertEqual(new_item["restock_level"], test_item.restock_level)
        self.assertEqual(new_item["active"], test_item.active.value)

    
    def test_create_inventory_missing_pid(self):
        """It should test the create case where pid is missing"""
        
        response = self.client.post(
            f"{BASE_URL}",
            json={
                "condition" : 0,
                "name": "Test Name",
                "quantity": 2,
                "restock_level": 3,
                "active": 0
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inventory_missing_condition(self):
        """It should test the create case where condition is missing"""
        
        response = self.client.post(
            f"{BASE_URL}",
            json={
                "pid" : 0,
                "name": "Test Name",
                "quantity": 2,
                "restock_level": 3,
                "active": 0
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_inventory_missing_name(self):
        """It should test the create case where condition is missing"""
        
        response = self.client.post(
            f"{BASE_URL}",
            json={
                "pid" : 0,
                "condition": 0,
                "quantity": 2,
                "restock_level": 3,
                "active": 0
            }
        )
        self.assertEqual(response.status_code, 400)
        

    def test_create_inventory_invalid_pid(self):
        """It should test the create case where pid is not a number"""
        
        response = self.client.post(
            f"{BASE_URL}",
            json={
                "pid" : "testing",
                "condition": 0,
                "quantity": 2,
                "restock_level": 3,
                "active": 0,
                "name" : "testing"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_inventory_invalid_condition_type(self):
        """It should test the create case where condition is invalid"""
        
        response = self.client.post(
            f"{BASE_URL}",
            json={
                "pid" : 0,
                "condition": "NEW",
                "quantity": 2,
                "restock_level": 3,
                "active": 0,
                "name" : "testing"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_inventory_invalid_condition_int(self):
        """It should test the create case where condition is invalid"""
        
        response = self.client.post(
            f"{BASE_URL}",
            json={
                "pid" : 0,
                "condition": 10,
                "quantity": 2,
                "restock_level": 3,
                "active": 0,
                "name" : "testing"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_inventory_duplicate_time(self):
        """It should test the case where the item is already in the database"""
        test_item = InventoryFactory()
        test_item.create()
        response = self.client.post(BASE_URL, json=test_item.serialize())
        self.assertEqual(response.status_code, 409)
    
    def test_update_inventory_happy_path(self):
        """It should Update an existing Inventory item"""
        test_item = InventoryFactory()
        test_item.create()
        found_item = Inventory.find_by_pid_condition(test_item.pid, test_item.condition)
        self.assertEqual(found_item.pid, test_item.pid)
        response = self.client.put(
            f"{BASE_URL}/pid/{test_item.pid}/condition/{test_item.condition.value}",
            json={
                "name": "Test Name",
                "quantity": 2,
                "restock_level": 3,
                "active": 0,
            },
        )
        # Check if response code is valid
        self.assertEqual(response.status_code, 200)
        # Check if the data is indeed persisted in DB
        updated_item = Inventory.find_by_pid_condition(
            test_item.pid, test_item.condition
        )
        self.assertEqual(updated_item.pid, test_item.pid)
        self.assertEqual(updated_item.name, "Test Name")
        self.assertEqual(updated_item.quantity, 2)
        self.assertEqual(updated_item.restock_level, 3)
        self.assertEqual(updated_item.active.value, 0)

    def test_update_inventory_missing_value(self):
        """It should Throw an error for Missing Value"""
        test_item = InventoryFactory()
        test_item.create()
        found_item = Inventory.find_by_pid_condition(test_item.pid, test_item.condition)
        self.assertEqual(found_item.pid, test_item.pid)
        response = self.client.put(
            f"{BASE_URL}/pid/{test_item.pid}/condition/{test_item.condition.value}",
            json={"quantity": 2, "restock_level": 3, "active": 0},
        )
        # Check if response code is valid
        self.assertEqual(response.status_code, 400)
        # Check if the data has not been persisted
        updated_item = Inventory.find_by_pid_condition(
            test_item.pid, test_item.condition
        )
        self.assertEqual(updated_item.pid, test_item.pid)
        self.assertEqual(updated_item.name, test_item.name)
        self.assertEqual(updated_item.quantity, test_item.quantity)
        self.assertEqual(updated_item.restock_level, test_item.restock_level)
        self.assertEqual(updated_item.active, test_item.active)

    def test_update_inventory_bad_condition_id(self):
        """It should Throw an error for Erroneous Condition ID"""
        test_item = InventoryFactory()
        test_item.create()
        found_item = Inventory.find_by_pid_condition(test_item.pid, test_item.condition)
        self.assertEqual(found_item.pid, test_item.pid)
        response = self.client.put(
            f"{BASE_URL}/pid/{test_item.pid}/condition/10",
            json={
                "name": "Test Name",
                "quantity": 2,
                "restock_level": 3,
                "active": 0,
            },
        )
        # Check if response code is valid
        self.assertEqual(response.status_code, 400)
        # Check if the data has not been persisted
        updated_item = Inventory.find_by_pid_condition(
            test_item.pid, test_item.condition
        )
        self.assertEqual(updated_item.pid, test_item.pid)
        self.assertEqual(updated_item.name, test_item.name)
        self.assertEqual(updated_item.quantity, test_item.quantity)
        self.assertEqual(updated_item.restock_level, test_item.restock_level)
        self.assertEqual(updated_item.active, test_item.active)

    def test_update_inventory_no_item_present(self):
        """It should Throw an error for Invalid Combination of (PID, Condition ID)"""
        test_item = InventoryFactory()  # do not create this
        response = self.client.put(
            f"{BASE_URL}/pid/{test_item.pid}/condition/{test_item.condition.value}",
            json={
                "name": "Test Name",
                "quantity": 2,
                "restock_level": 3,
                "active": 0,
            },
        )
        # Check if response code is valid
        self.assertEqual(response.status_code, 404)
        # Check if the data has not been persisted
        updated_item = Inventory.find_by_pid_condition(
            test_item.pid, test_item.condition
        )
        self.assertEqual(updated_item, None)

    def test_update_inventory_invalid_content_type(self):
        """It should Throw an error for Invalid Content Type"""
        test_item = InventoryFactory()
        headers = {"content-type": "xml"}
        response = self.client.put(
            f"{BASE_URL}/pid/{test_item.pid}/condition/{test_item.condition.value}",
            headers=headers,
        )
        # Check if response code is valid
        self.assertEqual(response.status_code, 415)
        # Check if the data has not been persisted
        updated_item = Inventory.find_by_pid_condition(
            test_item.pid, test_item.condition
        )
        self.assertEqual(updated_item, None)

    def test_update_inventory_no_content_type(self):
        """It should Throw an error for No Content Type"""
        test_item = InventoryFactory()
        headers = {}
        response = self.client.put(
            f"{BASE_URL}/pid/{test_item.pid}/condition/{test_item.condition.value}",
            headers=headers,
        )
        # Check if response code is valid
        self.assertEqual(response.status_code, 415)
        # Check if the data has not been persisted
        updated_item = Inventory.find_by_pid_condition(
            test_item.pid, test_item.condition
        )
        self.assertEqual(updated_item, None)

    def test_delete_inventory(self):
        """It should Delete a Inventory item using pid + condition"""
        test_item = InventoryFactory()
        test_item.create()

        response = self.client.delete(
            f"{BASE_URL}/{test_item.pid}/condition/{test_item.condition.value}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            Inventory.find_by_pid_condition(test_item.pid, test_item.condition), None
        )
    
    def test_delete_inventories(self):
        """It should Delete a Inventory items using pid"""
        test_item = InventoryFactory()
        test_item2 = InventoryFactory()
        test_item.create()
        test_item2.pid = test_item.pid
        test_item2.condition = Condition((test_item.condition.value + 1)%3)
        test_item2.create()
        response = self.client.delete(
            f"{BASE_URL}/{test_item.pid}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            list(Inventory.find(test_item.pid)), []
        )

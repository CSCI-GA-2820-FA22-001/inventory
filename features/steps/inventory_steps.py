"""
Inventory Steps
Steps file for Pet.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given  # pylint: disable=no-name-in-module
from compare import expect

@given('the following items')
def step_impl(context):
    """ Delete all Previous Items and load new ones """
    # List all of the items and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/inventory"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for item in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{item['pid']}/{item['condition']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new pets
    for row in context.table:
        payload = {
            "pid": int(row['pid']),
            "condition": int(row['condition']),
            "name": row['name'],
            "quantity": int(row['quantity']),
            "restock_level": int(row['restock_level']),
            "active": eval(row['active'])
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)
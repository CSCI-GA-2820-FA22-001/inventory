"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyInteger, FuzzyText
from service.models import Inventory


class InventoryFactory(factory.Factory):
    """Creates fake items that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Inventory

    id = factory.Sequence(lambda n: n)
    name = factory.Faker('first_name')
    quantity = FuzzyInteger(1,10)
    description = FuzzyText(length=10)
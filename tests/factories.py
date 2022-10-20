"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyInteger, FuzzyText, FuzzyChoice
from service.models import Inventory, Condition


class InventoryFactory(factory.Factory):
    """Creates fake items that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Inventory

    pid = factory.Sequence(lambda n: n)
    condition = FuzzyChoice(choices=[Condition.NEW, Condition.OPEN_BOX, Condition.USED])
    name = FuzzyText(length=10)
    quantity = FuzzyInteger(1, 100)
    restock_level = FuzzyInteger(1, 100)
    available = FuzzyInteger(1, 100)

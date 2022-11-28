Feature: The inventory service back-end
    As a Inventory Manager
    I need a RESTful inventory service
    So that I can keep track of all my items

Background:
    Given the following items
        | pid       | condition | name      | quantity  | restock_level | active   |
        | 5         | 0         | Test1     | 1         | 10            | True     |       
        | 6         | 1         | Test2     | 2         | 11            | False    |
        | 7         | 2         | Test3     | 3         | 12            | True     |
        | 8         | 0         | Test4     | 4         | 13            | True     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all order data
    When I visit the "Home Page"
    And I press the "listAll" button
    Then I should see the message "Success"
    And I should see "Test1" in the results
    And I should see "5" in the results
    And I should see "Test2" in the results
    And I should see "6" in the results
    And I should see "Test3" in the results
    And I should see "7" in the results
    And I should see "Test4" in the results
    And I should see "8" in the results

Scenario: Don't list incorrect data
    When I visit the "Home Page"
    And I press the "listAll" button
    Then I should see the message "Success"
    And I should not see "Test5" in the results
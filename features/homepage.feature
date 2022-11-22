Feature: The inventory service back-end
    As a Inventory Manager
    I need a RESTful inventory service
    So that I can keep track of all my items

Background:
    Given the following items
        | pid       | condition | name      | quantity  | restock_level | active   |
        | 1         | 0         | Test1     | 1         | 10            | True     |       
        | 2         | 1         | Test2     | 2         | 11            | False    |
        | 3         | 2         | Test3     | 3         | 12            | True     |
        | 4         | 0         | Test4     | 4         | 13            | True     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory RESTful Service" in the title
    And I should not see "404 Not Found"
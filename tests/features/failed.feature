Feature: Feature contains failed scenario
  Scenario: Failed assertion with message scenario
    Given I want to calculate 3 and 4
    When Use addition operation
    Then Result is 6

  Scenario: Failed assertion without message scenario
    Given I want to calculate 3 and 4
    When Use addition operation
    Then Result is 6 but without message

  Scenario: Exception throwing scenario
    Given I want to calculate 3 and 0
    When Use division operation
    Then Result is 0

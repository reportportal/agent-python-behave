Feature: Report portal logging.
  Your feature description

  Scenario: Simple scenario
    When I want to calculate 2 and 2
    And use addition method
    Then result is 4

  Scenario: Scenario with step text description
    When I want to calculate 2 and 3
    """
    It means that number 2 will be taken from one side and number 3 from other
    """
    And use multiplication method
    Then result is 6
    But this step is for incorrect expected result

  Scenario: Scenario with step data table
    When I want to calculate numbers from table
      | number_a | number_b | expected |
      | 2        | 3        | 6        |
      | 5        | 4        | 20       |
    And use multiplication method
    Then all table data calculated correctly

  Scenario Outline: Scenario with examples
    When I want to calculate <number_a> and <number_b>
    And use multiplication method
    Then result is <expected>

    Examples: numbers data
      | number_a | number_b | expected |
      | 2        | 3        | 6        |
      | 3        | 3        | 8        |

  @skip
  Scenario: Log skipped scenario
    Skipping reason: issue #3153
    When I want to calculate 2 and 2
    And use addition method
    Then result is 4

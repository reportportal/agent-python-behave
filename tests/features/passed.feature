@first_feature_tag
@second_feature_tag
Feature: Calculator functionality
  Calculator should implement all basic arithmetic operations
  such as addition, subtraction, multiplication, division

  @first_scenario_tag
  @second_scenario_tag
  Scenario: Scenario with tags, scenario and step descriptions
    Sending of feature and scenario tags, feature and scenario description
    to report portal is covered by this scenario
    Given I want to calculate 2 and 3
    When Use addition operation
    """
    Addition operation is equivalent to '+'
    """
    Then Result is 5

  Scenario: Scenario with step data table
    Given I want to calculate two numbers

      | number_a | number_b | expected |
      | 2        | 3        | 6        |
      | 5        | 4        | 20       |
    When Use multiplication method
    Then Result should be correct

  Scenario Outline: Scenario with examples
    Given I want to calculate <number_a> and <number_b>
    When Use addition operation
    Then Result is <expected>

    Examples: numbers data
      | number_a | number_b | expected |
      | 2        | 3        | 5        |
      | 3        | 3        | 6        |

  @skip
  Scenario: Skipped scenario
    Skipping reason: some issue
    Given I want to calculate 2 and 2
    When Use addition operation
    Then Result is 4

#  Copyright (c) 2023 EPAM Systems
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License

from behave import given, then, when


@given("I want to calculate {number_a:d} and {number_b:d}")
def calculate_two_numbers(context, number_a, number_b):
    context.number_a = number_a
    context.number_b = number_b


@given("I want to calculate two numbers")
def calculate_two_numbers_from_table(context):
    context.test_data = [
        {
            "number_a": int(r["number_a"]),
            "number_b": int(r["number_b"]),
            "expected": int(r["expected"]),
        }
        for r in context.table.rows
    ]


@given("Some setup condition")
def some_setup_condition(context):
    pass


@when("Use addition operation")
def use_addition_operation(context):
    context.result = context.number_a + context.number_b


@when("Use multiplication method")
def use_multiplication_method(context):
    for row in context.test_data:
        row["actual"] = row["number_a"] * row["number_b"]


@when("Use division operation")
def use_division_operation(context):
    context.result = context.number_a / context.number_b


@then("Result is {result:d}")
def result_is(context, result):
    assert (
        context.result == result
    ), f"Incorrect result:\nActual: {context.result}\nExpected: {result}"


@then("Result is {result:d} but without message")
def result_is_without_message(context, result):
    assert context.result == result


@then("Result should be correct")
def result_should_be_correct(context):
    for row in context.test_data:
        assert row["actual"] == row["expected"], (
            f"Incorrect result:\n"
            f"Actual: {row['actual']}\n"
            f"Expected: {row['expected']}"
        )

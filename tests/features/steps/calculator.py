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


@then("Result is {result:d}")
def result_is(context, result):
    assert (
        context.result == result
    ), "Incorrect result:\nActual: {actual}\nExpected: {expected}".format(
        actual=context.result, expected=result
    )


@then("Result should be correct")
def result_should_be_correct(context):
    for row in context.test_data:
        assert (
            row["actual"] == row["expected"]
        ), "Incorrect result:\nActual: {actual}\nExpected: {expected}".format(
            actual=row["actual"], expected=row["expected"]
        )

from behave import use_step_matcher, step, when, then

use_step_matcher("re")


@when('I want to calculate (?P<number_a>\d) and (?P<number_b>\d)')
def step_impl(context, number_a, number_b):
    context.number_a = int(number_a)
    context.number_b = int(number_b)


@step('use addition method')
def use_addition_method(context):
    context.result = context.number_a + context.number_b


@then('result is (?P<expected_result>\d)')
def result_assertion(context, expected_result):
    assert context.result == int(expected_result), 'Result is incorrect\nExpected: {}\nGot: {}'.format(expected_result,
                                                                                                       context.result)


@step('use multiplication method')
def use_multiplication_method(context):
    if 'input_data' in context:
        for i in context.input_data:
            i['actual'] = i['a'] * i['b']
    else:
        context.result = context.number_a * context.number_b


@step('this step is for incorrect expected result')
def step_impl(context):
    assert context.result == 7, 'Result is incorrect\nExpected: {}\nGot: {}'.format(7, context.result)


@then("all table data calculated correctly")
def step_impl(context):
    for i in context.input_data:
        assert i['expected'] == i['actual'], 'Result is incorrect\nExpected: {}\nGot: {}'.format(i['expected'],
                                                                                                 i['actual'])


@when("I want to calculate numbers from table")
def step_impl(context):
    step_table = context.table
    context.input_data = []
    for row in step_table:
        data = {
            'a': int(row['number_a']),
            'b': int(row['number_b']),
            'expected': int(row['expected'])
        }
        context.input_data.append(dict(data))

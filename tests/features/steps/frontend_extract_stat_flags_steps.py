# Import dependencies
from frontend import extract_stat_flags
from behave import given, when, then
import ast

@given('the metrics collection contains {metrics}')
def step_given_metrics(context, metrics):
    # Convert string representation of list from feature file to actual list
    context.metrics = ast.literal_eval(metrics)

@when('I extract the statistic flags')
def step_when_extract_flags(context):
    # Collect expected result
    context.flags = extract_stat_flags(context.metrics)

@then('the flags should be {expected_flags}')
def step_then_check_flags(context, expected_flags):
    # Evaluate expected result and assert the value matches generate result
    expected = ast.literal_eval(expected_flags)
    assert context.flags == tuple(expected), f"Expected {expected}, but got {context.flags}"

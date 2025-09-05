# Import dependencies
from frontend import aggregate_fairway_data
from behave import given, when, then
import ast

@given('the hole-level data contains {data}')
def step_given_hole_data(context, data):
    # Convert string representation of list of dicts into actual Python list
    context.data = ast.literal_eval(data)

@when('I aggregate the fairway data')
def step_when_aggregate(context):
    # Collect result from input data
    context.result_df = aggregate_fairway_data(context.data)

@then('the result should have fairways in order Left, Target, Right')
def step_then_check_order(context):
    # Define expected order
    expected_order = ["Left", "Target", "Right"]

    # Collect actual order
    actual_order = context.result_df["Fairway"].cat.categories.tolist()

    # Assert both sets of data to ensure data order is correct
    assert actual_order == expected_order, f"Expected order {expected_order}, but got {actual_order}"

@then('the counts should be {expected_counts}')
def step_then_check_counts(context, expected_counts):
    # Evaluate expression
    expected = ast.literal_eval(expected_counts)

    # Map the counts to Left, Target, Right
    counts_dict = context.result_df.set_index("Fairway")["Count"].to_dict()
    actual_counts = [counts_dict.get(fw, 0) for fw in ["Left", "Target", "Right"]]

    # Assert output, ensure it matches expected result
    assert actual_counts == expected, f"Expected counts {expected}, but got {actual_counts}"

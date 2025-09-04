@frontend
Feature: Aggregate fairway data
    As a golf analyst
    I want to count fairway outcomes and maintain a Left-Target-Right order
    So that I can summarize fairway accuracy consistently

    Scenario Outline: Aggregate fairway outcomes
        Given the hole-level data contains <data>
        When I aggregate the fairway data
        Then the result should have fairways in order Left, Target, Right
        And the counts should be <expected_counts>

        Examples:
            | data                                                                  | expected_counts |
            | [{"Fairways": "Left"}, {"Fairways": "Right"}, {"Fairways": "Target"}] | [1, 1, 1]       |
            | [{"Fairways": "Left"}, {"Fairways": "Left"}, {"Fairways": "Target"}]  | [2, 1, 0]       |
            | [{"Fairways": "Right"}, {"Fairways": "Right"}]                        | [0, 0, 2]       |

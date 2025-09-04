@frontend
Feature: Extract statistic flags from metrics
    As a data analyst
    I want to know if minimum, maximum, and average statistics are present
    So that I can handle metrics correctly

    Scenario Outline: Check presence of Min, Max, and Avg stats
        Given the metrics collection contains <metrics>
        When I extract the statistic flags
        Then the flags should be <expected_flags>

        Examples:
            | metrics                                 | expected_flags        |
            | ["Min Stats", "Max Stats", "Avg Stats"] | [True, True, True]    |
            | ["Min Stats"]                           | [True, False, False]  |
            | ["Max Stats"]                           | [False, True, False]  |
            | ["Avg Stats"]                           | [False, False, True]  |
            | ["Min Stats", "Avg Stats"]              | [True, False, True]   |
            | []                                      | [False, False, False] |

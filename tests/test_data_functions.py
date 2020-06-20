""" Test file for data_functions.py"""
from codes.data_function import pre_master_data
from codes.data_function import pre_forecast_data
from codes.data_function import top_forecast
from codes.data_function import merge_forecast_top_priority, accuracy
import pandas as pd
import math


master_df = pd.read_csv('/database/small_master.csv')
forecast_df = pd.read_csv('/database/small_forecast.csv')


def check_approx_equals(expected, received):
    """
    Checks received against expected, and returns whether or
    not they match (True if they do, False otherwise).
    If the argument is a float, will do an approximate check.
    If the arugment is a data structure will do an approximate check
    on all of its contents.
    """
    try:
        if type(expected) == dict:
            # first check that keys match, then check that the
            # values approximately match
            return expected.keys() == received.keys() and \
                all([check_approx_equals(expected[k], received[k])
                    for k in expected.keys()])
        elif type(expected) == list or type(expected) == set:
            # Checks both lists/sets contain the same values
            return len(expected) == len(received) and \
                all([check_approx_equals(v1, v2)
                    for v1, v2 in zip(expected, received)])
        elif type(expected) == float:
            return math.isclose(expected, received, abs_tol=0.001)
        else:
            return expected == received
    except Exception as e:
        print(f'EXCEPTION: Raised when checking check_approx_equals {e}')
        return False


def assert_equals(expected, received):
    """
    Checks received against expected, throws an AssertionError
    if they don't match. If the argument is a float, will do an approximate
    check. If the arugment is a data structure will do an approximate check
    on all of its contents.
    """
    assert check_approx_equals(expected, received), \
        f'Failed: Expected {expected}, but received {received}'


def test_pre_master_data():
    assert_equals('2016-05-01 20:00:00', str(pre_master_data(master_df)['ts'].iloc[0]))
    assert_equals('2016-05-02 21:00:00', str(pre_master_data(master_df)['ts'].iloc[1]))
    assert_equals('2016-05-03 20:00:00', str(pre_master_data(master_df)['ts'].iloc[2]))


def test_pre_forecast_data():
    assert_equals(0.0025, (pre_forecast_data(forecast_df)['forecast'].iloc[0]))
    assert_equals(0, (pre_forecast_data(forecast_df)['forecast'].iloc[1]))
    assert_equals(0.005, (pre_forecast_data(forecast_df)['forecast'].iloc[2]))


def test_top_forecast():
    assert_equals(100.0, (top_forecast('2016-09-07 17:00:00', 3, forecast_df)))
    assert_equals(44, (top_forecast('2016-08-10 18:00:00', 3, forecast_df)))
    assert_equals(0, (top_forecast('2016-08-25 16:00:00', 3, forecast_df)))


def test_merge_forecast_top_priority():
    assert_equals(21, (merge_forecast_top_priority(master_df, forecast_df)['hour_ending_eastern'].iloc[0]))
    assert_equals(20, (merge_forecast_top_priority(master_df, forecast_df)['hour_ending_eastern'].iloc[1]))
    assert_equals(21, (merge_forecast_top_priority(master_df, forecast_df)['hour_ending_eastern'].iloc[2]))


def test_accuracy():
    assert_equals(100, (accuracy(master_df, forecast_df)['performance'].iloc[0]))
    assert_equals(81, (accuracy(master_df, forecast_df)['performance'].iloc[1]))
    assert_equals(78, (accuracy(master_df, forecast_df)['performance'].iloc[2]))


def mains():
    test_pre_master_data()
    test_pre_forecast_data()
    test_merge_forecast_top_priority()
    test_top_forecast()
    test_accuracy()


if __name__ == '__main__':
    mains()

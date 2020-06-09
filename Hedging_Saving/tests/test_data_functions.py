""" Test file for data_functions.py"""
from data_function import *
import pandas as pd
import math


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


def test_pre_master_dataset():
    assert_equals('2016-05-01 20:00:00', str(pre_master_dataset(test_master)['ts'].iloc[0]))
    assert_equals('2016-05-02 21:00:00', str(pre_master_dataset(test_master)['ts'].iloc[1]))
    assert_equals('2016-05-03 20:00:00', str(pre_master_dataset(test_master)['ts'].iloc[2]))


def test_pre_forecast_dataset():
    assert_equals(0.0025, (pre_forecast_dataset(test_forecast)['forecast'].iloc[0]))
    assert_equals(0, (pre_forecast_dataset(test_forecast)['forecast'].iloc[1]))
    assert_equals(0.005, (pre_forecast_dataset(test_forecast)['forecast'].iloc[2]))


def test_extract_topN_forecast():
    assert_equals(100.0, (extract_topN_forecast('2016-09-07 17:00:00', 3)))
    assert_equals(44, (extract_topN_forecast('2016-08-10 18:00:00', 3)))
    assert_equals(0, (extract_topN_forecast('2016-08-25 16:00:00', 3)))


def test_merge_forecast_top_priority():
    assert_equals(21, (merge_forecast_top_priority(test_master,test_forecast)['hour_ending_eastern'].iloc[0]))
    assert_equals(20, (merge_forecast_top_priority(test_master,test_forecast)['hour_ending_eastern'].iloc[1]))
    assert_equals(21, (merge_forecast_top_priority(test_master,test_forecast)['hour_ending_eastern'].iloc[2]))


def test_Accuracy():
    assert_equals(100,(Accuracy(test_master,test_forecast)['percentage'].iloc[0]))
    assert_equals(81,(Accuracy(test_master,test_forecast)['percentage'].iloc[1]))
    assert_equals(78,(Accuracy(test_master,test_forecast)['percentage'].iloc[2]))


def main():
    test_master = pd.read_csv('samples/small_master.csv')
    test_forecast = pd.read_csv('samples/small_forecast.csv')
    test_pre_master_dataset()
    test_pre_forecast_dataset()
    test_merge_forecast_top_priority()
    test_extract_topN_forecast()
    test_Accuracy()


if __name__ == '__main__':
    main()

""" Test file for data_functions.py"""
from Hedging_Saving.data_function import *
import unittest
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import pytest
import numpy as np
from pandas.core.frame import DataFrame


def test_pre_master_dataset():
    """ Check for csv file"""
    master_df = pd.read_csv('/samples/small_master.csv')

    try:
        data_function.pre_master_dataset(master_df)
        raise Exception()
    except ValueError:
        pass


def test_pre_forecast_dataset():
    """ Check for csv file"""
    forecast_df = pd.read_csv('/samples/small_forecast.csv')
    try:
        data_function.pre_forecast_dataset(forecast_df)
        raise Exception()
    except ValueError:
        pass


def test_merge_forecast_top_priority():
    """ Check for two merge csv file"""
    master_df = pd.read_csv('/samples/small_master.csv')
    forecast_df = pd.read_csv('/samples/small_forecast.csv')
    try:
        data_function.merge_forecast_top_priority(master_df, forecast_df)
        raise Exception()
    except ValueError:
        pass


def test_extract_topN_forecast():
    """ Check for int probability"""
    ts = '2019-07-19 12:00:00'
    n = 12
    try:
        data_function.extract_topN_forecast(ts, n)
        raise Exception()
    except ValueError:
        pass


def test_Accuracy():
    """ Check for new df"""
    master_df = pd.read_csv('/samples/small_master.csv')
    forecast_df = pd.read_csv('/samples/small_forecast.csv')
    try:
        data_function.Accuracy(master_df, forecast_df)
        raise Exception()
    except ValueError:
        pass
    
    
# def main():
#     test_pre_master_dataset()
#     test_ pre_forecast_dataset()
#     test_merge_forecast_top_priority()
#     test_extract_topN_forecast()
#     test_Accuracy()
    
    
# if __name__ == '__main__':
#     main()

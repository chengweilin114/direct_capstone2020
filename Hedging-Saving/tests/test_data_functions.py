""" Test file for data_functions.py"""
from Hedging-Saving import data_functions
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
from pandas.core.frame import DataFrame


def test_pre_master_dataset():
    """ Check for csv file"""
    master_df = pd.read_csv('small_master_dataset.csv')

    try:
        data_functions.pre_master_dataset(master_df)
        raise Exception()
    except ValueError:
        pass
  
def test_ pre_forecast_dataset():
    """ Check for csv file"""
    forecast_df = pd.read_csv('small_forecasts_top_12.csv')
    try:
        data_functions.pre_forecast_dataset(forecast_df)
        raise Exception()
    except ValueError:
        pass
        
def test_merge_forecast_top_priority():
    """ Check for two merge csv file"""
    master_df = pd.read_csv('small_master_dataset.csv')
    forecast_df = pd.read_csv('small_forecasts_top_12.csv')
    try:
        data_functions.merge_forecast_top_priority(master_df, forecast_df)
        raise Exception()
    except ValueError:
        pass

      

import pandas as pd
from dataloader import dataloader
from summarize import get_actual_peaks, get_top_n_peaks
from summarize import summarize_top_n, summarize

def test_get_actual_peaks():
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    # Test get_actual_peaks
    actual_peaks = get_actual_peaks(actual_load)

    assert isinstance(actual_peaks, pd.DataFrame)


def test_get_top_n_peaks():
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    # Test get_actual_peaks
    actual_peaks = get_actual_peaks(actual_load)

    # Test get_top_n_peaks
    top_n_actual_peaks = get_top_n_peaks(actual_peaks, 1)

    assert isinstance(top_n_actual_peaks, pd.DataFrame)


def test_summarize_top_n():
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    # Test get_actual_peaks
    actual_peaks = get_actual_peaks(actual_load)

    top_n_results, top_n_sum = summarize_top_n(actual_peaks, forecasts, 1)

    assert isinstance(top_n_results, pd.DataFrame)
    assert isinstance(top_n_sum, pd.DataFrame) or isinstance(top_n_sum, pd.Series)

def test_summarize():
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    # Test get_actual_peaks
    actual_peaks = get_actual_peaks(actual_load)

    summary = summarize(actual_peaks, forecasts, save_path='')

    assert isinstance(summary, pd.DataFrame)

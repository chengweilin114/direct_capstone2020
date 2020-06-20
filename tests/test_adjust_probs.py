import pandas as pd
from dataloader import dataloader
from summarize import get_actual_peaks, summarize_top_n
from adjust_probs import get_top_n_forecasts, adjust_probs


def test_get_top_n_forecasts():
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    n_probs_to_use = 3
    top_n_forecasts = get_top_n_forecasts(forecasts, n_probs_to_use)

    assert isinstance(top_n_forecasts, pd.DataFrame)


def test_adjust_probs():
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    n_peaks_to_use = 1
    n_probs_to_use = 3

    # Get top n forecasts
    top_n_forecasts = get_top_n_forecasts(forecasts, n_probs_to_use)

    # Get actual peaks
    actual_peaks = get_actual_peaks(actual_load)

    # Get top n results
    top_n_results, _ = summarize_top_n(actual_peaks, forecasts, n_peaks_to_use)

    # Get top n adjusted probabilities
    top_n_adjusted = adjust_probs(top_n_results, 
                                  top_n_forecasts, 
                                  n_peaks_to_use, 
                                  n_probs_to_use)

    assert isinstance(top_n_adjusted, pd.DataFrame)


test_get_top_n_forecasts()
test_adjust_probs()
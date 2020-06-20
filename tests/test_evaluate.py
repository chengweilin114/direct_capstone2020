import pandas as pd
from dataloader import dataloader
from summarize import get_actual_peaks, summarize_top_n
from adjust_probs import get_top_n_forecasts, adjust_probs
from evaluate import get_top_n_report, get_report


def test_get_top_n_report():

    mapper = {}
    attr_keys = ['Season', 'Top_n_peaks', 'Top_n_probs', 'HitRate(%)', 'Performance(%)']
    hour_keys = ['12', '15', '16', '17', '18', '19', '20']
    keys = attr_keys + hour_keys
    for key in keys:
        mapper[key] = []

    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_12.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    n_peaks_to_use = 1
    n_probs_to_use = 4

    actual_peaks = get_actual_peaks(actual_load)
    top_n_forecasts = get_top_n_forecasts(forecasts, n_probs_to_use)

    top_n_results, _ = summarize_top_n(actual_peaks, forecasts, n_peaks_to_use)
    top_n_adjusted = adjust_probs(top_n_results, 
                                  top_n_forecasts, 
                                  n_peaks_to_use, 
                                  n_probs_to_use)

    # Update mapper with each season
    mapper = get_top_n_report(top_n_results, 
                              top_n_adjusted, 
                              n_peaks_to_use, 
                              n_probs_to_use,
                              hour_keys,
                              mapper)

    assert isinstance(mapper, dict)


def test_get_report():

    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_12.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    n_probs_to_use = 4

    # Generate report as dataframe
    report_df = get_report(actual_load, forecasts, n_probs_to_use)

    assert isinstance(report_df, pd.DataFrame)


test_get_top_n_report()
test_get_report()
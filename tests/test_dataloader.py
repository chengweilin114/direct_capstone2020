import pandas as pd
# from ..codes.dataloader import dataloader
from dataloader import dataloader

def test_dataloader():
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    assert isinstance(actual_load, pd.DataFrame)

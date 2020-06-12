import pandas as pd
import datetime


# Load actual demand data and forecasting results
def dataloader(fname1, fname2):

    """
    Arguments:
        fname1:
            A string. The file name for the actual demand data.

        fname2:
            A string. The file name for the forecasts.

    Return:
        Two dataframes. The first one is the actual demand data.
        The second one is the forecasts.

    This function takes the file names as input and return the
    actual demand data and the forecasts.

    """

    load_df = pd.read_csv(fname1)
    load_df.rename(columns={'timestamp_eastern': 'ts'}, inplace=True)
    load_df['ts'] = pd.to_datetime(load_df['ts'])

    forecasts_df = pd.read_csv(fname2, index_col=False)
    forecasts_df['ts'] = pd.to_datetime(forecasts_df['ts'])
    forecasts_df['ts_future'] = pd.to_datetime(forecasts_df['ts_future'])

    # Use the forecasts made at 10:00 am on each day
    mask = forecasts_df.ts.dt.time == datetime.time(10, 0)
    forecasts_df = forecasts_df[mask]

    forecasts_df = forecasts_df[['ts_future', 'forecast']]
    forecasts_df = forecasts_df.rename(columns={'ts_future': 'ts'})

    return load_df, forecasts_df


if __name__ == '__main__':
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    print('Actual load data:')
    print(actual_load.head(10))

    print('Forecasting results:')
    print(forecasts.head(10))

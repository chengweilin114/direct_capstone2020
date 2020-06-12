import pandas as pd
import datetime
from dataloader import dataloader


def get_actual_peaks(load_df):

    """
    Arguments:
        load_df: The entire actual demand datasets.

    Return:
        peaks_df: Keep the highest demand for each day.

    This function keeps the highest demand (the peak hour)
    for each day.

    """

    # Create a new column to hold rankings in a day
    rankings = load_df.groupby(['season',
                               load_df.ts.dt.date]
                               ).adjusted_demand_MW.rank(ascending=False)
    load_df['rankings_per_day'] = rankings

    mask = load_df['rankings_per_day'] == 1.0
    peaks_df = load_df[mask]

    # Reset index
    peaks_df.reset_index(drop=True, inplace=True)

    return peaks_df


def get_top_n_peaks(peaks_df, n_peaks_to_use):

    """
    Arguments:
        peaks_df: 
            A dataframe. The peak hours for each day.

        n_peaks_to_use: 
            An int. Number of top peaks to use in each season.

    Return:
        A dataframe. The top n_peaks_to_use peaks in each
        season.

    This function keeps the top n_peaks_to_use peak hours in 
    each season.

    """

    # Create a new column to hold rankings in a year
    rankings = peaks_df.groupby(['season']
                                ).adjusted_demand_MW.rank(ascending=False)
    peaks_df['rankings_per_season'] = rankings

    mask = peaks_df['rankings_per_season'] <= float(n_peaks_to_use)
    top_n_peaks = peaks_df[mask]

    return top_n_peaks


def summarize_top_n(peaks_df, forecasts, n_peaks_to_use):

    """
    Arguments:
        peaks_df:
            A dataframe. The peak hours for each day.

        forecasts:
            A dataframe. The entire forecasting results.

        n_peaks_to_use:
            An int. Number of top peaks to use in each season

    Return:
        Two DataFrames. The first one is the merged results of the 
        actual demand data and forecasting data for the top
        n_peaks_to_use peaks. The second one is the summary of 
        success rates for the forecasts.

    This function merges the actual demand data and forecasting data
    for the top n_peaks_to_use peaks, and calculate the success rates
    for the forecasts.

    """

    columns_to_keep = ['adjusted_demand_MW',
                       'demand_MW',
                       'season',
                       'ts',
                       'rankings_per_day',
                       'rankings_per_season']

    top_n_peaks = get_top_n_peaks(peaks_df, n_peaks_to_use)

    top_n_peaks = top_n_peaks[columns_to_keep]

    top_n_results = pd.merge(top_n_peaks, forecasts, on='ts')

    df = top_n_results.groupby(['season'])
    top_n_sum = df.forecast.apply(lambda x: (x > 0).sum())

    return top_n_results, top_n_sum


def summarize(peaks_df, forecasts, save_path):

    """
    Arguments:
        peaks_df:
            A dataframe. The peak hours for each day.

        forecasts:
            A dataframe. The entire forecasting results.

        save_path:
            A string. The path to save the summary of forecasts.

    Return:
        A DataFrame. The summary of success rates for the forecasts.

    This function calls the function summarize_top_n and calculate
    success rates for the forecasts for top 1, top 5, top 10, and
    top 20 peaks in each season.

    """

    mapper = {}
    keys_list1 = ['Season', 'Success(%)', 'Top_n']
    keys_list2 = ['12', '16', '17', '18', '19', '20']
    keys = keys_list1 + keys_list2
    for key in keys:
        mapper[key] = []

    for n in [1, 5, 10, 20]:
        top_n_results, top_n_sum = summarize_top_n(peaks_df, forecasts, n)
        seasons = top_n_sum.index.values

        for s in seasons:
            mapper['Season'].append(s)
            succ_rate = int(top_n_sum.loc[s]/n*100)
            mapper['Success(%)'].append(succ_rate)
            mapper['Top_n'].append(n)

            mask = top_n_results.season == s
            season_df = top_n_results[mask]

            for key in keys_list2:
                mask = season_df.ts.dt.time == datetime.time(int(key), 0)
                hour_df = season_df[mask]
                total_num = hour_df.shape[0]
                num_hit = hour_df.forecast.gt(0).sum()

                mapper[key].append(str(num_hit)+'/'+str(total_num))

    summary = pd.DataFrame(data=mapper)
    summary.to_csv(save_path+'Summary.csv')

    return summary


if __name__ == '__main__':
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    # Test get_actual_peaks
    actual_peaks = get_actual_peaks(actual_load)

    print('Actual peaks:')
    print(actual_peaks.head(3))

    # Test get_top_n_peaks
    top_n_actual_peaks = get_top_n_peaks(actual_peaks, top_n_to_use=1)

    print('Top n actual peaks:')
    print(top_n_actual_peaks.head(3))

    # Summarize actual peaks and forecasts
    # forecasts = forecasts[['ts_future', 'forecast']]
    # forecasts = forecasts.rename(columns={'ts_future': 'ts'})
    mapper = {}

    top_n_results, top_n_sum = summarize_top_n(actual_peaks, forecasts, 1)

    print('Top n results:')
    print(top_n_results.head(3))

    print('Top n summary:')
    print(top_n_sum.head(3))

    summary = summarize(actual_peaks, forecasts, save_path='')

    print('Summary:')
    print(summary.head(5))

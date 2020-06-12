import pandas as pd
import datetime
from dataloader import dataloader
from summarize import get_actual_peaks, get_top_n_peaks, summarize_top_n


def get_top_n_forecasts(forecasts, n_probs_to_use):

    """
    Arguments:
        forecasts:
            A dataframe. The entire forecasting results.

        n_probs_to_use:
            Number of top probabilities to use on each day

    Return:
        A DataFrame. The largest n_probs_to_use forecasting 
        probabilities on each day.

    This function keep the largest n forecasting probabilities
    for each day.

    """

    # Select forecasts with prob. > 0.
    mask = forecasts.forecast >0.
    pos_forecasts = forecasts[mask]

    df = pos_forecasts.groupby([pos_forecasts.ts.dt.date])
    rankings = df.forecast.rank(ascending=False, method='dense')
    pos_forecasts['prob_rankings_per_day'] = rankings

    # Keep the largest n_probs_to_use probs.
    mask = pos_forecasts['prob_rankings_per_day'] <= n_probs_to_use
    top_n_forecasts = pos_forecasts[mask]

    # Reset index
    top_n_forecasts.reset_index(drop=True, inplace=True)

    return top_n_forecasts


def adjust_probs(top_n_results, top_n_forecasts, n_peaks_to_use, n_probs_to_use):

    """
    Arguments:
        top_n_results:
            A DataFrame. Ground-truth demands for top 
            n_peaks_to_use peak days.

        top_n_forecasts:
            A DataFrame. Adjusted forecasting probabilities for top 
            n_peaks_to_use peak days.

        n_peaks_to_use:
            An int. Number of top peaks to use in each season

        n_probs_to_use:
            An int. Number of top probabilities to use on each day

    Return:
        A DataFrame. Adjusted forecasting probabilities for top 
        n_peaks_to_use peak days.


    This function adjust the forecasting probabilities in 
    top_n_forecasts to have them sum up to one on each day.
    Also calculate the discharging rates for each peak day.

    """

    dates = top_n_results.ts.dt.date.values
    frames = []
    for day in dates:
        # Select current day's peak hour information
        mask = top_n_results.ts.dt.date == day
        daily_results = top_n_results[mask]

        true_peak = daily_results.ts.dt.time.values[0]
        season = daily_results.season.values[0]

        # Select the forecasts for current day
        mask = top_n_forecasts.ts.dt.date == day
        daily_forecasts = top_n_forecasts[mask]

        mask = daily_forecasts.ts.dt.time == true_peak
        daily_forecasts['is_true_peak'] = mask.astype(int)

        # Adjust probs to sum up to one
        total_probs = daily_forecasts['forecast'].sum()
        adjusted_probs = daily_forecasts['forecast']/total_probs
        daily_forecasts['adjusted_prob'] = round(adjusted_probs, 2)

        # Discharge in proportional to probs.
        # i.e., prob = 0.3, then discharge 30% out of 0.5 capacity
        # 0.3/0.5
        discharge_rate = daily_forecasts['adjusted_prob']/0.5
        daily_forecasts['discharge_rate'] = round(discharge_rate, 2)

        daily_forecasts['season'] = season

        daily_forecasts['top_n'] = n_peaks_to_use

        mask = daily_forecasts.adjusted_prob > 0.5
        be_adjusted = daily_forecasts[mask]

        if not be_adjusted.empty:
            # For each day, at most one and only one prob. > 0.5
            cur = be_adjusted.index.values[0]
            daily_forecasts.at[cur, 'adjusted_prob'] = 0.5
            daily_forecasts.at[cur, 'discharge_rate'] = 0.5/0.5

            for row in daily_forecasts.index.values:
                if row != cur:
                    prob_ = 0.5/(n_probs_to_use-1)
                    daily_forecasts.at[row, 'adjusted_prob'] = round(prob_, 2)
                    # Spread out the remaining 0.5 capacity evenly
                    rate_ = (0.5/(n_probs_to_use-1))/0.5
                    daily_forecasts.at[row, 'discharge_rate'] = round(rate_, 2)

        frames.append(daily_forecasts)
    top_n_adjusted = pd.concat(frames)
 
    return top_n_adjusted


if __name__ == '__main__':
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_2.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    n_peaks_to_use = 1
    n_probs_to_use = 3

    n_probs = forecasts_fname.split('_')[3].split('.')[0]
    n_probs = int(n_probs)
    if n_probs_to_use > n_probs:
        print('n_probs_to_use must not exceed n_probs!')
        n_probs_to_use = n_probs

    # Get top n forecasts
    top_n_forecasts = get_top_n_forecasts(forecasts, n_probs_to_use)
    print('Top n forecasts:')
    print(top_n_forecasts.head(3))

    # Get actual peaks
    actual_peaks = get_actual_peaks(actual_load)

    # Get top n results
    top_n_results, _ = summarize_top_n(actual_peaks, forecasts, n_peaks_to_use)

    # Get top n adjusted probabilities
    top_n_adjusted = adjust_probs(top_n_results, 
                                  top_n_forecasts, 
                                  n_peaks_to_use, 
                                  n_probs_to_use)
    print('Top n adjusted:')
    print(top_n_adjusted.head(3))

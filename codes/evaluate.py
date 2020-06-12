import pandas as pd
import datetime
from dataloader import dataloader
from summarize import get_actual_peaks, get_top_n_peaks, summarize_top_n
from adjust_probs import get_top_n_forecasts, adjust_probs
from utils import percent_to_str


def get_top_n_report(top_n_results, 
                     top_n_adjusted, 
                     n_peaks_to_use, 
                     n_probs_to_use,
                     hour_keys,
                     mapper):

    """
    Arguments:
        top_n_results: 
            A DataFrame. Ground-truth demands for top 
            n_peaks_to_use peak days.

        top_n_adjusted: 
            A DataFrame. Adjusted forecasting probabilities for top 
            n_peaks_to_use peak days.

        n_peaks_to_use: 
            An int. Number of top peaks to use in each season

        n_probs_to_use:
            An int. Number of top probabilities to use on each day

        hour_keys:
            A list. Hours at which we evaluate the discharging strategy

        mapper:
            A dictionary. Keep track of perforamance for each season

    Return:
        A dictionary. The data of the performance report for 
        top n_peaks_to_use peak days.

    This function generates the performance report for the top 
    n_peaks_to_use peak days.

    """

    seasons = set(top_n_results.season.values)
    for s in seasons:
        # The season 2019-2020 only has 10 top peaks to use
        if s == '2019-2020' and n_peaks_to_use > 10:
            continue
        mapper['Season'].append(s)
        mapper['Top_n_peaks'].append(n_peaks_to_use)
        mapper['Top_n_probs'].append(n_probs_to_use)

        mask = top_n_results.season == s
        season_results = top_n_results[mask]
        # season_results.to_csv('season_results.csv')

        mask = top_n_adjusted.season == s
        season_adjusted = top_n_adjusted[mask]
        # season_adjusted.to_csv('season_adjusted.csv')

        season_hits = pd.merge(season_results, season_adjusted, how='inner', on=['ts'])
        # season_hits.to_csv('season_hits.csv')
        total_num_hit = season_hits.shape[0]
        
        total_discharge = 0.
        for hour in hour_keys:
            mask = season_adjusted.ts.dt.time == datetime.time(int(hour),0)
            hour_adjusted = season_adjusted[mask]
            # hour_adjusted.to_csv('hour_adjusted.csv')

            mask =  season_results.ts.dt.time == datetime.time(int(hour),0)
            hour_results = season_results[mask]
            # hour_results.to_csv('hour_results.csv')

            hour_hits = pd.merge(hour_results, hour_adjusted, how='inner', on=['ts'])
            hour_hits.drop(['season_y'], axis=1, inplace=True)
            hour_hits.drop(['forecast_y'], axis=1, inplace=True)
            # hour_hits.to_csv('hour_hits.csv')

            # Number of ground truth peaks at this hour
            num_true = hour_results.shape[0]

            # Number of true peaks which appear in forecasts at this hour
            num_hit = hour_hits.shape[0]

            # avg_percent is the average discharge rate at this hour
            if num_hit > 0:
                avg_percent = hour_hits.discharge_rate.mean()
                avg_percent = avg_percent * 100
                avg_percent = round(avg_percent, 0)
            else:
            	avg_percent = 0.0
                
            pct = percent_to_str(num_hit, num_true, avg_percent)
            mapper[hour].append(pct)

            # Accumulate discharge rates over all hours for this season
            total_discharge += hour_hits.discharge_rate.sum()

        # End visiting hours
        p = total_num_hit / n_peaks_to_use
        percent = round(p * 100, 0)
        hit_rate = percent_to_str(total_num_hit, n_peaks_to_use, percent)
        mapper['HitRate(%)'].append(hit_rate)

        avg_discharge = total_discharge / n_peaks_to_use
        avg_discharge = round(avg_discharge * 100, 0)
        mapper['Performance(%)'].append(avg_discharge)

    # End season
    return mapper 


def get_report(actual_load, forecasts, n_probs_to_use):

    """
    Arguments:
        actual_load:
            A dataframe. The entire ground-truth demands.

        forecasts:
            A dataframe. The entire forecasting results.

        n_probs_to_use:
            Number of top probabilities to use on each day

    Return:
        A dataframe. The performance report.

    This function generates the performance reports for top 
    1, top 5, top 10, and top 20 peak days.

    """

    mapper = {}
    attr_keys = ['Season', 'Top_n_peaks', 'Top_n_probs', 'HitRate(%)', 'Performance(%)']
    hour_keys = ['12', '15', '16', '17', '18', '19', '20']
    keys = attr_keys + hour_keys
    for key in keys:
        mapper[key] = []

    actual_peaks = get_actual_peaks(actual_load)
    top_n_forecasts = get_top_n_forecasts(forecasts, n_probs_to_use)

    for n_peaks_to_use in [1, 3, 5, 10, 20]:

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

    report_df = pd.DataFrame(data=mapper)

    return report_df


if __name__ == '__main__':
    actual_load_fname = 'ieso_ga_master_dataset_allWeather_updated2020.csv'
    forecasts_fname = 'ga_forecasts_top_12.csv'

    actual_load, forecasts = dataloader(actual_load_fname, forecasts_fname)

    n_peaks_to_use = 1
    n_probs_to_use = 4

    n_probs = forecasts_fname.split('_')[3].split('.')[0]
    n_probs = int(n_probs)
    if n_probs_to_use > n_probs:
        print('n_probs_to_use must not exceed n_probs!')
        n_probs_to_use = n_probs

    hour_keys = ['12', '15', '16', '17', '18', '19', '20']

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


    # Generate report as dataframe
    report_df = get_report(actual_load, forecasts, n_probs_to_use)
    print('Report:')
    print(report_df.head(3))

    report_df.to_csv('report_probs_to_use_{}.csv'.format(str(n_probs_to_use)))

""" Test file for data_functions.py"""
from Hedging_Saving import data_function
import pandas as pd
import math
import datetime
import numpy as np

def pre_master_dataset(master_df):
    """
    Get all dataset from the database and combine them to one dataframe.
    (data pre-processing)
    :param master_df: filename
    :type master_df: csv file
    :return dataframe contains all of the datasets
    """
    df = master_df.copy()
    df.rename(columns={'timestamp_eastern': 'ts'}, inplace=True)
    df['ts'] = pd.to_datetime(df['ts'])
    cols_to_keep = ['season', 'adjusted_demand_MW', 'demand_MW', 'hour_ending_eastern', 'ts']
    df = df[cols_to_keep]
    df['ts'] = pd.to_datetime(df['ts'])
    df['rankings_per_day'] = df.groupby(['season', df.ts.dt.date]).demand_MW.rank(ascending=False)
    df = df[df['rankings_per_day'] == 1]
    df.reset_index(drop=True, inplace=True)
    df['rankings_per_season'] = df.groupby(['season']).demand_MW.rank(ascending=False)
    return df


def pre_forecast_dataset(forecast_df):
    """
    Get all dataset from the database and combine them to one dataframe.
    (data pre-processing)
    :param forecast_df: filename
    :type forecast_df: csv file
    :return dataframe contains all of the datasets
    """
    df3 = forecast_df.copy()
    df3['ts'] = pd.to_datetime(df3['ts'])
    df3['ts_future'] = pd.to_datetime(df3['ts_future'])
    cols_to_keep = ['ts', 'ts_future', 'forecast']
    df3 = df3[cols_to_keep]
    df_ten = df3[(df3.ts.dt.time == datetime.time(10, 0))]
    df_ten = df_ten[['forecast', 'ts', 'ts_future']]
    df_ten.rename(columns={'ts': 'ts_main'}, inplace=True)
    df_ten.rename(columns={'ts_future': 'ts'}, inplace=True)
    df_ten = df_ten[['forecast', 'ts']]
    return df_ten


def merge_forecast_top_priority(master_df, forecast_df):
    """
    Merge two dataframe and create new column 'predict' based on forecast.
    :param master_df: filename
    :param forecast_df: filename
    :type master_df: csv file
    :type forecast_df: csv file
    :return a new dataframe
    """
    dff = pre_master_dataset(master_df)
    dff2 = pre_forecast_dataset(forecast_df)
    df_merge = dff.merge(dff2, on='ts')
    df_merge['predict'] = (df_merge.forecast > 0).astype(int)
    return df_merge


def extract_topN_forecast(ts, n):
    """
    Select topN highest probabilities from pre_forecast_dataset file.
    Also, generate their discharge percentages.
    :param ts: time
    :param n: numbers
    :type ts: datetime
    :type n: int
    :return probability
    """
    df3 = forecast_df.copy()
    df3['ts'] = pd.to_datetime(df3['ts'])
    df3['ts_future'] = pd.to_datetime(df3['ts_future'])
    cols_to_keep = ['ts', 'ts_future', 'forecast']
    df3 = df3[cols_to_keep]
    df_ten = df3[(df3.ts.dt.time == datetime.time(10, 0))]
    df_ten = df_ten[['forecast', 'ts', 'ts_future']]
    df_ten2 = df_ten[(df_ten['ts_future'] == ts)]
    ts_10 = df_ten2['ts'].max()
    df_ten = df_ten[(df_ten['ts'] == ts_10)]
    nlar = df_ten.nlargest(n, 'forecast')
    df = nlar['forecast']
    df_s = df.sum()
    dff = (1-df_s)/n
    nlar['pro'] = nlar['forecast'].apply(lambda x: (x + dff))
    result = nlar[(nlar['ts_future'] == ts)]
    if len(result['pro']) == 0:
        return 0
    df_p = result['pro'].max()
    if df_p >= 0.5:
        return (0.5/0.5)*100
    else:
        p = int((df_p/0.5)*100)
        return p


def Accuracy(master_df, forecast_df):
    """
    create new table for predicting peak hour. With this table we
    can know how well our designed forecasting algorithms and the
    performance on each season.
    :param master_df: filename
    :param forecast_df: filename
    :type master_df: csv file
    :type forecast_df: csv file
    :return a new dataframe
    """
    num = [1, 3, 5, 10, 20]
    new = []
    data = merge_forecast_top_priority(master_df, forecast_df)
    df = data.copy()
    for i in df.groupby('season'):
        for j in num:
            tmp = df[(df['season'] == i[0]) & (df['rankings_per_season'] <= j)]
            test = tmp.forecast.apply(lambda x: (x > 0))
            df = df[df['rankings_per_season'] <= 20]
            dff_uni = pd.unique(df['hour_ending_eastern'])
            count = 0
            for k, v in test.items():
                if v == True:
                    count += 1
            row = {
                'season': i[0],
                'top_n': j,
                'success': count,
                'Hit rate': count / j,
            }
            performance = 0
            for peak_hr in dff_uni:
                df_peak_hr = tmp[tmp['hour_ending_eastern'] == peak_hr]
                sum = 0
                ct = 0
                for z in df_peak_hr['ts']:
                    ct += 1
                    sum += extract_topN_forecast(z, 3)
                ave = 0
                if ct != 0:
                    ave = int(sum / ct)
                performance += int(ave * df_peak_hr.predict.sum())
                row[peak_hr] = f'{df_peak_hr.predict.sum()}/{df_peak_hr.predict.count()},{ave}'
            row['percentage'] = performance/j
            row['quality'] = np.where(row['percentage'] >= 70, 'good', 'poor')
            new.append(row)
        final_df = pd.DataFrame(new)
    return final_df

def check_approx_equals(expected, received):
    """
    Checks received against expected, and returns whether or
    not they match (True if they do, False otherwise).
    If the argument is a float, will do an approximate check.
    If the arugment is a data structure will do an approximate check
    on all of its contents.
    """
    try:
        if type(expected) == dict:
            # first check that keys match, then check that the
            # values approximately match
            return expected.keys() == received.keys() and \
                all([check_approx_equals(expected[k], received[k])
                    for k in expected.keys()])
        elif type(expected) == list or type(expected) == set:
            # Checks both lists/sets contain the same values
            return len(expected) == len(received) and \
                all([check_approx_equals(v1, v2)
                    for v1, v2 in zip(expected, received)])
        elif type(expected) == float:
            return math.isclose(expected, received, abs_tol=0.001)
        else:
            return expected == received
    except Exception as e:
        print(f'EXCEPTION: Raised when checking check_approx_equals {e}')
        return False


def assert_equals(expected, received):
    """
    Checks received against expected, throws an AssertionError
    if they don't match. If the argument is a float, will do an approximate
    check. If the arugment is a data structure will do an approximate check
    on all of its contents.
    """
    assert check_approx_equals(expected, received), \
        f'Failed: Expected {expected}, but received {received}'


def test_pre_master_dataset():
    assert_equals('2016-05-01 20:00:00', str(pre_master_dataset(master_df)['ts'].iloc[0]))
    assert_equals('2016-05-02 21:00:00', str(pre_master_dataset(master_df)['ts'].iloc[1]))
    assert_equals('2016-05-03 20:00:00', str(pre_master_dataset(master_df)['ts'].iloc[2]))


def test_pre_forecast_dataset():
    assert_equals(0.0025, (pre_forecast_dataset(forecast_df)['forecast'].iloc[0]))
    assert_equals(0, (pre_forecast_dataset(forecast_df)['forecast'].iloc[1]))
    assert_equals(0.005, (pre_forecast_dataset(forecast_df)['forecast'].iloc[2]))


def test_extract_topN_forecast():
    assert_equals(100.0, (extract_topN_forecast('2016-09-07 17:00:00', 3)))
    assert_equals(44, (extract_topN_forecast('2016-08-10 18:00:00', 3)))
    assert_equals(0, (extract_topN_forecast('2016-08-25 16:00:00', 3)))


def test_merge_forecast_top_priority():
    assert_equals(21, (merge_forecast_top_priority(master_df,forecast_df)['hour_ending_eastern'].iloc[0]))
    assert_equals(20, (merge_forecast_top_priority(master_df,forecast_df)['hour_ending_eastern'].iloc[1]))
    assert_equals(21, (merge_forecast_top_priority(master_df,forecast_df)['hour_ending_eastern'].iloc[2]))


def test_Accuracy():
    assert_equals(100,(Accuracy(master_df,forecast_df)['percentage'].iloc[0]))
    assert_equals(81,(Accuracy(master_df,forecast_df)['percentage'].iloc[1]))
    assert_equals(78,(Accuracy(master_df,forecast_df)['percentage'].iloc[2]))


def main():
    master_df = pd.read_csv('./samples/small_master.csv')
    forecast_df = pd.read_csv('./samples/small_forecast.csv')
    test_pre_master_dataset()
    test_pre_forecast_dataset()
    test_merge_forecast_top_priority()
    test_extract_topN_forecast()
    test_Accuracy()


if __name__ == '__main__':
    main()

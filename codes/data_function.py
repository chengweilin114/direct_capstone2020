""" Module contains functions to retrieve
and process data from the database folder"""


import pandas as pd
import datetime


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


def extract_topN_forecast(ts, n, df):
    """
    Select topN highest probabilities from pre_forecast_dataset file.
    Also, generate their discharge percentages.
    :param ts: time
    :param n: numbers
    :type ts: datetime
    :type n: int
    :return probability
    """
    df3 = df.copy()
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


def accuracy(master_df, forecast_df):
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
                if ave == 0:
                    row[peak_hr] =f'{0}/{df_peak_hr.predict.count()},{ave}'
                    row['success'] = row['success'] - df_peak_hr.predict.count()
                    row['Hit rate'] = row['success'] / j  
                else:
                    row[peak_hr] = f'{df_peak_hr.predict.sum()}/{df_peak_hr.predict.count()},{ave}'        
            row['performance'] = performance/j
            new.append(row)
        final_df = pd.DataFrame(new)
    return final_df


def main():
    master_df = pd.read_csv('/database/small_master.csv')
    forecast_df = pd.read_csv('/database/small_forecast.csv')
    pre_master_dataset(master_df)
    pre_forecast_dataset(forecast_df)
    merge_forecast_top_priority(master_df, forecast_df)
    accuracy(master_df, forecast_df)


if __name__ == '__main__':
    main()

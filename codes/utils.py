import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


def percent_to_str(a, b, pct):

    """
    Arguments:
        a: The numerator.
        b: The denominator.
        pct: The percentage.

    Return:
        A string with the format a/b(pct).

    """

    if pct > 0.:
        s = str(a)
        s += '/'
        s += str(b)
        s += '('
        s += str(pct)
        s += '%)'

    else:
        s = str(a)
        s += '/'
        s += str(b)

    return s

def plot_overall_performance(df, save_path):

    """
    Arguments:
        df:
        A dataframe. The overall report for discharging
        in proportional to probabilities, with a 2-hour
        battery spread out over different number of hours.

        save_path:
        A string. The path to save the figure.

    Return:
        None

    This function use the n_probs_to_use as x-axis and the
    average discharged energy as y_axis, and plot the
    performance fo top 1, top 3, top 5, top 10, and top 20
    peaks.

    """

    plt.figure(figsize=(10,10), dpi=200)
    plt.xlabel('n_probs_to_use', fontsize=14)
    plt.ylabel('Performance(%)', fontsize=14)
    for n in set(df['Top_n_peaks'].values):
        mask = df['Top_n_peaks'] == n
        top_n_df = df[mask]

        xdata = top_n_df['Top_n_probs']
        ydata = top_n_df['Performance(%)']
        plt.plot(xdata, ydata, marker='.', label=str(n)+' peaks')

    plt.legend(fontsize=14)
    plt.savefig('figure.png')


if __name__ == '__main__':

    overall_report = pd.read_csv('overall_report.csv')
    save_path = ''

    plot_overall_performance(overall_report, save_path)


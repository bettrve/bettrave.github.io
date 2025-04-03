import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import seaborn as sns
import os
import windrose
from scipy.constants import alpha
from scipy.optimize import curve_fit
from datetime import datetime
from windrose import WindroseAxes
from matplotlib.cm import ScalarMappable
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import calendar
from scipy import stats

pd.set_option('display.max_columns', 6)
pd.set_option('display.max_rows', 5)

# load data

scada_data = pd.read_csv(r"C:\Users\Admin\Desktop\Wind projects"
                   r"\Turbine_Data_Kelmarsh_1_2019-01-01_-_2020-01-01_228.csv",
                   skiprows=9, sep=',', index_col='# Date and time')

turbine_status = pd.read_csv(r"C:\Users\Admin\Desktop\Wind projects"
                   r"\Status_Kelmarsh_1_2019-01-01_-_2020-01-01_228.csv",
                   skiprows=9, sep=',')

#convert index column to datetime format

scada_data.index = pd.to_datetime(scada_data.index)

#print(scada_data.columns)
print(turbine_status.head())
print(turbine_status['IEC category'].unique())
print(turbine_status['Status'].unique())
#print(turbine_status['Code'].unique())
print(turbine_status['Message'].unique())

#turbine_status.resample('M')['IEC category'].value_counts()
turbine_status['Timestamp start'] = pd.to_datetime(turbine_status['Timestamp start'])


turbine_status.loc[turbine_status['Timestamp end'] == '-', 'Timestamp end'] = turbine_status['Timestamp start']
turbine_status['Timestamp end'] = pd.to_datetime(turbine_status['Timestamp end'])

def sec_to_format(s):
    h, s = divmod(int(s), 3600)
    m, s = divmod(s, 60)
    return f'{h:02}:{m:02}:{s:02}'

turbine_status.loc[turbine_status['Duration'] == '-', 'Duration'] = turbine_status['Timestamp end'] - turbine_status['Timestamp start']
turbine_status['Duration'] = pd.to_timedelta(turbine_status['Duration'])

turbine_status['Duration'] = [sec_to_format(s) for s in turbine_status['Duration'].dt.total_seconds()]

print(turbine_status.info())

c = ['red', 'orange', 'green', 'blue', 'violet']
turbine_status.resample('M', on='Timestamp start')['IEC category'].value_counts().unstack().plot.bar(stacked=True, width=0.8, figsize=(10,5), color=c, rot=45,
                                                                              title='Wind Turbine IEC Category', ylabel='Frequency')
plt.show()

# scada data info

print(scada_data.isna().sum())
print('\n')
print(scada_data.describe())
print('\n')
print(scada_data.info())
print('\n')
print(scada_data.count())
#print(scada_data['Data Availability'].unique())

# Get hours/months from datetime
scada_data = scada_data.fillna(0)
dates = scada_data.index
hours = [date.hour for date in dates]
scada_data['hour'] = hours
month = [date.month for date in dates]
scada_data['month'] = month
import calendar
scada_data['month_names'] = scada_data['month'].apply(lambda x: calendar.month_name[x])

month_dict = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

fig, ax1 = plt.subplots()
ax1.plot(scada_data['Voltage L1 / U (V)'], color='r')
ax1.plot(scada_data['Voltage L2 / V (V)'], color='b')
ax1.plot(scada_data['Voltage L3 / W (V)'], color='g')
ax1.plot(scada_data['Grid voltage (V)'], color='purple')
plt.show()


def weibull (x,c,k):
    return (k / c) * (x / c)**(k - 1) * np.exp(-(x / c)**k)

# Monthly distribution analysis with Weibull fitting

i=1
c_values, k_values = [], []
err_c_values, err_k_values = [], []
plt.figure(figsize=(10,12))
for key, value in month_dict.items():
    plt.subplot(4,3,i)
    data = scada_data[scada_data['month_names'] == value]['Wind speed (m/s)']
    #data_err = scada_data[scada_data['month_names'] == value]['Wind speed, Standard deviation (m/s)']
    #print(np.mean(data))
    bin_heights, bin_borders, _ = plt.hist(data, bins=20, edgecolor='k', alpha=0.5, density=True)
    #bin_heights_std, _, _ = plt.hist(data_err, bins=20, edgecolor='k', alpha=0.5, density=True)

    bin_centers = 0.5*(bin_borders[1:] + bin_borders[:-1])
    #std = np.sqrt(bin_heights)
    popt, pcov = curve_fit(weibull, bin_centers, bin_heights, p0=[4,2], ) # same guess for each month

    err = np.sqrt(np.diag(pcov))
    err_c, err_k  = err[0], err[1]
    c_values.append(popt[0])
    k_values.append(popt[1])
    err_c_values.append(err[0])
    err_k_values.append(err[1])

    print(F'The value of c is {np.round(popt[0], 2):.5f} '
          F'with standard error of {np.round(err_c, 2):.5f}.')
    print(F'The value of k is {np.round(popt[1], 2):.5f} '
          F'with standard error of {np.round(err_k, 2):.5f}.')

    textstr = '\n'.join((
        r'c=%.4f' % (np.round(popt[0], 2)),
        r'k=%.4f' % (np.round(popt[1], 2))))

    x_interval_for_fit = np.linspace(bin_borders[0], bin_borders[-1], 20)
    plt.plot(x_interval_for_fit, weibull(x_interval_for_fit, *popt),
             label=textstr)

    resid = np.abs(weibull(x_interval_for_fit, *popt) - bin_heights)
    rmse = np.std(resid)
    #print(rmse)

    #fig.text(0.5, -0.04, 'Wind speed (m/s)', ha='center')
    plt.title(value, fontsize=10)
    plt.legend(loc='upper right', fontsize=8)
    i += 1

plt.figure(figsize=(10,12))
for key, value in month_dict.items():
    data = scada_data[scada_data['month_names'] == value]['Wind speed (m/s)']
    plt.hist(data, bins=20, histtype='step', density=True)
    plt.legend(loc='upper right')

plt.xlabel('Wind speed bins (m/s)')
plt.ylabel('Frequency')
plt.show()

fig, ax1 = plt.subplots()

scada_data.groupby('month')['Wind speed (m/s)'].mean().plot(title='Monthly Average', kind='bar')

ax1.plot(c_values, color='g')
ax1.set_ylim(0,10)

plt.show()

# plots
fig, ax = plt.subplots(figsize=(12,6))

scada_data.plot(x='Wind speed (m/s)', y='Power (kW)', kind='scatter',
                title='Power curve (kW) vs Wind speed (m/s)',
                     xlabel='Wind speed (m/s)', label='Power (kW)', ax=ax)
scada_data.plot(x='Wind speed (m/s)', y='Power, Minimum (kW)', kind='scatter',
                title='Power curve (kW) vs Wind speed (m/s)',
                     xlabel='Wind speed (m/s)', label='Power, Min (kW)', ax=ax, color='#FF0000')
scada_data.plot(x='Wind speed (m/s)', y='Power, Maximum (kW)', kind='scatter',
                title='Power curve (kW) vs Wind speed (m/s)',
                     xlabel='Wind speed (m/s)', label='Power, Max (kW)', ax=ax, color='#0000FF')

plt.show()

from sklearn.ensemble import IsolationForest
iso_forest = IsolationForest(n_estimators=50, max_samples='auto', contamination=float(0.01),max_features=1.0)

# Select features
features = scada_data[['Wind speed (m/s)', 'Power (kW)']]

iso_forest.fit(features)

# Calculate anomaly scores and classify anomalies

scada_data['anomaly_score'] = iso_forest.decision_function(features)
scada_data['anomaly'] = iso_forest.predict(features)

scada_data['anomaly'].value_counts()

# Visualization of the results
plt.figure(figsize=(10, 5))

# Plot normal instances
normal = scada_data[scada_data['anomaly'] == 1]
plt.scatter(normal.index, normal['anomaly_score'], label='Normal')

# Plot anomalies
anomalies = scada_data[scada_data['anomaly'] == -1]
plt.scatter(anomalies.index, anomalies['anomaly_score'], label='Anomaly')
plt.xlabel("Instance")
plt.ylabel("Anomaly Score")
plt.legend()
plt.show()

fig, ax = plt.subplots(figsize=(12,6))

scada_data[scada_data['anomaly'] == 1].plot(x='Wind speed (m/s)', y='Power (kW)', kind='scatter',
                title='Power curve (kW) vs Wind speed (m/s)',
                     xlabel='Wind speed (m/s)', label='Normal', ax=ax)
scada_data[scada_data['anomaly'] == -1].plot(x='Wind speed (m/s)', y='Power (kW)', kind='scatter',
                title='Power curve (kW) vs Wind speed (m/s)',
                     xlabel='Wind speed (m/s)', label='Anomaly', ax=ax, color='#FF0000')
plt.ylabel('Power (kW)')
plt.show()

exit()

#plt.show()
#scada_data.groupby('hour').mean()['Wind speed (m/s)'].plot(title='Average of Wind speed of each Hours')
#plt.show()

# drop rows with Power = 0
scada_data = scada_data.drop(scada_data.loc[scada_data['Power (kW)'] <= 0].index)

# plots

scada_data.plot(x='Wind speed (m/s)', y='Power (kW)', kind='scatter',
                title='Power curve (kW) vs Wind speed (m/s)',
                     xlabel='Wind speed (m/s)', ylabel='Power (kW)', figsize=(12,6))

scada_data.plot(x='Wind speed (m/s)', y='Blade angle (pitch position) A (°)', kind='scatter',
                title='Blade Pitch Blade A (deg) vs Wind speed (m/s)',
                     xlabel='Wind speed (m/s)', ylabel='Blade Pitch (deg)', figsize=(12,6))

scada_data.plot(x='Wind speed (m/s)', y='Rotor speed (RPM)', kind='scatter',
                title='RPM vs Wind speed (m/s)',
                     xlabel='Wind speed (m/s)', ylabel='RPM', figsize=(12,6))



interval = np.arange(0.25,26,0.5)
scada_data.groupby(pd.cut(scada_data['Wind speed (m/s)'], interval)).mean().plot(y='Power (kW)', rot=45)
plt.show()

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12,6))
plt.suptitle('Distribution of Dataset Variables', fontsize=15)

scada_data['Wind speed (m/s)'].plot(ax=axes[0,0], kind='hist', bins=20)
axes[0,0].set_title('Wind speed (m/s)')
scada_data['Power (kW)'].plot(ax=axes[0,1], kind='hist', bins=20)
axes[0,1].set_title('Power (kW)')
scada_data['Wind direction (°)'].plot(ax=axes[1,0], kind='hist', bins=20)
axes[1,0].set_title('Wind direction (°)')
scada_data['Rear bearing temperature (°C)'].plot(ax=axes[1,1], kind='hist', bins=20)
axes[1,1].set_title('Rear bearing temperature (°C)')
#plt.show()


# Wind roses

from windrose import WindroseAxes
wd = scada_data['Wind direction (°)']
ws = scada_data['Wind speed (m/s)']
ax = WindroseAxes.from_ax()
ax.bar(wd, ws, normed=True, opening=0.8, edgecolor="white")
ax.set_legend()

# Wind roses frequency table

ax.bar(wd, ws, normed=True, nsector=16)
table = ax._info["table"]
wd_freq = np.sum(table, axis=0)
direction = ax._info["dir"]
wd_freq = np.sum(table, axis=0)
#plt.show()

# From https://python-windrose.github.io/windrose/usage-output.html

# Monthly analysis

wind_data = pd.DataFrame(
    {
        "ws": scada_data['Wind speed (m/s)'].values,
        "wd": scada_data['Wind direction (°)'].values,
        "month": scada_data['month'],
    }
)


# this creates the raw subplot structure with a subplot per value in month.
g = sns.FacetGrid(
    data=wind_data,
    # the column name for each level a subplot should be created
    col="month",
    # place a maximum of 3 plots per row
    col_wrap=3,
    subplot_kws={"projection": "windrose"},
    sharex=False,
    sharey=False,
    despine=False,
    height=3.5,
)

from functions import plot_windrose_subplots, wpc_equation

g.map_dataframe(
    plot_windrose_subplots,
    direction="wd",
    var="ws",
    normed=True,
    bins=(0.25, 4, 8, 12, 16, 20, 25),
    calm_limit=0.1,
    kind="bar",
)

# make the subplots easier to compare, by having the same y-axis range
y_ticks = range(0, 17, 4)
for ax in g.axes:
    ax.set_rgrids(y_ticks, y_ticks)
ax.set_legend(
        title=r"$m \cdot s^{-1}$", bbox_to_anchor=(1.15, -0.1),
    )
# adjust the spacing between the subplots to have sufficient space between plots
plt.subplots_adjust(wspace=-0.2)
#plt.show()

from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split

# Parameters
n_estimators = 100  # Number of trees
contamination = 0.01  # Expected proportion of anomalies
sample_size = 256  # Number of samples used to train each tree

features = scada_data['Power (kW)']

# Train Isolation Forest
iso_forest = IsolationForest(n_estimators=n_estimators,
                            contamination=contamination,
                            max_samples=sample_size,
                            random_state=42)
iso_forest.fit(features)




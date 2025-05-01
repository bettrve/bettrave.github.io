# bettrave.github.io
# Wind SCADA analysis

## The Dataset

This is an analysis of SCADA data from the Kelmarsh project. The data comes from the Zenodo open database.

This dataset contains various files (see description at the following link) including 10-minute SCADA and status data from the 6 Senvion MM92's at Kelmarsh wind farm, grouped by year from 2016 to mid-2021. 

Each scada file contains 261 columns of :

1. meteorological data (e.g wind speed (m/s), wind direction , air temperature)
2. data linked to the wind turbine itself (e.g blade angle (pitch position), rotor speed, tower acceleration, temperature of major components (e.g hub, rotor bearing, transformer))
3. electrical data (e.g current, voltage, grid current, grid voltage, grid frequency, power factor, reactive power)

** including min, max and std for each data type cited above

## Data cleaning

## Wind speed distribution analysis

A number of different methods have been proposed and evaluated with the aim of determining the best practice. Most commonly used for wind energy assessments is the two-parameter Weibull distribution, which has been shown to accurately capture the skewness of the wind speed distribution. The Weibull distribution function, as given in Eq. (2), generally contains a scale parameter, c, in units of wind speed, which determines the abscissa scale of the wind speed distribution, and a dimensionless shape parameter, k, which reflects the width of the distribution

for this purpose, we will the tool curve_fit from scipy that uses non-linear least squares to fit a function, f, to data.

Let's take a closer look at the wind data for each month of the year in a histogram (normalized data). Note that all the months seem to follow a Weibull probability distribution ($f(x, c, k) = {k/c}(x/c)^(k-1)*e^-{x/c}^k$). Each histogram is left-skewed with mean wind speed ranging from 5 to 8. 

A detail version is given in the next graph with histograms plotted separetly and fitted with a Weibull distribution curve. This is done through a loop process by calculating each bins center values and bins center heights and using the module curve fit from scipy. 

The initialisation p0 takes two intial guess for {k} and {c}, respectively 2 and 4, based on the observations of the first graph. Each fit gets his RMSE calculated. The curve fit is also plotted and compared to a KDE plot.

![image](https://github.com/user-attachments/assets/748253fd-fc21-44a2-b2c1-e277968d3ccb)


![Figure_2](https://github.com/user-attachments/assets/7bcbd733-9ce6-47e2-8369-6a0273f5e5a5)

![Figure_3](https://github.com/user-attachments/assets/92cbf7cd-9d10-49c6-b169-23f5ce842778)

Once the scale and shape parameters are determined, the wind power density can be determined. 


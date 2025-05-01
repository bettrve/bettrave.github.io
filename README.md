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

## Wind speed distribution monthly analysis

A number of different methods have been proposed and evaluated with the aim of determining the best wind distribution. Most commonly used for wind energy assessments is the two-parameter Weibull distribution, which has been shown to accurately capture the skewness of the wind speed distribution. 

The Weibull distribution function, as given in Eq. (1), generally contains a scale parameter, {c}, in units of wind speed, which determines the abscissa scale of the wind speed distribution, and a dimensionless shape parameter, {k}, which reflects the width of the distribution. Several methods for parameter estimation of the probability distribution exists in the literature. The most common are the method of moments, least square method, method of L-moments and maximum likelihood method and power density method.

  ![image](https://github.com/user-attachments/assets/748253fd-fc21-44a2-b2c1-e277968d3ccb) (Eq. 1)

In this case, we will use the tool _curve_fit_ from _scipy_ that uses non-linear least squares. A loop is calculating each bins center values and bins center heights and is optimising parameters {k} and {c}. Based on the monthly aggregated histogram plot, the initialisation p0 takes two intial guess for {k} and {c}, respectively 2 and 4. The curve fit is then plotted over the distribution (green) and compared to a KDE plot (orange).

Analysis showed that the monthly shape parameter 𝑘 ranged from x in x to x in x and the monthly scale parameter 𝑐 ranged from x m/s in x to x m/s in x.

In order to determine the performance of the Weibull distribution for modelling the wind speed data, the coefficient of determination (𝑅2) and the root mean square error (RMSE) were used. The correlation coefficient over the year between 0.95 and 0.98 and the values of RMSE are less than 0.01. It indicates that the Weibull distribution describes the data satisfactorily. Furthermore, the goodness of fit was found to be an inverse function of the shape parameter (not shown).

![Figure_2](https://github.com/user-attachments/assets/7bcbd733-9ce6-47e2-8369-6a0273f5e5a5)

![Figure_3](https://github.com/user-attachments/assets/92cbf7cd-9d10-49c6-b169-23f5ce842778)

Once the scale and shape parameters are determined, the wind power density can be determined. It represents the potential available wind energy rather than what a turbine can extract.

Analysis showed that the ...

## Wind roses monthly analysis


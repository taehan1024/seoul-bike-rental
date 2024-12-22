# **Seoul City Public Bike Rental System Analysis**

Building on the [initial analysis](README_v1.md) of predicting hourly bike rentals for the public bike rental system in Seoul, we expand the same methodology to predict hourly bike returns for each station. With the goal of optimizing bike allocation across rental stations and minimizing shortages, we quantify the probabilities of bike shortages using these predictions and simulate changes in shortage probabilities for all possible bike rides between two destinations. Ultimately, we aim to recommend bike rides that could potentially reduce bike shortage probabilities across the system, supported by quantitative evidence. This approach mirrors the NYC and Lyft initiative known as the [Bike Angel Program.](https://citibikenyc.com/bike-angels)

![Main](images/main_visual_bikesoul.png)

---


## **Methods**

### **1. Predicting Bike Rental and Return Demand**
- Train Poisson GAM models to predict bike rentals and returns on an hourly basis, incorporating variables such as geographical locations, days, hours, and past rental and return data for each station, respectively.

The Poisson GAM will be structured as follows:

$$
\log(\lambda) = \beta_0 + f_1(\text{latitude}, \text{longitude}) + f_2(\text{weekday}) + f_3(\text{hour}) + f_4(\text{weekday} \times \text{hour}) + f_5(\text{past rentals/returns})
$$

Where:
- $\lambda$ is the expected number of bike rentals/returns at each station on an hourly basis.
- $f_1(\text{latitude}, \text{longitude})$ is an interaction term that captures the non-linear impact of geographical location on bike rentals/returns.
- $f_2(\text{weekday})$ and $f_3(\text{hour})$ represent smooth functions to capture the periodic and seasonal effects of day and time.
- $f_4(\text{weekday} \times \text{hour})$ is an interaction term that captures any combined effects between the day of the week and hour of the day.
- $f_5(\text{past rentals/returns})$ accounts for rolling averages of bike rentals/returns over the past 7 days on an hourly basis, capturing both the inherent and recent demand for each station.

### **2. Daily Net Bike Rentals and Returns at Each Station**
- Calculate the daily net predicted bike rentals and returns by accumulating hourly predictions from 6 Am to 5 AM the following day.

|   station_number | date       |   hour |   rent_pred |   net_rent_pred |   return_pred |   net_return_pred |
|-----------------:|:-----------|-------:|------------:|----------------:|--------------:|------------------:|
|                0 | 2024-06-24 |      6 |        1.05 |            1.05 |          1.64 |              1.64 |
|                0 | 2024-06-24 |      7 |        2.68 |            3.73 |          3.76 |              5.4  |
|                0 | 2024-06-24 |      8 |        3.69 |            7.43 |          9.83 |             15.23 |
|                0 | 2024-06-24 |      9 |        1.17 |            8.59 |          5.75 |             20.98 |
|                0 | 2024-06-24 |     10 |        1.56 |           10.16 |          4.86 |             25.84 |
|                0 | 2024-06-24 |     11 |        1.83 |           11.99 |          3    |             28.84 |
|                0 | 2024-06-24 |     12 |        1.75 |           13.74 |          1.87 |             30.71 |
|                0 | 2024-06-24 |     13 |        2.38 |           16.12 |          2.98 |             33.69 |
|                0 | 2024-06-24 |     14 |        2.2  |           18.32 |          2.1  |             35.79 |
|                0 | 2024-06-24 |     15 |        2.25 |           20.57 |          1.77 |             37.56 |
|                0 | 2024-06-24 |     16 |        3.91 |           24.48 |          2.89 |             40.46 |
|                0 | 2024-06-24 |     17 |        6.39 |           30.87 |          5.09 |             45.54 |
|                0 | 2024-06-24 |     18 |       10.24 |           41.11 |          8.16 |             53.71 |
|                0 | 2024-06-24 |     19 |        5.69 |           46.8  |          5.1  |             58.81 |
|                0 | 2024-06-24 |     20 |        4.38 |           51.18 |          3.29 |             62.09 |
|                0 | 2024-06-24 |     21 |        3.86 |           55.04 |          3.19 |             65.28 |
|                0 | 2024-06-24 |     22 |        2.75 |           57.79 |          2.92 |             68.2  |
|                0 | 2024-06-24 |     23 |        1.01 |           58.8  |          0.91 |             69.11 |
|                0 | 2024-06-25 |      0 |        1.51 |           60.31 |          1.19 |             70.31 |
|                0 | 2024-06-25 |      1 |        1.56 |           61.87 |          1.09 |             71.4  |
|                0 | 2024-06-25 |      2 |        0.68 |           62.55 |          0.56 |             71.96 |
|                0 | 2024-06-25 |      3 |        0.33 |           62.88 |          0.26 |             72.22 |
|                0 | 2024-06-25 |      4 |        0.33 |           63.21 |          0.33 |             72.55 |
|                0 | 2024-06-25 |      5 |        0.63 |           63.84 |          0.79 |             73.33 |


### **3. Initial Bike Allocation**
- Assign the initial number of bikes to each station at the start of the day (6 AM), weighted according to the average number of rentals at each station. Round down to the nearest integer.
- Assume that at 6 AM each day, all stations are reset to their initial number of bikes.

For $$\text{Station}_i$$:

$$
\text{Initial Bikes}_i = \left\lfloor \frac{\text{Bike Rentals}_i}{\text{Total Bike Rentals}} \times \text{Total Bikes} \right\rfloor
$$

$$
\text{Initial Bikes}_0 = \left\lfloor \frac{\text{2,059}}{\text{4,431,917}} \times \text{39,162} \right\rfloor = \text{18} 
$$


### **4. Bike Shortage Probabilities** 
- Define bike shortage as the condition where the number of bikes remaining at a station drops below 0.
- Using the [Skellam distribution](https://en.wikipedia.org/wiki/Skellam_distribution), calculate the probabilities of the differences between daily net predicted bike returns and rentals falling below the initial number of bikes, on an hourly basis for each station.

For $$\text{Station}_i \text{ at } \text{Hour}_h \text{ on } \text{Date}_d$$:

$
\P(\text{Shortage}_i) \text{ at h on d} = \text{SkellamCDF}(-1 \cdot \text{Initial Bikes}_i, \text{Net Return}_idh, \text{Net Rentals}_idh)
$$

Where:
- $\text{Initial Bikes}$: Number of bikes initially at the station at 6 AM.  
- $\text{Net Return}_idh$: Daily net predicted bike returns at the given date and hour.  
- $\text{Net Rentals}_idh$: Daily net predicted bike rentals at the given date and hour. 

$$
P(\text{Shortage}_0) \text{ at 6 PM on 6/24} = \text{SkellamCDF}(\text{-18, } \text{53.71, } \text{41.11}) = \text{18.22\%} 
$$

### **5. Ride Simulation** 
- Per bike ride, returning stations would gain an additional bike reducing bike shortage probabilities while renting stations would lose one increasing the probabilities of bike shortage.  

For a bike ride from $$\text{Station }_i$$ to $$\text{Station }_j$$:

$$
P(\text{Shortage with +1 bike}_j) = \text{SkellamCDF}(-1 \cdot (\text{Initial Bikes} - 1), \mu_{\text{Returns}}, \mu_{\text{Rentals}})
$$

$$
\Delta P(\text{Shortage with +1 bike}_j) = P(\text{Shortage with +1 bike}_j) - P(\text{Shortage}_j)
$$

$$
P(\text{Shortage with -1 bike}_i) = \text{SkellamCDF}(-1 \cdot (\text{Initial Bikes} + 1), \mu_{\text{Returns}}, \mu_{\text{Rentals}})
$$

$$
\Delta P(\text{Shortage with -1 bike}_i) = P(\text{Shortage with -1 bike}_i) - P(\text{Shortage}_i)
$$

$$
\Delta P(\text{Shortage for Ride}_{ij}) = \Delta P(\text{Shortage with +1 bike}_j) + \Delta P(\text{Shortage with -1 bike}_i)
$$



- Calculate the probabilities of shortage assuming the addition of one extra bike, and determine the differences from the original shortage probabilities. These differences represent the reduction in shortage probabilities due to the additional bike.

\[
P(\text{shortage\_plus\_one}) = \text{SkellamCDF}(-1 \times (\text{initial\_num\_bikes} + 1), \mu_{\text{return}}, \mu_{\text{rent}})
\]

### Reduction in Shortage Probabilities
The reduction in the probability of shortage due to the additional bike is calculated as:

\[
\Delta P(\text{shortage\_plus\_one}) = P(\text{shortage}) - P(\text{shortage\_plus\_one})
\]

- Similarly, calculate the probabilities of shortage assuming one fewer bike, and determine the differences from the original probabilities. These differences represent the increased shortage probabilities due to the removal of one bike.

\[
P(\text{shortage\_minus\_one}) = \text{SkellamCDF}(-1 \times (\text{initial\_num\_bikes} - 1), \mu_{\text{return}}, \mu_{\text{rent}})
\]

### Increase in Shortage Probabilities
The increase in the probability of shortage due to the removal of one bike is calculated as:

\[
\Delta P(\text{shortage\_minus\_one}) = P(\text{shortage\_minus\_one}) - P(\text{shortage})
\]

Where:
- \(P(\text{shortage})\): Original probability of shortage.
- \(P(\text{shortage\_minus\_one})\): Probability of shortage with one less bike.

- We have quantified how much bike shortage probabilities are reduced with one additional bike or increased with one fewer bike for all stations across all hours. We can also quantify the overall change in bike shortage probabilities in the system for all possible bike rides from one station to another, with the rental station losing a bike and the return station gaining one.

\[
\Delta P_{\text{ride}}(\text{rent}, \text{return}) = \Delta P(\text{shortage\_plus\_one}) - \Delta P(\text{shortage\_minus\_one})
\]

Where:
- \(\Delta P(\text{shortage\_plus\_one})\): Reduction in shortage probability due to adding one bike at the **return station**.
- \(\Delta P(\text{shortage\_minus\_one})\): Increase in shortage probability due to removing one bike at the **rent station**.

This allows for evaluating the net impact of a specific ride on system-wide shortages.



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
- Calculate the daily net predicted bike rentals and returns by accumulating hourly predictions from 6 AM to 5 AM the following day.

For $$\text{Station}_ {1920} \text{ on 6/24/2024}$$:

|   station_number | date       |   hour |   rent_pred |   net_rent_pred |   return_pred |   net_return_pred |
|-----------------:|:-----------|-------:|------------:|----------------:|--------------:|------------------:|
|             1920 | 2024-06-24 |      6 |         1.8 |             1.8 |           1.1 |               1.1 |
|             1920 | 2024-06-24 |      7 |         9.1 |            10.9 |           3.8 |               4.9 |
|             1920 | 2024-06-24 |      8 |        14.5 |            25.5 |           5.1 |              10   |
|             1920 | 2024-06-24 |      9 |         1.5 |            26.9 |           1.5 |              11.4 |
|             1920 | 2024-06-24 |     10 |         1.1 |            28   |           1   |              12.4 |
|             1920 | 2024-06-24 |     11 |         1.7 |            29.7 |           0.9 |              13.4 |
|             1920 | 2024-06-24 |     12 |         1   |            30.7 |           1.3 |              14.7 |
|             1920 | 2024-06-24 |     13 |         1   |            31.8 |           0.8 |              15.5 |
|             1920 | 2024-06-24 |     14 |         0.9 |            32.7 |           1.3 |              16.7 |
|             1920 | 2024-06-24 |     15 |         1.3 |            34   |           1.6 |              18.4 |
|             1920 | 2024-06-24 |     16 |         1.1 |            35.1 |           1.4 |              19.8 |
|             1920 | 2024-06-24 |     17 |         4.1 |            39.2 |           5.2 |              25   |
|             1920 | 2024-06-24 |     18 |         6.7 |            45.9 |           7.6 |              32.6 |
|             1920 | 2024-06-24 |     19 |         4.1 |            50   |           4.3 |              36.8 |
|             1920 | 2024-06-24 |     20 |         3.2 |            53.2 |           4.3 |              41.2 |
|             1920 | 2024-06-24 |     21 |         2.3 |            55.5 |           4.5 |              45.7 |
|             1920 | 2024-06-24 |     22 |         2.7 |            58.2 |           3.5 |              49.2 |
|             1920 | 2024-06-24 |     23 |         0.8 |            59   |           2.9 |              52.1 |
|             1920 | 2024-06-25 |      0 |         0.9 |            59.9 |           0.9 |              53   |
|             1920 | 2024-06-25 |      1 |         0.8 |            60.7 |           0.7 |              53.8 |
|             1920 | 2024-06-25 |      2 |         0.3 |            61   |           0.5 |              54.3 |
|             1920 | 2024-06-25 |      3 |         0.3 |            61.3 |           0.2 |              54.5 |
|             1920 | 2024-06-25 |      4 |         0.2 |            61.6 |           0.3 |              54.8 |
|             1920 | 2024-06-25 |      5 |         0.7 |            62.3 |           0.5 |              55.4 |


### **3. Initial Bike Allocation**
- Assign the initial number of bikes to each station at the start of the day (6 AM), weighted according to the average number of rentals at each station. Round down to the nearest integer.
- Assume that at 6 AM each day, all stations are reset to their initial number of bikes.

For $$\text{Station}_i$$:

$$
\text{Initial Bikes}_i = \left\lfloor \frac{\text{Bike Rentals}_i}{\text{Total Bike Rentals}} \times \text{Total Bikes} \right\rfloor
$$

For $$\text{Station}_ {1920}$$:

$$
\text{Initial Bikes}_ {1920} = \left\lfloor \frac{\text{1,637}}{\text{4,431,917}} \times \text{39,162} \right\rfloor = \text{14} 
$$


### **4. Bike Shortage Probabilities** 
- Define bike shortage as the condition where the number of bikes remaining at a station drops below 0.
- Using the [Skellam distribution](https://en.wikipedia.org/wiki/Skellam_distribution), calculate the probabilities of the differences between daily net predicted bike returns and rentals falling below the initial number of bikes, on an hourly basis for each station.

For $$\text{Station}_i \text{ at } \text{Hour}_h \text{ on } \text{Date}_d$$:

$$
P(\text{Shortage}_ {idh}) = \text{SkellamCDF}(-1 \cdot \text{Initial Bikes}_ {i}, \text{Net Return}_ {idh}, \text{Net Rentals}_ {idh})
$$

Where:
- $\text{Initial Bikes}_i$: Number of bikes initially at $\text{Station}_i$ at 6 AM.  
- $\text{Net Return}_{idh}$: Daily net predicted bike returns at the given $\text{Date}_d$ and $\text{Hour}_h$.  
- $\text{Net Rentals}_{idh}$: Daily net predicted bike rentals at the given $\text{Date}_d$ and $\text{Hour}_h$. 

For $$\text{Station}_ {1920}$$ $$\text{ at 1 PM on 6/24/2024}$$:

$$
P(\text{Shortage}) = \text{SkellamCDF}(\text{-14, } \text{15.5, } \text{31.8}) = 65.5%
$$


### **5. Ride Simulation** 
- For each ride, the return station gains one additional bike, while the renting station loses one, influencing bike shortage probabilities. 
- Calculate the changes in bike shortage probabilities when gaining or losing one additional bike, given the date and hour for each station. 

When return $$\text{Station}_j$$ gains a bike at $$\text{Hour}_h$$ on $$\text{Date}_d$$:

$$
P(\text{Shortage}_ {jdh} after +1 bike) = \text{SkellamCDF}(-1 \cdot \text{Initial Bikes}_ {j} - 1, \text{Net Return}_ {jdh}, \text{Net Rentals}_ {jdh})
$$

$$
\Delta P(\text{Shortage}_ {jdh}) = P(\text{Shortage}_ {jdh} after +1 bike) - P(\text{Shortage}_ {jdh})
$$

When renting $$\text{Station}_i$$ loses a bike at $$\text{Hour}_h$$ on $$\text{Date}_d$$:

$$
P(\text{Shortage}_ {idh} after -1 bike) = \text{SkellamCDF}(-1 \cdot \text{Initial Bikes}_ {i} + 1, \text{Net Return}_ {idh}, \text{Net Rentals}_ {idh})
$$

$$
\Delta P(\text{Shortage}_ {idh}) = P(\text{Shortage}_ {idh} after -1 bike) - P(\text{Shortage}_ {idh})
$$

When a bike travels from $$\text{Station}_i$$ to $$\text{Station}_j$$, the bike-sharing system experiences the following change in overall bike shortage probabilities:

$$
\Delta P(\text{Shortage}_ {ijdh}) = \Delta P(\text{Shortage}_ {idh}) + \Delta P(\text{Shortage}_ {jdh})
$$


For example, a bike renting from $$\text{Station}_ {704}$$ and returning to $$\text{Station}_ {1920}$$ $$\text{ at 1 PM on 6/24/2024}$$:


$$
\Delta P(\text{Shortage}_ {1920}) = \text{SkellamCDF}(\text{-14, } \text{15.5, } \text{31.8}) - \text{SkellamCDF}(\text{-15, } \text{15.5, } \text{31.8})
                                  = 59.9% - 65.5%
                                  = -5.55%
$$

$$
\Delta P(\text{Shortage}_ {704}) = \text{SkellamCDF}(\text{-57, } \text{181.1, } \text{78.5}) - \text{SkellamCDF}(\text{-56, } \text{181.1, } \text{78.5})
                                  = 0.0% - 0.0%
                                  = ~0.0%
$$

$$
\Delta P(\text{Shortage}_ {704, 1920}) = -5.55% + ~0.0%
                                       = -5.55%
$$

At Station 704, losing one bike does not impact the probability of a bike shortage, given an initial inventory of 57 bikes, with expected returns of 181 and rentals of 78.5.
In contrast, Station 1920 faces a bike shortage, with expected returns of 15.5 and rentals of 31.8. Adding one bike reduces the probability of a shortage by approximately 5.55%.
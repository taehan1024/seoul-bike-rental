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

For $$\text{Station}_1920 \text{ on 6/24/2024}$$:

|   station_number | date       |   hour |   rent_pred |   net_rent_pred |   return_pred |   net_return_pred |
|-----------------:|:-----------|-------:|------------:|----------------:|--------------:|------------------:|
|             1920 | 2024-06-24 |      6 |        1.84 |            1.84 |          1.1  |              1.1  |
|             1920 | 2024-06-24 |      7 |        9.09 |           10.93 |          3.76 |              4.86 |
|             1920 | 2024-06-24 |      8 |       14.52 |           25.45 |          5.1  |              9.96 |
|             1920 | 2024-06-24 |      9 |        1.46 |           26.91 |          1.46 |             11.42 |
|             1920 | 2024-06-24 |     10 |        1.13 |           28.04 |          1.03 |             12.45 |
|             1920 | 2024-06-24 |     11 |        1.7  |           29.74 |          0.95 |             13.4  |
|             1920 | 2024-06-24 |     12 |        1    |           30.74 |          1.3  |             14.69 |
|             1920 | 2024-06-24 |     13 |        1.03 |           31.77 |          0.79 |             15.48 |
|             1920 | 2024-06-24 |     14 |        0.92 |           32.69 |          1.27 |             16.75 |
|             1920 | 2024-06-24 |     15 |        1.33 |           34.01 |          1.64 |             18.39 |
|             1920 | 2024-06-24 |     16 |        1.1  |           35.12 |          1.43 |             19.82 |
|             1920 | 2024-06-24 |     17 |        4.06 |           39.18 |          5.16 |             24.98 |
|             1920 | 2024-06-24 |     18 |        6.72 |           45.9  |          7.57 |             32.56 |
|             1920 | 2024-06-24 |     19 |        4.11 |           50    |          4.27 |             36.82 |
|             1920 | 2024-06-24 |     20 |        3.2  |           53.2  |          4.33 |             41.15 |
|             1920 | 2024-06-24 |     21 |        2.33 |           55.54 |          4.55 |             45.7  |
|             1920 | 2024-06-24 |     22 |        2.71 |           58.24 |          3.51 |             49.21 |
|             1920 | 2024-06-24 |     23 |        0.76 |           59    |          2.91 |             52.12 |
|             1920 | 2024-06-25 |      0 |        0.93 |           59.93 |          0.93 |             53.05 |
|             1920 | 2024-06-25 |      1 |        0.78 |           60.71 |          0.71 |             53.75 |
|             1920 | 2024-06-25 |      2 |        0.33 |           61.04 |          0.52 |             54.28 |
|             1920 | 2024-06-25 |      3 |        0.3  |           61.35 |          0.21 |             54.49 |
|             1920 | 2024-06-25 |      4 |        0.24 |           61.59 |          0.35 |             54.83 |
|             1920 | 2024-06-25 |      5 |        0.73 |           62.32 |          0.52 |             55.35 |


### **3. Initial Bike Allocation**
- Assign the initial number of bikes to each station at the start of the day (6 AM), weighted according to the average number of rentals at each station. Round down to the nearest integer.
- Assume that at 6 AM each day, all stations are reset to their initial number of bikes.

For $$\text{Station}_i$$:

$$
\text{Initial Bikes}_i = \left\lfloor \frac{\text{Bike Rentals}_i}{\text{Total Bike Rentals}} \times \text{Total Bikes} \right\rfloor
$$

For $$\text{Station}_1920$$:

$$
\text{Initial Bikes}_1920 = \left\lfloor \frac{\text{1,637}}{\text{4,431,917}} \times \text{39,162} \right\rfloor = \text{14} 
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

For $$\text{Station}_1920$$ $$\text{ at 1 PM on 6/24/2024}$$:

$$
P(\text{Shortage}) = \text{SkellamCDF}(\text{-14, } \text{15.48, } \text{31.77}) = \text{65.5\%} 
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


For example, a ride from Station '704' to Station '1920' at 1 PM on 6/24/2024:


$$
\Delta P(\text{Shortage}_ {1920}) = \text{SkellamCDF}(\text{-14, } \text{15.48, } \text{31.77}) - \text{SkellamCDF}(\text{-15, } \text{15.48, } \text{31.77})
                                  = \text{65.5\%} - \text{59.9\%}
                                  = \text{-5.55\%}
$$

$$
\Delta P(\text{Shortage}_ {704}) = \text{SkellamCDF}(\text{-57, } \text{181.10, } \text{78.52}) - \text{SkellamCDF}(\text{-56, } \text{181.10, } \text{78.52})
                                  = \text{0.0\%} - \text{0.0\%}
                                  = \text{~0.0~\%}
$$

$$
\Delta P(\text{Shortage}_ {704, 1920}) = \text{-5.55\%} + \text{~0.0~\%}
                                       = \text{-5.55\%}
$$


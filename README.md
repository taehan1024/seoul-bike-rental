# **Seoul City Public Bike Rental System Analysis**

Building on the [initial analysis](README_v1.md) of predicting hourly bike rentals for the public bike rental system in Seoul, we expand the same methodology to predict hourly bike returns for each station. With the goal of optimizing bike allocation across rental stations and minimizing shortages, we quantify the probabilities of bike shortages using these predictions and simulate changes in shortage probabilities for all possible bike rides between two destinations. Ultimately, we aim to recommend bike rides that could potentially reduce bike shortage probabilities across the system, supported by quantitative evidence. This approach mirrors the NYC and Lyft initiative known as the [Bike Angel Program.](https://citibikenyc.com/bike-angels)

![Main](images/main_visual_bikesoul.png)

---


## **Methods**

1. Predicting Bike Rental and Return Demand
- Similar to the previous analysis predicting bike rental demand, train another GAM model using geographical locations, days, hours, and past rental demands for each station.

2. Net Changes at Each Station
- Subtract predicted bike returns from rentals for each station and hour.
- Calculate the net change to determine the net surplus or shortage for each hour from 6 AM to 5 AM the next day.

3. Initial Bike Allocation
- Assign the initial number of bikes to each station at the start of the day (6 AM), weighted based on the average rentals at each station.

4. Bike Shortage Simulation 
- Define a shortage as having fewer than 0 bikes remaining, considering the initial allocation and expected net changes throughout the day on an hourly basis.
- Use the [Skellam distribution](https://en.wikipedia.org/wiki/Skellam_distribution) to calculate the probability of the number of bikes at a station dropping below zero, based on the difference between predicted returns and rentals.

\[
P(\text{shortage}) = P(X < 0) = \text{SkellamCDF}(-1 \* \text{initial\_#\_bikes}, \mu_{\text{return}}, \mu_{\text{rent}})
\]

Where:
- **initial\_bikes**: Number of bikes initially at the station.
- \(\mu_{\text{return}}\): Expected returns (predicted).
- \(\mu_{\text{rent}}\): Expected rentals (predicted).

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



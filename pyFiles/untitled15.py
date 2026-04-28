# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 08:26:19 2026

@author: Ezgi
"""



import pandas as pd
import matplotlib.pyplot as plt







# Which City is worse? Which is best?

df = pd.read_csv("air_pollution.csv")

#average AQI per city
city_avg_aqi = df.groupby("City Name")["AQI Level"].mean().reset_index()

# sort cities by AQI descending (worst first)
city_avg_aqi = city_avg_aqi.sort_values(by="AQI Level", ascending=False)


plt.figure(figsize=(10,6))
bars = plt.bar(city_avg_aqi["City Name"], city_avg_aqi["AQI Level"], color='crimson')

# Highlight best and worst
bars[0].set_color('red')    # Worst AQI
bars[-1].set_color('green') # Best AQI

plt.xlabel("City")
plt.ylabel("Average AQI Level")
plt.title("Average AQI by City (Worst to Best)")
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.show()






# Heatmap for every city: 
# Green for lower / Red for higher:
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read your dataset
df = pd.read_csv("air_pollution.csv")


pivot = df.pivot_table(index="City Name", columns="year", values="AQI Level", aggfunc='mean')

# Plot heatmap
plt.figure(figsize=(10,6))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlGn_r")  # red = high AQI, green = low AQI
plt.title("AQI Heatmap by City and Year")
plt.xlabel("Year")
plt.ylabel("City")
plt.show()
 

#AQI per year:

df = pd.read_csv("air_pollution.csv")


yearly_avg = df.groupby("year")["AQI Level"].mean()

# Plot trend
plt.figure(figsize=(8,5))
plt.plot(yearly_avg.index, yearly_avg.values, marker='o', color='blue', linewidth=2)
plt.title("Average AQI by Year (All Cities)")
plt.xlabel("Year")
plt.ylabel("Average AQI Level")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()

#Shows no change by years 2016 to 2021 



































  
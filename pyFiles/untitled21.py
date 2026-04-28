# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 23:06:50 2026

@author: Ezgi
""" 

import pandas as pd
import plotly.express as px

# Load data
# map visual
df = pd.read_csv("uv-county.csv")

fig = px.choropleth(
    df,
    geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
    locations='COUNTY_FIPS',
    color='UV_ Wh/m_',
    color_continuous_scale='YlOrRd',
    scope="usa",
    hover_name='COUNTY NAME',
    labels={'UV_ Wh/m_':'UV Radiation'}
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(title='Pennsylvania County UV Radiation Potential')


fig.show(renderer='browser')



# Interactive bar chart with plotly. 

df = df.sort_values('UV_ Wh/m_', ascending=False)

fig = px.bar(
    df,
    x='COUNTY NAME',
    y='UV_ Wh/m_',
    color='UV_ Wh/m_',
    color_continuous_scale='YlOrRd',
    hover_data=['COUNTY_FIPS'],
    title='UV Radiation by Pennsylvania County'
)

fig.update_layout(xaxis_tickangle=-60)
fig.show(renderer='browser')
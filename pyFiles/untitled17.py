# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 19:36:53 2026

@author: Ezgi
"""


import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool, Select, CheckboxGroup
from bokeh.transform import factor_cmap



df = pd.read_excel(r"C:\Users\Ezgi\Downloads\pennsylvania_seasonal_pollen_allergy_dataset.xlsx")

df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"])

season_colors = {
    "Spring": "lightgreen",
    "Summer": "orange",
    "Fall": "brown",
    "Winter": "Darkblue"
}

source = ColumnDataSource(df)


p2 = figure(title="Pollen Types Over Time",
            x_axis_type="datetime",
            width=900, height=300)

p2.line("Date", "Tree_Pollen_Index", source=source, color="brown", legend_label="Tree")
p2.line("Date", "Grass_Pollen_Index", source=source, color="green", legend_label="Grass")
p2.line("Date", "Ragweed_Pollen_Index", source=source, color="orange", legend_label="Ragweed")

p2.legend.click_policy = "hide"


p3 = figure(title="Temperature vs Allergy (Season Colored)",
            width=450, height=350)

p3.circle(
    x="Avg_Temperature",
    y="Estimated_Allergy_Symptom_Index",
    source=source,
    size=8,
    color=factor_cmap(
        "Season",
        palette=list(season_colors.values()),
        factors=list(season_colors.keys())
    ),
    alpha=0.7
)

p3.xaxis.axis_label = "Temperature"
p3.yaxis.axis_label = "Allergy Index"



dropdown = Select(
    title="Choose Pollen Type",
    value="Tree_Pollen_Index",
    options=[
        ("Tree_Pollen_Index", "Tree"),
        ("Grass_Pollen_Index", "Grass"),
        ("Ragweed_Pollen_Index", "Ragweed"),
        ("Total_Pollen_Index", "Total Pollen")
    ]
)


layout = column(
    dropdown,
    p2,
    p3
)

output_file("seasonal_allergy_dashboard.html")
show(layout)


 























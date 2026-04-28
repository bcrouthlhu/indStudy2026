# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 20:12:11 2026

@author: Ezgi
"""

import pandas as pd
from bokeh.plotting import figure, show,output_file
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Select, CustomJS, HoverTool, Range1d


df = pd.read_excel(r"C:\Users\Ezgi\Downloads\pennsylvania_seasonal_pollen_allergy_dataset.xlsx")


spring_df = df[df["Season"] == "Summer"]


grouped = spring_df.groupby("Year").mean(numeric_only=True).reset_index()
grouped["Year"] = grouped["Year"].astype(str)


source = ColumnDataSource(data=dict(
    Year=grouped["Year"],
    value=grouped["Estimated_Allergy_Symptom_Index"],
    temp=grouped["Avg_Temperature"]
))

full_source = ColumnDataSource(grouped)


p = figure(
    x_range=grouped["Year"],
    title="Summer Allergy vs Temperature",
    width=750,
    height=400
)


bars = p.vbar(
    x="Year",
    top="value",
    width=0.6,
    color="green",
    source=source,
    legend_label="Allergy / Selected Metric"
)


p.extra_y_ranges = {"temp_axis": Range1d(start=min(grouped["Avg_Temperature"]) - 5,
                                         end=max(grouped["Avg_Temperature"]) + 5)}

p.add_layout(p.yaxis[0], 'left')


line = p.line(
    x="Year",
    y="temp",
    source=source,
    line_width=3,
    color="orange",
    y_range_name="temp_axis",
    legend_label="Avg Temperature"
)


p.add_tools(HoverTool(tooltips=[
    ("Year", "@Year"),
    ("Value", "@value"),
    ("Temp", "@temp")
]))

p.xaxis.axis_label = "Year"
p.yaxis.axis_label = "Allergy / Metric"


select = Select(
    title="Choose Metric",
    value="Estimated_Allergy_Symptom_Index",
    options=[
        ("Estimated_Allergy_Symptom_Index", "Allergy Index"),
        ("Tree_Pollen_Index", "Tree Pollen"),
        ("Grass_Pollen_Index", "Grass Pollen"),
        ("Ragweed_Pollen_Index", "Ragweed Pollen"),
        ("Total_Pollen_Index", "Total Pollen")
    ]
)
 


callback = CustomJS(args=dict(source=source, full=full_source, select=select), code="""
    const data = source.data;
    const full_data = full.data;
    const metric = select.value;

    data['value'] = full_data[metric];
    data['temp'] = full_data['Avg_Temperature'];

    source.change.emit();
""")

select.js_on_change("value", callback)


layout = column(select, p)

output_file("Summer_Allergy_Index.html")
show(layout)





import pandas as pd
import plotly.express as px

# Load data
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

fig.show()
























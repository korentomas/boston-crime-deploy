# -*- coding: utf-8 -*-
"""BostonCrimesv2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fU-8ZvgQyIuoQcn7A-MI7nyftRz1SoX0

# Crimes in Boston Analysis
Developed by Tomás Pablo Korenblit (tomaskorenblit@gmail.com)

Crime incident reports are provided by Boston Police Department (BPD) to document the initial details surrounding an incident to which BPD officers respond. This is a dataset containing records from the new crime incident report system, which includes a reduced set of fields focused on capturing the type of incident as well as when and where it occurred.

## Import Packages
"""

import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import datetime
import datashader as ds
import datashader.transfer_functions as tf
from colorcet import fire, bmy

px.defaults.color_discrete_sequence = px.colors.qualitative.Antique

"""## Read data"""

data = pd.read_csv('https://github.com/korentomas/boston-crime-data/raw/main/bostoncrime.zip', compression='zip', low_memory=False, encoding='latin')
data.loc[data.OFFENSE_CODE_GROUP.isnull(),'OFFENSE_CODE_GROUP'] = 'Other'
data.head()

data.describe()

dataf = data.query('Lat < 44').query('Lat > 36').query('Long < -69').query('Long > -74')
cvs = ds.Canvas(plot_width=350, plot_height=350)
agg = cvs.points(dataf, x='Long', y='Lat')

# agg is an xarray object, see http://xarray.pydata.org/en/stable/ for more details
coords_lat, coords_lon = agg.coords['Lat'].values, agg.coords['Long'].values
# Corners of the image, which need to be passed to mapbox
coordinates = [[coords_lon[0], coords_lat[0]],
               [coords_lon[-1], coords_lat[0]],
               [coords_lon[-1], coords_lat[-1]],
               [coords_lon[0], coords_lat[-1]]]

img = tf.shade(agg, cmap=fire)[::-1].to_pil()

# Trick to create rapidly a figure with mapbox axes
fig = px.scatter_mapbox(dataf[:1], lat='Lat', lon='Long', zoom=10, opacity=0)
# Add the datashader image as a mapbox layer image
fig.update_layout(mapbox_style="carto-darkmatter",
                 mapbox_layers = [
                {
                    "sourcetype": "image",
                    "source": img,
                    "coordinates": coordinates
                }]
)
fig.show()

"""## Visualization"""

# Create functions to show different types of graphs

# TreeMap
def treemap(categories,title,path,values):
    fig = px.treemap(categories, path=path, values=values, height=700,
                 title=title, color_discrete_sequence = px.colors.sequential.RdBu)
    fig.data[0].textinfo = 'label+text+value'
    fig.show()

# Histogram
def histogram(data,path,color,title,xaxis,yaxis):
    fig = px.histogram(data, x=path,color=color)
    fig.update_layout(
        title_text=title,
        xaxis_title_text=xaxis, 
        yaxis_title_text=yaxis, 
        bargap=0.2, 
        bargroupgap=0.1
    )
    fig.show()

# Bar
def bar(categories,x,y,color,title,xlab,ylab):
    fig = px.bar(categories, x=x, y=y,
             color=color,
             height=400)
    fig.update_layout(
    title_text=title, 
    xaxis_title_text=xlab, 
    yaxis_title_text=ylab,
    bargap=0.2, 
    bargroupgap=0.1
    )
    fig.show()

def year_crimes_analysis(year=None, display_all=False, display_major=False, display_major_month=False, display_major_dayweek=False, display_crime_month=False, display_crime_eachday=False, display_crime_hour=False):
    if year == None:

        data_year = data.reset_index(drop=True)
        if display_all==True or display_major==True:
            number_crimes_year = data_year['OFFENSE_CODE_GROUP'].value_counts()
            categories_year = pd.DataFrame(data=number_crimes_year.index, columns=["OFFENSE_CODE_GROUP"])
            categories_year['values'] = number_crimes_year.values

            treemap(categories_year,'Major Crimes in Boston',['OFFENSE_CODE_GROUP'],categories_year['values'])

            histogram(data_year,"OFFENSE_CODE_GROUP","OFFENSE_CODE_GROUP",'Major Crimes in Boston','Crime','Count')

            fig = px.bar(categories_year, x=categories_year['OFFENSE_CODE_GROUP'][0:10], y=categories_year['values'][0:10],
                     color=categories_year['OFFENSE_CODE_GROUP'][0:10], height=400)

            fig.update_layout(
                title_text='Top 10 Major Crimes in Boston in', # title of plot
                xaxis_title_text='Crime', # xaxis label
                yaxis_title_text='Count', # yaxis label
                bargap=0.2, 
                bargroupgap=0.1
            )
            fig.show()

        if display_all==True or display_major_month==True:
            Number_crimes_month_year = data_year['MONTH'].value_counts()
            months_year = pd.DataFrame(data=Number_crimes_month_year.index, columns=["MONTH"])
            months_year['values'] = Number_crimes_month_year.values

            fig = go.Figure(go.Bar(
                    y=months_year['values'],
                    x=months_year['MONTH'],
                marker=dict(
                    color='green',

                ),
                    orientation='v'))

            fig.update_layout(
                title_text='Major Crimes in Boston per month', # title of plot
                xaxis_title_text='Month', # xaxis label
                yaxis_title_text='Count ', # yaxis label
                bargap=0.2, 
                bargroupgap=0.1
            )
            fig.show()

        if display_all==True or display_major_dayweek==True:
            Number_crimes_days_year = data_year['DAY_OF_WEEK'].value_counts()
            days_year= pd.DataFrame(data=Number_crimes_days_year.index, columns=["DAY_OF_WEEK"])
            days_year['values'] = Number_crimes_days_year.values

            histogram(data_year,"DAY_OF_WEEK","DAY_OF_WEEK",'Crime count on each day','Day','Crimes Count')


            fig = go.Figure(data=[go.Pie(labels=days_year['DAY_OF_WEEK'], values=days_year['values'])])
            fig.update_layout(
                title_text='Crime count on each day', # title of plot
            )
            fig.show()
        if display_all==True or display_crime_month==True:
            histogram(data_year,"OFFENSE_CODE_GROUP","MONTH",'Crime count per Category on each Month','Category','Crimes Count on each Month')

        if display_all==True or display_crime_eachday==True:
            histogram(data_year,"MONTH","DAY_OF_WEEK",'Crime count per Month on each Day','Month','Crimes Count on each Day')

        if display_all==True or display_crime_hour==True:
            histogram(data_year,"DAY_OF_WEEK","HOUR",'Crime count per Day on each Hour','Day','Crimes Count on each Hour')
        
        
    
    else:
        data_year = data [(data['YEAR'] == year) ].reset_index(drop=True)
        if display_all==True or display_major==True:
            number_crimes_year = data_year['OFFENSE_CODE_GROUP'].value_counts()
            categories_year = pd.DataFrame(data=number_crimes_year.index, columns=["OFFENSE_CODE_GROUP"])
            categories_year['values'] = number_crimes_year.values

            treemap(categories_year,'Major Crimes in Boston in ' + str(year),['OFFENSE_CODE_GROUP'],categories_year['values'])

            histogram(data_year,"OFFENSE_CODE_GROUP","OFFENSE_CODE_GROUP",'Major Crimes in Boston in ' + str(year),'Crime','Count')

            fig = px.bar(categories_year, x=categories_year['OFFENSE_CODE_GROUP'][0:10], y=categories_year['values'][0:10],
                     color=categories_year['OFFENSE_CODE_GROUP'][0:10], height=400)

            fig.update_layout(
                title_text='Top 10 Major Crimes in Boston in ' + str(year), # title of plot
                xaxis_title_text='Crime', # xaxis label
                yaxis_title_text='Count', # yaxis label
                bargap=0.2, 
                bargroupgap=0.1
            )
            fig.show()

        if display_all==True or display_major_month==True:
            Number_crimes_month_year = data_year['MONTH'].value_counts()
            months_year = pd.DataFrame(data=Number_crimes_month_year.index, columns=["MONTH"])
            months_year['values'] = Number_crimes_month_year.values

            fig = go.Figure(go.Bar(
                    y=months_year['values'],
                    x=months_year['MONTH'],
                marker=dict(
                    color='green',

                ),
                    orientation='v'))

            fig.update_layout(
                title_text='Major Crimes in Boston per month in ' + str(year), # title of plot
                xaxis_title_text='Month', # xaxis label
                yaxis_title_text='Count ', # yaxis label
                bargap=0.2, 
                bargroupgap=0.1
            )
            fig.show()

        if display_all==True or display_major_dayweek==True:
            Number_crimes_days_year = data_year['DAY_OF_WEEK'].value_counts()
            days_year= pd.DataFrame(data=Number_crimes_days_year.index, columns=["DAY_OF_WEEK"])
            days_year['values'] = Number_crimes_days_year.values

            histogram(data_year,"DAY_OF_WEEK","DAY_OF_WEEK",'Crime count on each day in ' + str(year),'Day','Crimes Count')


            fig = go.Figure(data=[go.Pie(labels=days_year['DAY_OF_WEEK'], values=days_year['values'])])
            fig.update_layout(
                title_text='Crime count on each day in ' + str(year), # title of plot
            )
            fig.show()
        if display_all==True or display_crime_month==True:
            histogram(data_year,"OFFENSE_CODE_GROUP","MONTH",'Crime count per Category on each Month in ' + str(year),'Category','Crimes Count on each Month')

        if display_all==True or display_crime_eachday==True:
            histogram(data_year,"MONTH","DAY_OF_WEEK",'Crime count per Month on each Day in ' + str(year),'Month','Crimes Count on each Day')

        if display_all==True or display_crime_hour==True:
            histogram(data_year,"DAY_OF_WEEK","HOUR",'Crime count per Day on each Hour in ' + str(year),'Day','Crimes Count on each Hour')

"""## Usage:

Possible params:
- year: select year to use as data (2015 - 2021). Select None to do the whole range.
- display_all: Displays all graphs
- display_major: Displays major crimes in Boston by offense code group and top 10 most common crimes.
- display_major_month: Displays major crimes in Boston per month
- display_major_dayweek: Displays crime count on each day
- display_crime_month: Displays crime count per Category on each Month
- display_crime_eachday: Displays crime count per Month on each Day
- display_crime_hour: Displays crime count per Day on each Hour


```
year_crimes_analysis(None, display_all=True)
```
Displays all the possible graphs taking all the data (2015 - 2021) in account.


```
year_crimes_analysis(2017, display_major_month=True, display_crime_month=True)
```
Displays the major crimes in boston in 2017 and displays crime count per category on each month



"""

year_crimes_analysis(2019, display_all=True)
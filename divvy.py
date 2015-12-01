%matplotlib inline

import datetime
import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from mpl_toolkits.basemap import Basemap


#Load and combine data sets 
#https://www.divvybikes.com/data
divvy_q1 = pd.read_csv('Divvy_Trips_2015-Q1.csv')
divvy_q2 = pd.read_csv('Divvy_Trips_2015-Q2.csv')
divvy_stations = pd.read_csv('Divvy_Stations_2015.csv')
divvy_rides = pd.concat([divvy_q1, divvy_q2]).reset_index()


#Add additional columns
divvy_rides['start_hour'] = divvy_rides['starttime'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y %H:%M').hour)
divvy_rides['week_day'] = divvy_rides['starttime'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y %H:%M').weekday())
divvy_rides['am_rush'] = divvy_rides['start_hour'].apply(lambda x: True if x in [7,8,9] else False)
divvy_rides['pm_rush'] = divvy_rides['start_hour'].apply(lambda x: True if x in [16,17,18] else False)


#Make Rush hour historgram
week_df = divvy_rides[(divvy_rides.week_day != 5) & (divvy_rides.week_day != 6)]
group_weekdays = week_df.groupby('start_hour').size()
color_list = ['g']*7 + ['r']*3 + ['g']*6 + ['r']*3 + ['g']*5

my_plot = group_weekdays.plot(kind='bar', figsize=(10,6), color=color_list)
my_plot.set_xlabel('hour of the day')
my_plot.set_ylabel('total number rides')

fig = my_plot.get_figure()


#Station Agg
station_count = week_df.groupby('from_station_id').size()
station_am_count = week_df[week_df.am_rush == True].groupby('from_station_id').size()
station_pm_count = week_df[week_df.pm_rush == True].groupby('from_station_id').size()

station_agg = pd.concat([station_count, station_am_count, station_pm_count], axis=1)

station_agg['pct_am'] = station_agg[1]/station_agg[0]
station_agg['pct_pm'] = station_agg[2]/station_agg[0]

station_agg.index.names = ['id']
station_agg = station_agg.reset_index()

enhanced_stations = pd.merge(divvy_stations, station_agg, on='id', how='inner')
enhanced_stations['rides_per_dock'] = enhanced_stations[0]/enhanced_stations['dpcapacity']

enhanced_stations.drop(enhanced_stations.columns[[1,4,5,6,7,8]], axis=1, inplace=True)

enhanced_stations['pct_diff'] = enhanced_stations['pct_pm'] - enhanced_stations['pct_am']


#Create difference map
lats = list(enhanced_stations['latitude'])
lons = list(enhanced_stations['longitude'])
values = list(enhanced_stations['pct_diff'])

plt.figure(figsize=(30,15))

m  = Basemap(llcrnrlon=-87.75,llcrnrlat=41.735,
             urcrnrlon=-87.5,urcrnrlat=42.03,
             projection='merc',resolution='h')

m.drawcoastlines()

x, y = m(lons, lats)

m.scatter(x, y, s=values)

plt.show()


#CTA Stations
#https://data.cityofchicago.org/Transportation/CTA-System-Information-List-of-L-Stops/8pix-ypme
cta = pd.read_csv('CTA_-_System_Information_-_List_of__L__Stops.csv')

cta_lats = cta['Location'].apply(lambda x: float(x[1:].split(', ')[0])).tolist()
cta_lons = cta['Location'].apply(lambda x: float(x[:-1].split(', ')[1])).tolist()

plt.figure(figsize=(30,15))

m  = Basemap(llcrnrlon=-87.75,llcrnrlat=41.735,
             urcrnrlon=-87.5,urcrnrlat=42.03,
             projection='merc',resolution='h')

m.drawcoastlines()

x, y = m(lons, lats)
xx, yy = m(cta_lons, cta_lats)

m.scatter(x, y, s=values)
m.scatter(xx, yy, color='r')

plt.show()
#%%
import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from branca.colormap import linear
import branca.colormap as cm
import requests

#%%
#######################
# Page configuration
st.set_page_config(
    page_title = "U.S. Census Dashboard",
    page_icon = "✅",
    layout = "wide",
    initial_sidebar_state = "expanded")


#%%
#######################
# load data

@st.cache_data(ttl=1800, show_spinner="Loading the dashboard...")
def load_geojson(url):
    geojson = requests.get(url).json()
    
    return geojson


@st.cache_data(ttl=1800, show_spinner="Loading the dashboard...")
def load_data(url):
    df = pd.read_csv(url)
    
    return df


seoul_geo = load_geojson('https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json')
ride_dat = load_data("ride_dat_streamlit.csv")



#%%
# Sidebar

with st.sidebar:
    st.title('U.S. Population')
       

    

#%%
# Titles

app_title = f"US census map dashboard"
app_subtitle = 'Source: US census gov.'


#%%





#%%
# Columns


# Define top rides (select top 500 based on prob_shortage_improved)
top_rides = ride_dat.nlargest(500, 'prob_shortage_improved')

# Define colormap using branca's linear colormap
def on_click(event):
    global clicked_location
    clicked_location = [event.latitude, event.longitude]
    
# Initialize the map
m = folium.Map(
    location=[37.55708, 126.9902],
    zoom_start=12,
    scrollWheelZoom=False,
    tiles='cartodbpositron',
)

# Add GeoJSON for Seoul's district boundaries
folium.GeoJson(
    seoul_geo, 
    name='지역구', 
    fillOpacity=0, 
    weight=0.6
).add_to(m)

# Add circles and polylines for top rides
for idx, geo_df_row in top_rides.iterrows():
    # Circle for return station
    folium.Circle(
        radius=5,
        location=[geo_df_row['return_station_latitude'], geo_df_row['return_station_longitude']],
        color='black',
        fill=True,
    ).add_to(m)

    # Circle for rent station
    folium.Circle(
        radius=5,
        location=[geo_df_row['rent_station_latitude'], geo_df_row['rent_station_longitude']],
        color='orange',
        fill=True,
    ).add_to(m)

    # Polyline connecting rent and return stations
    folium.PolyLine(
        locations=[
            [geo_df_row['rent_station_latitude'], geo_df_row['rent_station_longitude']],
            [geo_df_row['return_station_latitude'], geo_df_row['return_station_longitude']]
        ],
       # color=colormap(geo_df_row['prob_shortage_improved']),  # Map value to colormap
        weight=2,
        opacity=0.7
    ).add_to(m)

# Add colormap legend
#colormap.caption = 'Predicted Bike Returns'
#colormap.add_to(m)
m.on('click', on_click)

# Display the map in Streamlit
st_map = st_folium(m, width=1400, height=900)


print(clicked_location)



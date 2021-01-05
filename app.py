import streamlit as st
import pandas as pd
import numpy as np
import xlrd
import pydeck as pdk


#connecting to the database

mag1_df = pd.read_excel('Earthquake_database.xls',sheet_name='Sheet1')
mag2_df = pd.read_excel('Earthquake_database.xls',sheet_name='Sheet2')
mag3_df = pd.read_excel('Earthquake_database.xls',sheet_name='Sheet3')
mag4_df = pd.read_excel('Earthquake_database.xls',sheet_name='Sheet4')
mag5_df = pd.read_excel('Earthquake_database.xls',sheet_name='Sheet5')

database_dfs = pd.concat([mag1_df,mag2_df,mag3_df,mag4_df, mag5_df])

#getting the entry with the latest date from database_df
database_dfs['Date_TimeUTC'] = pd.to_datetime(database_dfs['Date_TimeUTC'])
database_dfs['Date'] = database_dfs['Date_TimeUTC'].dt.date
recent_date = database_dfs['Date_TimeUTC'].max()
least_recent_date = database_dfs['Date_TimeUTC'].min()

#getting unique magnitude types for sidebar
magnitude_types = (database_dfs.Mag.dropna().unique())
magnitude_types = [w.upper() for w in magnitude_types]
magnitude_types_unique = ['All']
for i in np.unique(magnitude_types):
    magnitude_types_unique.append(i)
magnitude_types_unique = tuple(magnitude_types_unique)

#getting magnitude range for slidebar
Mag_number = database_dfs.Mag_number.astype('float')
magnitude_min = database_dfs.Mag_number.min() 
magnitude_max = database_dfs.Mag_number.max() 
magnitude_mode = database_dfs.Mag_number.mode()[0]

#getting depth range for slidebar
database_dfs.Depthkm = database_dfs.Depthkm.astype('float')
depth_min = database_dfs.Depthkm.min() 
depth_max = database_dfs.Depthkm.max() 
depth_mode = database_dfs.Depthkm.mode()[0]


st.write("""
# Worldwide Earthquake Monitor
This app shows earthquakes happening wordlwide! It's the first version of app, in upcoming updates it's planned to incorporate interactive map instead of tables.
Data obtained from the https://www.emsc-csem.org/Earthquake/seismologist.php """)

st.sidebar.header('User Filters')

st.sidebar.markdown("""
[Here is the database used for the app]
(https://github.com/beksultankarimov/earthequakes-streamlit/blob/main/Earthquake_database.xls)
""")

# Collects user input features into dataframe

def user_input_features():
    mag_type = st.sidebar.selectbox('Magnitude type',magnitude_types_unique)
    magnitude = st.sidebar.selectbox('Magnitude', ('All', 1,2,3,4,5,6,7,'8+'))
    start_date = st.sidebar.date_input('Start Date',least_recent_date)
    end_date = st.sidebar.date_input('End Date',recent_date)
    if start_date <= end_date:
        st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
    else:
        st.error('Error: End date must fall after start date.')
    
    data = {'mag_type': mag_type,
            'magnitude': magnitude,
            'start_date':start_date,
            'end_date': end_date}

    return data




st.subheader('Filter result')
input_data = user_input_features()
if input_data['mag_type']!='All':
    result_df = database_dfs.loc[database_dfs.Mag == input_data['mag_type']]
else:
    result_df = database_dfs


if input_data['magnitude'] != 'All':
    if input_data['magnitude'] != '8+':
        result_df = result_df.loc[(result_df.Mag_number >= input_data['magnitude']) & 
        (result_df.Mag_number < input_data['magnitude']+1)] 
    else: 
        result_df = result_df.loc[result_df.Mag_number >= 8]
else: result_df = database_dfs


result_df = result_df.loc[(result_df.Date  >= input_data['start_date']) & (result_df.Date  <= input_data['end_date'])]

#st.write(result_df.drop(['Upload_time', 'Date'], axis=1).sort_values(by='Date_TimeUTC'))


# Map

st.write("Eearthquakes happeed between: ", input_data['start_date']," and ",input_data['end_date'])

midpoint = (np.average(result_df.latitude), np.average(result_df.longitude))
#st.map(result_df)

#map with column plot
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 0,
        "pitch": 40,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=result_df[['Date_TimeUTC', 'latitude', 'longitude']],
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        radius=50000,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 100000],
        ),
    ],
))





"""view_state = pdk.ViewState(latitude=midpoint[0], longitude=midpoint[0], zoom=4, min_zoom=1)
view  = pdk.View(type="_GlobeView", controller=True, width=1200, height=700)
layers=[
    pdk.Layer(
        "HexagonLayer",
        data=result_df[["Mag_number","longitude", "latitude"]],
        get_elevation="Mag_number",
        get_position=["longitude", "latitude"],
        radius=20000,
        elevation_scale=100,
        #elevation_range=[0, 10],
        pickable=True,
        auto_highlight=True,
        ),
]
st.write(pdk.Deck(
    views=[view],
    initial_view_state=view_state,
    layers=layers,
    # Note that this must be set for the globe to be opaque
    parameters={"cull": True},
))"""

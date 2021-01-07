import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime as dt
import time

#reading csv file with data
df = pd.read_csv('data_clean.csv')

#convirting to datetime
df.date_time_utc = pd.to_datetime(df.date_time_utc, utc=True)
df['Date'] = df['date_time_utc'].dt.date



st.write("""
# Worldwide Earthquake Monitor
## This app shows earthquakes wordlwide! 
It's the first version of app, in upcoming updates it's planned to incorporate interactive map instead of tables.
Data obtained from the https://www.emsc-csem.org """)

st.sidebar.header('User Filters')

st.sidebar.markdown("""
[Here is the database used for the app]
(https://github.com/beksultankarimov/earthequakes-streamlit/blob/main/Earthquake_database.xls)
""")


        

result_df = df
result_df = result_df[['date_time_utc', 'Countries', 'region_name', 'magnitude_type',
        'magnitude', 'depth','latitude', 'longitude']]
##################################################################################################
if st.sidebar.checkbox("Filter by Date/time", False):
    #getting the entry with the latest date from df
    recent_date = df['date_time_utc'].max()
    least_recent_date = df['date_time_utc'].min()

    #Filter df by date
    start_date = st.sidebar.date_input('Start Date',recent_date)
    end_date = st.sidebar.date_input('End Date',recent_date)

    if start_date > end_date:
        st.error('Error: End date must fall after start date.')


    result_df = result_df.loc[(result_df.date_time_utc.dt.date  >= start_date) & (result_df.date_time_utc.dt.date  <= end_date)]

    ##########################################################################################################
    #filtering by time
    Start_time = None
    End_time = None

    if st.sidebar.checkbox("Filter by time", False):
        start_time = st.sidebar.time_input('Start Time', result_df.date_time_utc.dt.time.min())
        end_time = st.sidebar.time_input('End Time',result_df.date_time_utc.dt.time.max())
        result_df.index = result_df.date_time_utc
        result_df = result_df.between_time(str(start_time)[:5], str(end_time)[:5])      
        
        Start_time = start_time
        End_time = end_time
        
    else:
        result_df = result_df
else:
    last_date = recent_date = df['Date'].max()
    result_df = result_df.loc[result_df.date_time_utc.dt.date >= last_date]

#########################################################################################################

#getting unique magnitude types for sidebar
if st.sidebar.checkbox("Filter by magnitude", False):
    magnitude_types = (result_df.magnitude_type.sort_values().unique())
    magnitude_types_unique = ['All']
    for i in np.unique(magnitude_types):
        magnitude_types_unique.append(i)
    magnitude_types_unique = tuple(magnitude_types_unique)

    #Mgnitude_type filter
    mag_type = st.sidebar.selectbox('Magnitude type',magnitude_types_unique)
    if mag_type !='All':
        result_df = result_df.loc[result_df.magnitude_type == mag_type]
    else:
        result_df = result_df


    #########################################################################################################   

    #Magnitude filter

    #values for the first filter
    magnitude_list = result_df.magnitude.sort_values().astype('int').unique()
    magnitude_unique = ['All']
    for i in magnitude_list:
        magnitude_unique.append(i)
    magnitude_unique = tuple(magnitude_unique)

    #values for the second filter
    separate_mag_list = ['None']
    for i in magnitude_list:
        separate_mag_list.append(i)
    separate_mag_list = tuple(separate_mag_list)

    
    mag_filters = st.sidebar.selectbox('Choose a filter: ',('Filter by fixed magnitude', 'Filter by magnitude range'))
    if mag_filters == 'Filter by fixed magnitude':
        magnitude = st.sidebar.selectbox('Magnitude', magnitude_unique)
        if magnitude != 'All':
            result_df = result_df.loc[(result_df.magnitude >= magnitude) & 
                (result_df.magnitude < magnitude+1)] 
        else: result_df = result_df
    else:
        min_magnitude = st.sidebar.selectbox('Minimum Magnitude', separate_mag_list)
        if min_magnitude != 'None':
            result_df =  result_df.loc[result_df.magnitude >= min_magnitude] 
        else: result_df = result_df

        max_magnitude = st.sidebar.selectbox('Maximum Magnitude', separate_mag_list)
        if max_magnitude != 'None':
            result_df =  result_df.loc[result_df.magnitude < max_magnitude+1] 
        else: result_df = result_df

#####################################################################################################

if st.sidebar.checkbox("Filter by Location", False):
    main_filter = st.sidebar.selectbox("Show Entire World/Region", ('Entire World', 'By Country/Border/Sea'))
    if main_filter == 'Entire World':
        result_df = result_df

    else:
        countries = tuple(result_df.Countries.sort_values().unique())

        country = st.sidebar.multiselect('Select a Country/Border/Sea', countries)
        if len(country) == 1:
            result_df = result_df.loc[result_df.Countries == country[0]]
            
        elif len(country) >1:
            result_df = result_df.loc[result_df.Countries.isin(country)]
            
            countries_df = {}
            countries_df = {elem : pd.DataFrame() for elem in country}
            for i in countries_df:
                countries_df[i] = pd.DataFrame(result_df.loc[result_df.Countries == i])


            #stats by chosen country    
            if len(country)>1:
                if st.checkbox("Show Statistical Data Per Chosen Country", False):
                    for i in countries_df:
                        st.write('Stats of', i)
                        st.write(countries_df[i])

            #subcategory of Countries
            if len(result_df.Countries.unique())==1:
                if len(result_df.region_name.unique())>1:
                    regions = ['All']
                    for i in result_df.region_name.sort_values().unique():
                        regions.append(i)
                    regions = tuple(regions)

                    region = st.sidebar.multiselect('Select region', regions)
                    if 'All' not in region:
                        result_df = result_df.loc[result_df.region_name.isin(region)]

                        region_df = {}
                        region_df = {elem : pd.DataFrame() for elem in region}
                        for i in region_df:
                            region_df[i] = pd.DataFrame(result_df.loc[result_df.region_name == i])
                        
                        if len(result_df.region_name.sort_values().unique())>1:
                            if st.checkbox("Show Statistical Data Per Chosen Region", False):
                                for i in region_df:
                                    st.write('Stats of', i)
                                    st.write(region_df[i])
                    else:
                        result_df = result_df

                        region_df = {}
                        region_df = {elem : pd.DataFrame() for elem in result_df.region_name.sort_values().unique()}
                        for i in region_df:
                            region_df[i] = pd.DataFrame(result_df.loc[result_df.region_name == i])
                        if st.checkbox("Show Statistical Data Per Chosen Region", False):
                                for i in region_df:
                                    st.write('Stats of', i)
                                    st.write(region_df[i])
        else:
            result_df = result_df
#########################################################################################################

st.write('### Filter results: : ' ,result_df.shape[0], ' earthquakes detected')
st.write('### From (date): `%s` To (date):`%s`' % (result_df['date_time_utc'].dt.date.min(), result_df['date_time_utc'].dt.date.max()))
# Map
st.map(result_df)
#Raw data display
if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(result_df.drop('date_time_utc', axis=1))

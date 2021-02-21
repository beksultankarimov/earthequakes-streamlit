import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime as dt
from datetime import datetime, timedelta
import time
import dateutil


@st.cache(allow_output_mutation=True)
def get_data(df):
    df = pd.read_csv('data_clean.csv', index_col=0)
    return df
#reading csv file with data
df = None
df = get_data(df)

#convirting to datetime
df['date_time_utc'] = pd.to_datetime(df.date_time_utc, utc = True)
df['Date'] = df['date_time_utc'].dt.date



st.write("""
# Worldwide Earthquake Monitor
It's the first version of app, in upcoming updates it's planned to incorporate visualy pleasing charts instead of tables.\n
Data obtained from the https://www.emsc-csem.org """)

#visually dividing section
st.write('___________________________________________________________________________________________________')

st.sidebar.header('Apply Filters')
st.sidebar.markdown("""
[Source code(GitHub)]
(https://github.com/beksultankarimov/earthequakes-streamlit)
""")


        

result_df = df
result_df = result_df[['date_time_utc', 'Countries', 'region_name', 'magnitude_type',
        'magnitude', 'depth','latitude', 'longitude']]
result_df.index = result_df.date_time_utc
##################################################################################################
# filter by year

target_year = st.sidebar.selectbox('Choose target year:', tuple(result_df.date_time_utc.dt.year.sort_values(ascending=False).unique()))
result_df = result_df.loc[(result_df.date_time_utc.dt.year >= target_year) & (result_df.date_time_utc.dt.year < target_year+1)]

##################################################################################################
if st.sidebar.checkbox("Filter by Date", False):
    #Filter df by date
    start_date = st.sidebar.date_input('Start Date',result_df.date_time_utc.min())
    end_date = st.sidebar.date_input('End Date',result_df.date_time_utc.max())

    if start_date > end_date:
        st.error('Error: End date must fall after start date.')


    result_df = result_df.loc[(result_df.date_time_utc.dt.date  >= start_date) & (result_df.date_time_utc.dt.date  <= end_date)]


#########################################################################################################

#getting unique magnitude types for sidebar
if st.sidebar.checkbox("Filter by magnitude", False):

    if st.sidebar.checkbox("Magnitude types reference list", False):
        mag_description = pd.read_csv('magnitudes_description.csv')
        mag_description = mag_description[['Magnitude Type', 'Magnitude Range', 'Comments', 'Distance Range', 'Equation']]
        mag_type_decsr = st.sidebar.selectbox('Magnitude type definition', tuple(mag_description['Magnitude Type'].sort_values()))
        if mag_type_decsr != None:
            mag_description = mag_description.loc[mag_description['Magnitude Type'] ==  mag_type_decsr]
            st.write('### **The description of** ', mag_type_decsr, ' magnitude type:')
            st.write(mag_description['Comments'].values[0])
            st.write('**Equation:** ', mag_description['Equation'].values[0])
            st.write('**Magnitude Range:** ', mag_description['Magnitude Range'].values[0])
            st.write('**Distance Range:** ', mag_description['Distance Range'].values[0])
            #visually dividing section
            st.write('___________________________________________________________________________________________________')


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

st.write('### Filter results: ' ,result_df.shape[0], ' earthquakes detected')
st.write('### From (date): `%s` To (date):`%s`' % (result_df['date_time_utc'].dt.date.min(), result_df['date_time_utc'].dt.date.max()))
# Map
st.map(result_df)
#Raw data display
if st.checkbox("Show Detailed Data", False):
    st.write(result_df.drop('date_time_utc', axis=1))

#visually dividing section
st.write('___________________________________________________________________________________________________')
#footer
st.write('''\n[Check the data cleaning Jupiter Notebook here](https://github.com/beksultankarimov/earthequakes-streamlit/blob/main/Earthquakes_Data_Cleaning_.ipynb)''')
st.write('''\n[Check the EDA Jupiter Notebook here](https://github.com/beksultankarimov/earthequakes-streamlit/blob/main/Earthquake_EDA.ipynb)''')
st.write('___________________________________________________________________________________________________')
st.write('This project was done by: **Beksultan Karimov**')
st.write('Check my other ' , '''[Warsaw Flat Price Prediction app](https://warsaw-flat-prediction.herokuapp.com)''')
st.write('''\n[Get my CV](https://drive.google.com/file/d/1yrBoLqFLD_0Qxa10lM8Zjhx2w3GGX4xl/view?usp=sharing)''')
st.write('''\n[LinkedIn](https://www.linkedin.com/in/beksultan-karimov-6a4296179/)''')
st.write('''[Facebook](https://www.facebook.com/profile.php?id=100009130718211)''')
st.write('''[GitHub](https://github.com/beksultankarimov)''')

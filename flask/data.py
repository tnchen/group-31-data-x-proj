import numpy as np
import os
from pathlib import Path
import pandas as pd

# Load the data
directory = os.path.dirname(os.path.dirname(__file__))

path = os.path.join(directory, 'data', 'final_data.csv')
gunViolence = pd.read_csv(path)
gunViolence.fillna(0, inplace=True)

path = os.path.join(directory, 'data', 'county_unemployment.csv')
countyData = pd.read_csv(path)
countyData.fillna(0, inplace=True)

path = os.path.join(directory, 'data', 'predictions.csv')
predictions = pd.read_csv(path)
predictions.fillna(0, inplace=True)

# Subset predictions
predictionsSub = predictions[((predictions['year'] == 2019) & (predictions['month'] == 1))]
predictionsSub = predictionsSub.drop(columns=['year', 'month', 'Gun Death Rate (Ranked High to Low)', 'Gun Denials 2008', 'Mental Health 2008', 'Gun Ownership Rank', 'Gun Denials 2017'])


def decode(row):
    for c in predictionsSub.columns:
        if row[c] == 1:
            return c
predictionsSub['State'] = predictionsSub.apply(decode, axis=1)
predictionsSub = predictionsSub[['State', 'predictions']]

# Get the country geometry
stateGeom = pd.read_json('data/us_states_20m.json')
for i in range(len(stateGeom['features'])):
    stateGeom['type'][i] = stateGeom['features'][i]['properties']['NAME']
    stateGeom['features'][i] = stateGeom['features'][i]['geometry']
stateGeom.rename(columns={'type': 'State', 'features': 'Geometry'}, inplace=True)

# Reformat datasets
stateCols = ['state', 'Mental_Health_Records_Submitted_2008', 'Mental_Health_Records_Submitted_2017', 'Gun_Sale_Denials_2008',
             'Gun_Sale_Denials_2017', 'Giffords Gun Safety Score',  'Gun Deaths per 100k People (2018)',
             'Gun Death Rate (Ranked High to Low)', '# of guns per capita', '# of guns registered',
             'Handgun_Carry_Permit_Fee', 'Years_Valid', '5_Year_Cost', 'Happiness Score']
countyCols = ['County', 'Rate']
stateData = gunViolence[stateCols].drop_duplicates('state')
countyData = countyData[countyCols].drop_duplicates('County')
countyData.columns.values[1] = '2015 Unemployment Rate'
countyData = countyData.reset_index()
stateData = stateData.reset_index()
stateData = stateData.drop(columns=['index'])
countyData = countyData[['County', '2015 Unemployment Rate']]
countyData['County'] = countyData['County'].str.replace(' County', '', regex=True)
stateData = stateGeom.merge(stateData, left_on='State', right_on='state')
stateData = stateData.drop(columns=['state'])
stateData = stateData.merge(predictionsSub, left_on='State', right_on='State')

# Rename StateData
stateData.rename(columns={'predictions': '# Predicted Incidents (2019)',
                          '5_Year_Cost': '5-Year Gun Ownership Cost (USD)',
                          'Handgun_Carry_Permit_Fee': 'Handgun Carry Permit Fee (USD)',
                          'Years_Valid': 'Permit Term (Years)',
                          'Mental_Health_Records_Submitted_2008': 'Mental Health Records Submitted (2008)',
                          'Mental_Health_Records_Submitted_2017': 'Mental Health Records Submitted (2017)',
                          'Gun_Sale_Denials_2008': 'Gun Sale Denials (2008)',
                          'Gun_Sale_Denials_2017': 'Gun Sale Denials (2017)'
                          },
                 inplace=True)
dropdownOptions = np.concatenate([stateData.columns.values[2:], countyData.columns.values[1:]])
print(dropdownOptions)

# Define list of factors that should be plotted with high values as red instead of green
badFactorsList = ['Gun Deaths per 100k People (2018)', '# of guns per capita', '# of guns registered', '2015 Unemployment Rate']


def getColor(col):
    if (col in badFactorsList):
        return 'OrRd'
    else:
        return 'YlGn'


def getMarkerColor(n_killed):
    if (n_killed == 0):
        return '#ffff00'
    elif (n_killed < 2):
        return '#f8d568'
    elif (n_killed < 5):
        return '#ffa500'
    else:
        return '#ff0000'

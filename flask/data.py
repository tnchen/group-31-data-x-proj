import os
from pathlib import Path
import pandas as pd

# Load the gun violence data
directory = os.path.dirname(os.path.dirname(__file__))
path = os.path.join(directory, 'data', 'final_data.csv')
gunViolence = pd.read_csv(path)

# Subset state data
stateCols = ['state', 'Mental_Health_Records_Submitted_2008', 'Mental_Health_Records_Submitted_2017', 'Gun_Sale_Denials_2008',
             'Gun_Sale_Denials_2017', 'Giffords Gun Safety Score',  'Gun Deaths per 100k People (2018)',
             'Gun Death Rate (Ranked High to Low)', '# of guns per capita', '# of guns registered', 'Permit Type',
             'Handgun_Carry_Permit_Fee', 'Years_Valid', '5_Year_Cost', 'Happiness Score']

stateData = gunViolence[stateCols].drop_duplicates('state')

# Define list of factors that should be plotted with high values as red instead of green
badFactorsList = ['Gun_Death_Rate_2018 (per 100k people)', '# of guns per capita', '# of guns registered', ]


def getColor(col):
    if col in badFactorsList:
        return 'OrRd'
    else:
        return 'YlGn'

from flask import *
import folium
from folium.plugins import MarkerCluster
import math
import numpy as np
import os
from pathlib import Path
import re

# Load our data and ML
import data
import ml
directory = os.path.dirname(os.path.dirname(__file__))

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/map', methods=['GET', 'POST'])
def mapPage():
    if request.method == 'POST':
        # Get form info
        numIncidents = request.form['numIncidents']
        center = request.form['center']
        zoom = request.form['zoom']
        selectedIndex = request.form['indexVal']
        yearVal = request.form['yearVal']

        # Extract the number of incidents
        if numIncidents != '':
            numIncidents = int(numIncidents)
        else:
            numIncidents = 100

        # Extract the zoom level
        if zoom != '':
            zoom = int(zoom)
        else:
            zoom = 4

        # Extract the map center
        center = re.findall('LatLng\((.+), (.+)\)', center)
        if len(center) > 0:
            center = center[0]
            center = [float(val) for val in center]
        else:
            center = [35, -97]

        # Extract the selected factor
        if selectedIndex != '':
            selectedIndex = int(selectedIndex)
        else:
            selectedIndex = -1

        # Extract the year
        if yearVal != '':
            yearVal = int(yearVal)
        else:
            yearVal = 2014
    else:
        numIncidents = 100
        zoom = 4
        center = [35, -97]
        selectedIndex = -1
        yearVal = 2014

    # Define our factors
    factors = data.dropdownOptions

    # Create the map
    mapObj = folium.Map(location=center, zoom_start=zoom, tiles='Mapbox Bright', width='75%', height='75%')

    if selectedIndex != -1:
        # Get the selected factor
        selectedFactor = factors[selectedIndex]

        # Add the individual data
        cluster = MarkerCluster(name='Gun Violence Incidents')
        for i, row in data.gunViolence[data.gunViolence['year'] == yearVal].sample(frac=1).head(numIncidents).iterrows():
            cluster.add_child(folium.CircleMarker(location=[row.latitude, row.longitude], radius=5 * (row.n_killed + row.n_injured), fill=True, color=data.getMarkerColor(row.n_killed),
                                                  popup=folium.Popup('Date: ' + str(row.month) + '-' + str(row.day) + '-' + str(row.year) + '</br>Lives Lost: ' + str(row.n_killed), max_width=200)))
        mapObj.add_child(cluster)

        if selectedFactor == '2015 Unemployment Rate':
            # Add the county data
            path = os.path.join(directory, 'data', 'us_counties_20m.json')
            folium.Choropleth(
                geo_data=path,
                name=selectedFactor,
                data=data.countyData,
                columns=['County', selectedFactor],
                key_on='feature.properties.NAME',
                fill_color=data.getColor(selectedFactor),
                fill_opacity=0.5,
                line_opacity=0.2,
                legend_name=selectedFactor
            ).add_to(mapObj)
        else:
            # Add the state data
            path = os.path.join(directory, 'data', 'us_states_20m.json')
            folium.Choropleth(
                geo_data=path,
                name=selectedFactor,
                data=data.stateData,
                columns=['State', selectedFactor],
                key_on='feature.properties.NAME',
                fill_color=data.getColor(selectedFactor),
                fill_opacity=0.5,
                line_opacity=0.2,
                legend_name=selectedFactor
            ).add_to(mapObj)
        folium.LayerControl().add_to(mapObj)
    else:
        selectedIndex = 0

    # Extract the HTML and make it safe
    mapHTML = mapObj.get_root().render()
    mapVar = re.findall('(map_[a-z0-9]+)', mapHTML)[0]
    mapHTML = Markup(mapHTML)

    return render_template('map.html', map=mapHTML, mapVar=mapVar, numIncidents=numIncidents, factors=factors, numFactors=len(factors), selectedIndex=selectedIndex, yearVal=yearVal)


@app.route('/ml', methods=['GET', 'POST'])
def mlPage():
    # Define list of values
    year_list = list(range(2005, 2026))
    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    state_list = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
                  'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois',
                  'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
                  'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana',
                  'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
                  'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
                  'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah',
                  'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
    grade_list = ['A', 'A-', 'B', 'B+', 'B-', 'C', 'C+', 'C-', 'D', 'D+', 'D-', 'F']

    if request.method == 'POST':
        # Get form info
        year = request.form['yearVal']
        month = request.form['monthVal']
        state = request.form['stateVal']
        mentHealthRecSubmit2008 = request.form['mentHealthRecSubmit2008']
        mentHealthRecSubmit2017 = request.form['mentHealthRecSubmit2017']
        gunDenials2008 = request.form['gunDenials2008']
        gunDenials2017 = request.form['gunDenials2017']
        gunDeathRate2018 = request.form['gunDeathRate2018']
        gunDeathRank = request.form['gunDeathRankVal']
        gunOwnerRank = request.form['gunOwnerRankVal']
        gunPerCap = request.form['gunPerCap']
        numGunRegis = request.form['numGunRegis']
        permitCost5Yr = request.form['permitCost5Yr']
        happinessScore = request.form['happinessScore']
        scoreGiffords = request.form['scoreGiffords']

        # Extract the year
        if year != '':
            year = int(year)
            if year < len(year_list):
                year = year_list[year]
        else:
            year = 2019

        # Extract the month
        if month != '':
            month = int(month)
        else:
            month = 0

        # Extract the state
        if state != '':
            state = int(state)
        else:
            state = 0

        # Extract the number of mental health records submitted in 2008
        if mentHealthRecSubmit2008 != '':
            mentHealthRecSubmit2008 = int(mentHealthRecSubmit2008)
        else:
            mentHealthRecSubmit2008 = 155

        # Extract the number of mental health records submitted in 2017
        if mentHealthRecSubmit2017 != '':
            mentHealthRecSubmit2017 = int(mentHealthRecSubmit2017)
        else:
            mentHealthRecSubmit2017 = 5036

        # Extract the number of gun sale denials in 2008
        if gunDenials2008 != '':
            gunDenials2008 = int(gunDenials2008)
        else:
            gunDenials2008 = 32

        # Extract the number of gun sale denials in 2017
        if gunDenials2017 != '':
            gunDenials2017 = int(gunDenials2017)
        else:
            gunDenials2017 = 125

        # Extract the gun death rate in 2018
        if gunDeathRate2018 != '':
            gunDeathRate2018 = float(gunDeathRate2018) / 10
        else:
            gunDeathRate2018 = 22.9

        # Extract the gun death rank
        if gunDeathRank != '':
            gunDeathRank = int(gunDeathRank)
        else:
            gunDeathRank = 1

        # Extract the gun owner rank
        if gunOwnerRank != '':
            gunOwnerRank = int(gunOwnerRank)
        else:
            gunOwnerRank = 6

        # Extract the guns per capita
        if gunPerCap != '':
            gunPerCap = float(gunPerCap) / 1000
        else:
            gunPerCap = 0.033

        # Extract the number of guns registered
        if numGunRegis != '':
            numGunRegis = int(numGunRegis)
        else:
            numGunRegis = 161641

        # Extract the 5 year permit cost
        if permitCost5Yr != '':
            permitCost5Yr = int(permitCost5Yr)
        else:
            permitCost5Yr = 25

        # Extract the happiness score
        if happinessScore != '':
            happinessScore = int(happinessScore)
        else:
            happinessScore = 4

        # Extract the Gifford's gun safety score
        if scoreGiffords != '':
            scoreGiffords = int(scoreGiffords)
        else:
            scoreGiffords = 11
    else:
        year = 2019
        month = 0  # based on month_list (NOTE: 0 is January here, but in ML 1 is January)
        mentHealthRecSubmit2008 = 155
        mentHealthRecSubmit2017 = 5036
        gunDenials2008 = 32
        gunDenials2017 = 125
        gunDeathRate2018 = 22.9  # per 100k people
        gunDeathRank = 1  # zero indexed
        gunOwnerRank = 6  # zero indexed
        gunPerCap = 0.033
        numGunRegis = 161641
        permitCost5Yr = 25
        happinessScore = 4
        state = 0  # based on state_list
        scoreGiffords = 11  # based on grade_list

    # Create the ML input array
    stateArr = [0] * len(state_list)
    stateArr[state] = 1
    gradeArr = [0] * len(grade_list)
    gradeArr[scoreGiffords] = 1
    X = [year, month + 1, mentHealthRecSubmit2008, mentHealthRecSubmit2017, gunDenials2008, gunDenials2017, gunDeathRate2018, gunDeathRank + 1, gunOwnerRank + 1,
         gunPerCap, numGunRegis, permitCost5Yr, happinessScore] + stateArr + gradeArr
    prediction = ml.predict([X])

    return render_template('ml.html', monthList=month_list, stateList=state_list, gradeList=grade_list, selectedYear=year, selectedMonth=month, selectedState=state, mentHealthRecSubmit2008=mentHealthRecSubmit2008,
                           mentHealthRecSubmit2017=mentHealthRecSubmit2017, gunDenials2008=gunDenials2008, gunDenials2017=gunDenials2017, gunDeathRate2018=gunDeathRate2018 * 10,
                           gunDeathRank=gunDeathRank, gunOwnerRank=gunOwnerRank, gunPerCap=gunPerCap * 1000, numGunRegis=numGunRegis, permitCost5Yr=permitCost5Yr,
                           happinessScore=happinessScore, scoreGiffords=scoreGiffords, prediction=prediction)

if __name__ == '__main__':
    app.run(debug=False)

from flask import *
import folium
from folium.plugins import MarkerCluster
import math
import os
from pathlib import Path
import re

# Load our data
import data
directory = os.path.dirname(os.path.dirname(__file__))

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/map', methods=['GET', 'POST'])
def map():
    if request.method == 'POST':
        # Get form info
        numIncidents = request.form['numIncidents']
        center = request.form['center']
        zoom = request.form['zoom']
        selectedIndex = request.form['indexVal']

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
    else:
        numIncidents = 100
        zoom = 4
        center = [35, -97]
        selectedIndex = -1

    # Define our factors
    factors = data.stateCols[1:]

    # Create the map
    mapObj = folium.Map(location=center, zoom_start=zoom, tiles='Mapbox Bright', width='75%', height='75%')

    if selectedIndex != -1:
        # Get the selected factor
        selectedFactor = factors[selectedIndex]

        # Add the individual data
        cluster = MarkerCluster(name='Gun Violence Incidents')
        for i, row in data.gunViolence.sample(frac=1).head(numIncidents).iterrows():
            popup = folium.Popup('Date: ' + str(row.month) + '/' + str(row.day) + '/' + str(row.year) +
                                 '<br>Lives Lost: ' + str(row.n_killed), max_width=200)
            marker = folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=5 * (row['n_killed'] + row['n_injured']), fill=True, color=data.getMarkerColor(row.n_killed), popup=popup)
            cluster.add_child(marker)
        cluster.add_to(mapObj)

        # Add the state data
        path = os.path.join(directory, 'us_states_20m.json')
        folium.Choropleth(
            geo_data=path,
            name=selectedFactor,
            data=data.stateData,
            columns=['state', selectedFactor],
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

    return render_template('map.html', map=mapHTML, mapVar=mapVar, numIncidents=numIncidents, factors=factors, numFactors=len(data.stateCols[1:]), selectedIndex=selectedIndex)

if __name__ == '__main__':
    app.run(debug=True)

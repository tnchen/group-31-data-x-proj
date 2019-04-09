from flask import *
import folium
import math
import re

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/map', methods=['GET', 'POST'])
def map():
    
    if request.method == 'POST':
        # Get form info
        numIncidents = request.form['numIncidents']
        center = request.form['center']
        zoom = int(request.form['zoom'])

        # Extract the map center
        center = re.findall('LatLng\((.+), (.+)\)', center)[0]
        center = [float(val) for val in center]
    else:
        numIncidents = 50
        zoom = 4
        center = [35, -97]

    # Create the map
    mapObj = folium.Map(location=center, zoom_start=zoom, tiles='Mapbox Bright', width='75%', height='75%')

    # Extract the HTML and make it safe
    mapHTML = mapObj.get_root().render()
    mapVar = re.findall('(map_[a-z0-9]+)', mapHTML)[0]
    mapHTML = Markup(mapHTML)

    return render_template('map.html', map=mapHTML, mapVar = mapVar, numIncidents=numIncidents)

if __name__ == '__main__':
    app.run(debug=True)

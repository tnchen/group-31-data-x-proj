from flask import *
import folium

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/map', methods=['GET', 'POST'])
def map():
    # Get the user settings
    if request.method == 'POST':
    	numIncidents = request.form['numIncidents']
    else:
    	numIncidents = 50

    # Create the map
    map_obj = folium.Map(location=[35, -97], zoom_start=4, tiles='Mapbox Bright', width='50%', height='50%')

    # Extract the HTML and make it safe
    map_html = Markup(map_obj.get_root().render())
    print(map_html)

    return render_template('map.html', map=map_html, numIncidents=numIncidents)

if __name__ == '__main__':
    app.run(debug=True)

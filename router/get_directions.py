import numpy as np

__author__    = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__   = 'MIT'
__version__   = '0.1'


class router():
    def __init__(self):
        super().__init__()


    def bearing_wpts(a, b):
        dlat = np.deg2rad(b[0] - a[0])
        dlon = np.deg2rad(b[1] - a[1])

        dlon = dlon * np.cos(np.deg2rad(a[0]))

        return(np.rad2deg(np.arctan(dlon, dlat)))


    def distance_wtps(a, b, haversine=False):
        if (haversine):
            return (distance_haversine(a, b))
        __lat1__ = np.deg2rad(a[0])
        __lon1__ = np.deg2rad(a[1])
        __lat2__ = np.deg2rad(b[0])
        __lon2__ = np.deg2rad(b[1])
        d = np.arccos(np.sin(__lat1__) * np.sin(__lat2__) + np.cos(__lat1__) * np.cos(__lat2__) * np.cos(__lon2__ - __lon1__)) * 6371
        return (d)

    def distance_haversine_wtps(a, b):
        dlat = radians(b[0] - a[0])
        dlon = radians(b[1] - a[1])
        a1 = sin(0.5 * dlat)
        a2a = cos(radians(a[0]))
        a2b = cos(radians(b[0]))
        a3 = sin(0.5 * dlon)

        a = a1 * a1 + a2a * a2b * a3 * a3
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        d = 6371 * c
        return (d)

current_gps_lat = 48.0852887
current_gps_lon = 11.275966400000016
destination = "Elsenheimerstraße 12, 80687 München"

# Clients: decoding and directions from different API
gmapsdec = googlemaps.Client(key='AIzaSyB2rlaAh6WWerqd7gdoSLy7FEe28DO5qHM')
gmapsdir = googlemaps.Client(key='AIzaSyAp8jxy8GHeOJWyktGFCEfM14diGsGZ-yA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmapsdec.reverse_geocode((current_gps_lat, current_gps_lon))
current_address = reverse_geocode_result[0]['formatted_address']

# Request directions via public transit
now = datetime.now()
directions_result = gmapsdir.directions(current_address,
                                     destination,
                                     mode="driving")
summary_travel = 'via: ' + directions_result[0]['summary']
istructions    = directions_result[0]['legs'][0]['steps']
lat_istr       = np.zeros((len(istructions),1))
lon_istr       = np.zeros((len(istructions),1))

print(len(lat_istr))
for i in np.arange(0, len(istructions)):
    istructions_mod = istructions[i]['html_instructions']
    istructions_mod = re.sub('<b>', '', istructions_mod)
    istructions_mod = re.sub('</b>', '', istructions_mod)
    istructions_mod = re.sub('</div>', '', istructions_mod)
    istructions_mod = re.sub('<div style="font-size:0.9em">', ' - ', istructions_mod)
    #print(istructions_mod)
    try:
        print(istructions[i]['maneuver'])
    except KeyError:
        print('No maneuver')
    lat_istr[i] = istructions[i]['end_location']['lat']
    lon_istr[i] = istructions[i]['end_location']['lng']

test_lat_rand = np.random.rand(len(istructions),1)*0.0001
test_lon_rand = np.random.rand(len(istructions),1)*0.0001

new_lat_curr = lat_istr - test_lat_rand
new_lon_curr = lon_istr - test_lon_rand

curr_bearing  = np.zeros(np.shape(lat_istr))
curr_distance = np.zeros(np.shape(lat_istr))

for i in np.arange(0, np.shape(lat_istr)[0]):
    lat_array = np.array([new_lat_curr[i], lat_istr[i]])
    lon_array = np.array([new_lon_curr[i], lon_istr[i]])

    curr_bearing[i]  = bearing(lat_array, lon_array)
    curr_distance[i] = distance(lat_array, lon_array, False)

print(curr_bearing)
print(curr_distance)

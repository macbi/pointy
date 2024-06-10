import eel
from pyproj import Transformer
import requests
from owslib.wms import WebMapService

eel.init('web')                     # Give folder containing web files

@eel.expose                         # Expose this function to Javascript
def handleinput(x):
    print('%s' % x)

@eel.expose
def getHeight(X,Y,coordinate_system):
    print(X,Y,coordinate_system)
    transfomer = Transformer.from_crs(f'epsg:{coordinate_system}', "epsg:2180")
    transformed = transfomer.transform(Y, X) # Y first, X second, return x, y

    print(transformed)
    
    respone = requests.get(f'https://services.gugik.gov.pl/nmt/?request=GetHByXY&x={transformed[0]}&y={transformed[1]}')
    print(respone.json(), respone.status_code)
    return respone.json()

@eel.expose
def getMap(X,Y,coordinate_system):
    wms = WebMapService("https://mapy.geoportal.gov.pl/wss/service/img/guest/TOPO/MapServer/WMSServer")
    x = Y
    y = X
    print(x, y)
    transformer = Transformer.from_crs(f'epsg:{coordinate_system}', "epsg:2180") # second value is always 2180, first need to be adjusted to your data
    x_trans, y_trans = transformer.transform(x, y)
    max_y = y_trans + 6000
    min_y = y_trans - 6000
    min_x = x_trans - 6000
    max_x = x_trans + 6000
    img = wms.getmap(layers=['Raster'], styles=['default'], srs='EPSG:2180', bbox=( min_y, min_x, max_y, max_x), size=(1000, 1000), format='image/jpeg', transparent=True)
    with open('web/map.jpg', 'wb') as out:
        out.write(img.read())



eel.say_hello_js('connected!')   # Call a Javascript function

eel.start('main.html', size=(1000, 1000))    # Start
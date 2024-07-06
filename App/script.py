import eel
from pyproj import Transformer
import requests
from owslib.wms import WebMapService
import wx
import pandas as pd

eel.init('web')                     # Give folder containing web files

pointData = pd.DataFrame()
fileName = ""
wildcard="Pliki Excel (*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt)|*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt"

@eel.expose                         # Expose this function to Javascript
def handleinput(x):
    print('%s' % x)

def transformCoordinates(X,Y,input_crs,output_crs):
    transfomer = Transformer.from_crs(f'epsg:{input_crs}', f'epsg:{output_crs}')
    x, y = transfomer.transform(Y, X) # Y first, X second, return x, y
    return x, y

    # x = row['Y_2000']
    # y = row['X_2000']
    # transformer = Transformer.from_crs("epsg:2176", "epsg:4326") # second value is always 2180, first need to be adjusted to your data
    # x, y = transformer.transform(x, y)

def getPointHeight(X,Y,input_crs):
    #check if x and y are numbers
    try:
        X = float(X)
        Y = float(Y)
    except ValueError:
        return {'X and Y must be numbers'}

    x, y = transformCoordinates(X,Y,input_crs,2180)
    print(f'X: {x}, Y: {y}')
    
    response = requests.get(f'https://services.gugik.gov.pl/nmt/?request=GetHByXY&x={x}&y={y}')
    print(response.json(), response.status_code)
    if response.status_code != 200:
        return {'server error'}
    return response.json()

@eel.expose
def addHeightToDataFrame(input_crs):
    global pointData
    df = pointData
    df['Height'] = df.apply(lambda row: getPointHeight(row['X'], row['Y'], input_crs), axis=1)
    pointData = df
    return df.to_html(index=False, justify="left").replace('<table border="1" class="dataframe">','<table class="table table-striped table-bordered table-sm">') # use bootstrap styling


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

@eel.expose
def getFilePath(): 
    app = wx.App(None) ## necessary for opening dialog
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.STAY_ON_TOP
    with wx.FileDialog(None, 'Open', wildcard=wildcard, style=style) as dialog:
        if dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

        path = dialog.GetPath()
        global fileName
        fileName = dialog.GetFilename()

        return path
    
def getOutputFilePath():
    app = wx.App(None)
    style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.STAY_ON_TOP
    with wx.FileDialog(None, 'Save', wildcard=wildcard, style=style, defaultFile=f"{fileName.split('.')[0]}_results.xlsx") as dialog:
        if dialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed their mind

        path = dialog.GetPath()

        return path
    
@eel.expose
def saveDataFrameToExcel():
    path = getOutputFilePath()
    if path:
        pointData.to_excel(path, index=False)


@eel.expose
def getExcelSheetNames(path):
    xl = pd.ExcelFile(path)
    return xl.sheet_names

@eel.expose
def getHTMLTable(path, sheet_name, headers):
    df = pd.read_excel(path, sheet_name)
    df = df[headers]
    global pointData
    pointData = df
    return df.to_html(index=False, justify="left").replace('<table border="1" class="dataframe">','<table class="table table-striped table-bordered table-sm">') # use bootstrap styling

def getHeaders(df):
    return df.columns.values.tolist()

@eel.expose
def getExcelSheetData(path, sheet_name):
    xl = pd.ExcelFile(path)
    return getHeaders(xl.parse(sheet_name))


eel.say_hello_js('connected!')   # Call a Javascript function

eel.start('main.html', cmdline_args=['--start-maximized'])    # Start
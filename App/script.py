import time
import eel
from pyproj import Transformer
import requests

import pandas as pd
from tkinter import Tk
from tkinter import filedialog

root = Tk()
root.attributes('-topmost', True)  # Display the dialog in the foreground.
root.withdraw()  # Hide the little window.

eel.init('web')                     # Give folder containing web files

pointData = pd.DataFrame()
fileName = ""
wildcard="Pliki Excel (*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt)|*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt"

@eel.expose                         # Expose this function to Javascript
def handleinput(x):
    print('%s' % x)

eel.say_hello_js('connected!')   # Call a Javascript function

def transformCoordinates(X,Y,input_crs,output_crs):
    transfomer = Transformer.from_crs(f'epsg:{input_crs}', f'epsg:{output_crs}')
    x, y = transfomer.transform(Y, X) # Y first, X second, return x, y
    return x, y

## Get height of point from GUGiK API

def getPointHeight(X,Y,input_crs):
    #check if x and y are numbers
    try:
        X = float(X)
        Y = float(Y)
    except ValueError:
        return 'X and Y must be numbers'

    if input_crs != 2180:
        x, y = transformCoordinates(X,Y,input_crs,2180)
        print(f'X: {x}, Y: {y}')
    else:
        x = Y
        y = X 
    
    # wait to avoid server error
    time.sleep(0.5)

    response = requests.get(f'https://services.gugik.gov.pl/nmt/?request=GetHByXY&x={x}&y={y}')
    print(response.status_code)
    if response.status_code != 200:
        print(response.text)
        return 'server error'
    print(response.json())
    return response.json()

@eel.expose
def addHeightToDataFrame(input_crs):
    global pointData
    pointData['Height'] = pointData.apply(lambda row: getPointHeight(row['X'], row['Y'], input_crs), axis=1)
    return pointData.to_html(index=False, justify="left").replace('<table border="1" class="dataframe">','<table class="table table-striped table-bordered table-sm">') # use bootstrap styling


## File path handling

@eel.expose
def getFilePath(): 

    filePath = filedialog.askopenfilename(filetypes=[('Excel files', '*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt')])
    global fileName
    fileName = filePath.split('/')[-1]

    return filePath
    
def getOutputFilePath():

    return filedialog.asksaveasfilename(defaultextension='.xlsx', initialfile = f"{fileName.split('.')[0]}_results")
    
## Data frame handling

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
    # update headers names to number, X and Y
    df.columns = ['Name', 'X', 'Y']
    global pointData
    pointData = df
    return df.to_html(index=False, justify="left").replace('<table border="1" class="dataframe">','<table class="table table-striped table-bordered table-sm">') # use bootstrap styling

def getHeaders(df):
    return df.columns.values.tolist()

@eel.expose
def getExcelSheetData(path, sheet_name):
    xl = pd.ExcelFile(path)
    return getHeaders(xl.parse(sheet_name))

## map handling

@eel.expose
def showPointsOnMap(input_crs):
    eel.clearMap()
    pointsList = []

    for index, row in pointData.iterrows():
        #check if x and y are numbers
        try:
            X = float(row['X'])
            Y = float(row['Y'])
        except ValueError:
            print('X and Y must be numbers')
            continue
        x, y = transformCoordinates(X,Y,input_crs,4326)
        print(f'x: {x}, y: {y}, Name: {row["Name"]}')
        eel.addMarker(x, y, row['Name'])
        pointsList.append([x, y])  

    eel.getCenterAndFlyTo(pointsList)

eel.start('main.html', cmdline_args=['--start-maximized'])    # Start
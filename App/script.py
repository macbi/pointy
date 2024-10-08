import time
import eel
from pyproj import Transformer
import requests
import pandas as pd
from tkinter import Tk
from tkinter import filedialog
import simplekml

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
    for index, row in pointData.iterrows():
        height = getPointHeight(row['X'],row['Y'],input_crs)
        pointData.at[index, 'Height'] = height
        updateProgress(f"{(index+1)}/{len(pointData)}")
    return pointData.to_html(index=False, justify="left").replace('<table border="1" class="dataframe">','<table class="table table-striped table-bordered table-sm">') # use bootstrap styling


def updateProgress(progress):
    eel.updateProgress(progress)

## File path handling

@eel.expose
def getFilePath(): 

    filePath = filedialog.askopenfilename(filetypes=[('Excel files', '*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt')])
    global fileName
    fileName = filePath.split('/')[-1]

    return filePath
    
def getOutputFilePath(extension):

    return filedialog.asksaveasfilename(defaultextension=extension, initialfile = f"{fileName.split('.')[0]}_results", filetypes=[("All Files","*.*")])
    
## Data frame handling

@eel.expose
def saveDataFrameToExcel():
    path = getOutputFilePath('.xlsx')
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
        
        height = row.get('Height')
        if height:
            popupName = f'<p><b>{row["Name"]}</b> <br> {height} m ASL</p>'
        else:
            popupName = f'<p><b>{row["Name"]}</b></p>'
        eel.addMarker(x, y, popupName)
        pointsList.append([x, y])  

    eel.getCenterAndFlyTo(pointsList)

## KML handling

def dataFrameToKml(df, input_crs):
    kml = simplekml.Kml()
    for index, row in pointData.iterrows():
        #check if x and y are numbers
        X = float(row['X'])
        Y = float(row['Y'])
        x, y = transformCoordinates(X,Y,input_crs,4326)
        print(f'x: {x}, y: {y}, Name: {row["Name"]}')
        point = kml.newpoint(name=row['Name'], coords=[(y,x)])
        
        height = row.get('Height')
        if height:
            point.description = f'{height} m ASL'
    return kml

@eel.expose
def saveDataFrameToKML(input_crs):
    kml = dataFrameToKml(pointData, input_crs)
    kml.document.name = fileName.split('.')[0]
    path = getOutputFilePath('.kml')
    if path:
        kml.save(path)


eel.start('main.html', cmdline_args=['--start-maximized'])    # Start
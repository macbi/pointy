import time
import eel
from pyproj import Transformer, CRS, exceptions
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
loggingList = []
fileName = ""
filePath = ""

@eel.expose
def log(message):
    loggingList.insert(0, message)
    eel.updateList("logging-list", loggingList)

@eel.expose
def validateEPSG(epsg):
    print(f'EPSG: {epsg}')
    try:
        epsg = int(epsg)
    except ValueError:
        print('EPSG must be a number')
        return False
    if epsg < 2000 or epsg > 10000:
        print('EPSG must be between 2000 and 10000')
        return False
    try:
        CRS.from_epsg(epsg)
        return True
    except exceptions.CRSError:
        print('EPSG not found')
        return False


def transformCoordinates(X,Y,input_crs,output_crs):
    transfomer = Transformer.from_crs(f'epsg:{input_crs}', f'epsg:{output_crs}')
    x, y = transfomer.transform(Y, X) # Y first, X second, return x, y
    return x, y

## Get height of point from GUGiK API

def getPointHeight(name,X,Y,input_crs):
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
    time.sleep(0.1)

    response = requests.get(f'https://services.gugik.gov.pl/nmt/?request=GetHByXY&x={x}&y={y}')
    print(response.status_code)
    if response.status_code != 200:
        log({"type":'error', "message":f'{response.status_code} - server error for point {name}'})
        print(response.text)
        return 'server error'
    print(response.json())
    return response.json()

@eel.expose
def addHeightToDataFrame(input_crs):
    # TODO: fix adding multiple "_heights" to file name, when you don't change sheet
    global fileName
    fileName = fileName.split('.')[0] + '_heights'
    
    global pointData
    errorNumber = 0
    log({"type":'info',"message":f'Adding heights to all points from <a href="https://services.gugik.gov.pl/nmt/" target="_blank">GUGiK API</a>'})
    for index, row in pointData.iterrows():
        
        height = getPointHeight(row['Name'],row['X'],row['Y'],input_crs)
        if height == 'server error':
            errorNumber += 1
        pointData.at[index, 'Height'] = height
        updateProgress(f"{(index+1)}/{len(pointData)}")
    if errorNumber > 0:
        log({"type":'warning', "message":f'{errorNumber} point{"s" if (errorNumber > 1) else ""} with server error', "actionId": "btn_addMissingHeights"})
    else:
        log({"type":'success', "message":f'Heights added to all points'})
    return getHTMLTable(pointData)

def updateProgress(progress):
    eel.updateProgress(progress)
    
@eel.expose
def addMissingHeights(input_crs):
    global pointData
    errordedPointsNumber = len(pointData[pointData['Height']=='server error'])
    errorNumber = 0
    doneNumber = 0
    for index, row in pointData.iterrows():
        if row['Height']=='server error':
            height = getPointHeight(row['Name'],row['X'],row['Y'],input_crs)
            if height == 'server error':
                errorNumber += 1
            pointData.at[index, 'Height'] = height
            doneNumber += 1
            updateProgress(f"{(doneNumber)}/{errordedPointsNumber}")
    if errorNumber > 0:
        log({"type":'warning', "message":f'{errorNumber} point{"s" if (errorNumber > 1) else ""} with server error', "actionId": "btn_addMissingHeights"})
    else:
        log({"type":'success', "message":f'Heights added to all missing points'})
    return getHTMLTable(pointData)

## File path handling

@eel.expose
def getFilePath(): 

    path = filedialog.askopenfilename(filetypes=[('Excel files', '*.xlsx')])
    global filePath
    filePath = path
    
    global fileName
    fileName = path.split('/')[-1]

    return filePath
    
def getOutputFilePath(extension):

    return filedialog.asksaveasfilename(defaultextension=extension, initialfile = fileName.split('.')[0], filetypes=[("All Files","*.*")])
    
## Data frame handling

@eel.expose
def saveDataFrameWithTransformedCoordinates(input_crs, output_crs):
    global fileName
    oldFileName = fileName
    fileName = fileName.split('.')[0] + f'_to_{output_crs}'
    path = getOutputFilePath('.xlsx')

    transformedPointData = pointData.copy()
    if path:
        try:
            for index, row in pointData.iterrows():
                #check if x and y are numbers
                try:
                    X = float(row['X'])
                    Y = float(row['Y'])
                    Y, X = transformCoordinates(X,Y,input_crs,output_crs)
                    #overwrite X and Y with transformed values
                    transformedPointData.at[index, 'X'] = X
                    transformedPointData.at[index, 'Y'] = Y
                except ValueError:
                    continue
                
            #add name of new crs to x y columns
            transformedPointData.rename(columns={'X': f'X_{output_crs}', 'Y': f'Y_{output_crs}'}, inplace=True)    
            transformedPointData.to_excel(path, index=False)
            log({"type":'success', "message":f'Excel file saved at {path}'})
        except Exception as e:
            log({"type":'error', "message":f'Error saving Excel file: {e}'})
    fileName = oldFileName

@eel.expose
def saveDataFrameToExcel():
    path = getOutputFilePath('.xlsx')
    if path:
        try:
            pointData.to_excel(path, index=False)
            log({"type":'success', "message":f'Excel file saved at {path}'})
        except Exception as e:
            log({"type":'error', "message":f'Error saving Excel file: {e}'})
            
@eel.expose
def saveDataFrameToCSV():
    path = getOutputFilePath('.csv')
    if path:
        try:
            pointData.to_csv(path, index=False)
            log({"type":'success', "message":f'CSV file saved at {path}'})
        except Exception as e:
            log({"type":'error', "message":f'Error saving CSV file: {e}'})


@eel.expose
def getExcelSheetNames(path):
    xl = pd.ExcelFile(path)
    return xl.sheet_names

@eel.expose
def createIntialTable(path, sheet_name, headers):
    try:
        df = pd.read_excel(path, sheet_name)
    except Exception as e:
        log({"type":'error', "message":f'Error loading Excel file: {e}'})
        return
    
    df = df[headers]
    # update headers names to number, X and Y
    df.columns = ['Name', 'X', 'Y']
    # validate if X and Y columns have values
    if df['X'].isnull().values.any() or df['Y'].isnull().values.any():
        log({"type":'error', "message":'X and Y columns must have values. Points with empty X or Y will be omitted.'})
        #insert "no data" to empty cells, those cells will be omitted in map and calculations
        df['X'].fillna('no data', inplace=True)
        df['Y'].fillna('no data', inplace=True)   
    # validate if X and Y columns have numbers
    if not pd.to_numeric(df['X'], errors='coerce').notnull().all() or not pd.to_numeric(df['Y'], errors='coerce').notnull().all():
        log({"type":'error', "message":'X and Y columns must have numbers. Points with non-numeric X or Y will be omitted.'})     
    global pointData
    pointData = df
    
    # remove all suffixes from file name
    global fileName, filePath
    fileName = filePath.split('/')[-1]
    
    log({"message":f'Excel file loaded: {len(pointData)} points'})
    return getHTMLTable(pointData)

def getHTMLTable(df):
    return df.to_html(index=False, justify="left").replace('<table border="1" class="dataframe">','<table id="table" class="table table-striped table-bordered table-sm">') # use bootstrap styling

@eel.expose
def getExcelSheetHeaders(path, sheet_name):
    xl = pd.ExcelFile(path)
    return xl.parse(sheet_name).columns.values.tolist()

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

def dataFrameToKml(input_crs):
    kml = simplekml.Kml()
    for index, row in pointData.iterrows():
        height = row.get('Height')
        
        #check if x and y are numbers
        try:
            X = float(row['X'])
            Y = float(row['Y'])
        except ValueError:
            continue
        x, y = transformCoordinates(X,Y,input_crs,4326)

        if height:
            try:
                z = float(height)
                point = kml.newpoint(name=row['Name'], coords=[(y,x,z)])
                point.description = f'{height} m ASL'
            except ValueError:
                log({"type":'warning', "message": f'{row["Name"]} height was not a number - omitting Z value'})
                point = kml.newpoint(name=row['Name'], coords=[(y,x)])
        else:
            print(f'x: {x}, y: {y}, Name: {row["Name"]}')
            point = kml.newpoint(name=row['Name'], coords=[(y,x)])
            
    return kml

@eel.expose
def saveDataFrameToKML(input_crs):
    kml = dataFrameToKml(input_crs)
    kml.document.name = fileName.split('.')[0]
    path = getOutputFilePath('.kml')
    if path:
        try:
            kml.save(path)
            log({"type":'success', "message":f'KML file saved at {path}'})
        except Exception as e:
            log({"type":'error', "message":f'Error saving KML file: {e}'})


eel.start('main.html', cmdline_args=['--start-maximized'])    # Start
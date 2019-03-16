import pandas as pd
from datetime import datetime as dt
import random
import glob

def getAvailableDate(source):
    history = pd.read_csv(source)
    # startDate = history['DATE'][0]
    # endDate = history['DATE'][history.shape[0]-1]
    history['dep_time']=pd.to_datetime(history['dep_time'])
    history['Date'] = history['dep_time'].dt.date
    availableDate = history['Date'].unique().tolist()
    return availableDate


def validateDate(dateArr):
    dateStart = dt.strptime(dateArr[0], "%Y-%m-%d")
    dateEnd = dt.strptime(dateArr[1], "%Y-%m-%d")
    if dateStart > dateEnd:
        print("--FALSE DATE--")
        return False
    else:
        return True

def loadBookingByDate(dateStartIn, dateEndIn):
    dateStart = dt.strptime(dateStartIn, "%Y-%m-%d")
    dateEnd = dt.strptime(dateEndIn, "%Y-%m-%d")
    targetBooking = pd.read_csv('./resources/bookings.csv')
    targetBooking['dep_time']=pd.to_datetime(targetBooking['dep_time'])
    mask = (targetBooking['dep_time'] > dateStart) & (targetBooking['dep_time'] <= dateEnd)
    return targetBooking.loc[mask]

def loadHistoryByDate(dateStartIn, dateEndIn):
    dateStart = dt.strptime(dateStartIn, "%Y-%m-%d")
    dateEnd = dt.strptime(dateEndIn, "%Y-%m-%d")
    targetHistory = pd.read_csv('./resources/yearHistoryTemplate.csv')
    targetHistory['dep_time']=pd.to_datetime(targetHistory['dep_time'])
    mask = (targetHistory['dep_time'] > dateStart) & (targetHistory['dep_time'] <= dateEnd)
    return targetHistory.loc[mask]

def getCurrentExternFile():
    files = glob.glob('upload/'+"*.csv")
    # return render_template('bookings.html',  options=files)
    return files

def checkUploadFile(filename):
    print(filename[-4 ::])
    if filename[-4 ::] != '.csv':
        return False
    else:
        return True

def integrateData(mapCol, integrateCols, startDate, endDate, externFile):
    print(integrateCols)
    print(mapCol)
    print(startDate + " " + endDate + " " + externFile)
    df = loadHistoryByDate(startDate, endDate)
    extdf = pd.read_csv(externFile)
    df['DATE'] = pd.to_datetime(df['dep_time'], format = '%Y-%m-%d').dt.date
    extdf[mapCol] = pd.to_datetime(extdf['DATE'], format = '%Y-%m-%d').dt.date
    for ele in integrateCols:
        df[ele] = df['DATE'].map(extdf.set_index('DATE')[ele])
    return df
# def insertRandom(df):
#     print("--inset value--")
#     nb = random.randint(0, int(df.shape[0]/4))
#     df = df.reset_index(drop=False)
#     indexs = []
#     for i in range(0, nb):
#         index = random.randint(0, df.shape[0])
#         indexs.append(index)
#     for i in indexs:
#         df.set_value(i,'isLate', 1)
#     df = df.set_index('DATE', inplace=True)
#     return df

# import predict
# startDate = '2018-08-20'
# endDate = '2018-08-30'
# data = predict.lrByDate([startDate, endDate])
# data.set_index(['DATE'], inplace=True)
# data = data[(data['isLate']==1)]
# if data:
#     print(data.shape)
# else:
#     print("None")

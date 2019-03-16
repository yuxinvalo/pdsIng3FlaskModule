import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
from datetime import datetime

def loadData():
    fait = pd.read_csv("resources/fait.csv")
    fait.drop(['Unnamed: 0'], axis=1, inplace=True)
    faitPred = pd.read_csv("resources/FaitAPred.csv")
    faitPred.drop(['Unnamed: 0'], axis=1, inplace=True)
    return fait, faitPred

# DONNO HOW TO TRANSFER IT
from sklearn import preprocessing

def cleanData(fait):
    print("--clean data--")
    lb = preprocessing.LabelBinarizer()
    def rep_precip(x):
        if x < 3.0:
            return 'precip_faible'
        elif x >= 3. and x < 5.:
            return 'precip_moyen'
        else :
            return 'precip_fort'

# definition visibility
# faible = < 5km
# moyen = >= 5km and < 8km
# bonne = >= 8km
    def rep_visib(x):
        if x < 5.:
            return 'visib_faible'
        elif x >= 5. and x < 8.:
            return 'visib_moyen'
        else :
            return 'visib_fort'
# definition month
# haute = 7, 8
# basse = other months
    def rep_month(x):
        if x is 7 or x is 8:
            return 'month_haute'
        else:
            return 'month_basse'
# definition hour
# pointe = in 7, 8, 12, 13, 19, 20
# creuse in other hours
    def rep_hour(x):
        if x in [7, 8, 12, 13, 19, 20]:
            return 'hour_pointe'
        else:
            return 'hour_creuse'
    fait['precip'] = fait['precipitation'].apply(lambda x: rep_precip(x))
    fait['visib'] = fait['visibility'].apply(lambda x: rep_visib(x))
    fait['month'] = fait['month'].apply(lambda x: rep_month(x))
    fait['hour'] = fait['hour'].apply(lambda x: rep_hour(x))
    fait.drop(['visibility', 'precipitation'], axis=1, inplace=True)
    dummies_col = ['month', 'hour', 'precip', 'visib']
    for each in dummies_col:
        dummy = pd.get_dummies(fait[each])
        fait = pd.concat([fait, dummy], axis=1)
    fait.drop(['month','hour', 'precip', 'visib'], axis=1, inplace=True)
    print("--clean data finish--")
    return fait


def adjustCol(faitPred):
    cols = ['month_basse', 'month_haute', 'hour_creuse', 'hour_pointe',\
       'precip_faible', 'precip_fort', 'precip_moyen', 'visib_fort',\
       'visib_moyen', 'visib_faible']
    if(len(faitPred.columns) != len(cols)):
        i = len(cols) - len(faitPred.columns)
        print("--adjust column: i : " + str(i) + "--")
        for index,ele in enumerate(faitPred.columns):
            if ele != cols[index]:
                newCol = 0
                faitPred.insert(loc=0, column=cols[index], value=newCol)
                i = i + 1
        if i != 0:
            for x in range(0, i):
                print("--missing column nb: " + str(len(faitPred.columns)+x)+ ".--")
                newCol = 0
                faitPred[cols[len(faitPred.columns)+x]] = 0
    print("--adjust columns of faitPred:" + faitPred.columns)
    return faitPred

def splitTrainData(fait):
    print("--split data--")
    faitX = fait.drop('isLate', axis=1)
    x_train, x_test, y_train, y_test = train_test_split\
    (faitX, fait.isLate, test_size=0.33, random_state=0)
    print("--split finish--")
    return x_train, x_test, y_train, y_test

def getPredData(faitPred, dateStart, dateEnd):
    print("--get predictive data--")
    dateStart = datetime.strptime(dateStart, "%Y-%m-%d")
    dateEnd = datetime.strptime(dateEnd, "%Y-%m-%d")
    faitPred['DATE'] = pd.to_datetime(faitPred['DATE'], format="%Y-%m-%d")
    mask = (faitPred['DATE'] >= dateStart) & (faitPred['DATE'] <= dateEnd)
    res = faitPred.loc[mask]
    resDate =  pd.concat([res['DATE']], axis=1, keys=["DATE"])
    res.drop(['DATE'], axis=1, inplace=True)
    res = adjustCol(res)
    print("--get predictive data finish--")
    return res,resDate

def lrByDate(dateArr):
    fait, faitPred = loadData()
    faitPred = cleanData(faitPred)
    dateStart = dateArr[0]
    dateEnd = dateArr[len(dateArr) - 1]

    faitX = fait.drop('isLate', axis=1)
    x_train, x_test, y_train, y_test = splitTrainData(fait)
    lr = LogisticRegression()
    lr.fit(x_train, y_train)
#     resPred = lr.predict(x_test)
    y_pred = lr.predict(x_test)
    score = metrics.accuracy_score(y_test, y_pred)
    resPred, resDate = getPredData(faitPred, dateStart, dateEnd)
    resY = lr.predict(resPred)
    resPred['isLate'] = resY
    resPred['DATE'] = resDate['DATE']
    return resPred,score

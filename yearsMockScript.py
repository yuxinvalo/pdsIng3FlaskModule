# Editor: Tearsyu
# PDS
# Generate history records
# Estimate number : 123774/356 = 347
import pandas as pd
import datetime
import random
import math

# Constraints: - 3000 clients (how many active clients?) and 173 parkings
#              - Paris accepts largest numbers of visiters in July, like a normal distribution
#              - At a common day, 00-06 clock there is less use times, from 7 to 8, 12 to 13, 19 to 20, there is more use times
#              - We need a bundle of high random data with the constraints above.


clients = 3000
parkings = 173

# getOneDayData(day, base_time_day) takes 2 arguments
# %day% the datetime like 2018-09-10
# %base_time_day% is the basic times of one day, according to our vision doc, this value is 347
def getOneDayData(day, base_time_day):
    currHours = day.hour
    currMonth = day.month
    # seedSign is used to add a random seed of times, some days there is more use times while some days less.
    seedSign = random.choice(["+", "-"]);
    hourTimes = 0
    res = []
    histId = 1
    seedBaseHourTimes = int(base_time_day/24)
    for currHours in range(0, 24):
        if seedSign == '+':
            # baseHourTimes gives a basic use times of one hour, it ranges from 347/12-squart(347/12) to 347/12+squart(347/12)
            baseHourTimes = seedBaseHourTimes + random.randint(0, seedBaseHourTimes + int(math.sqrt(seedBaseHourTimes)))
        else:
            baseHourTimes = seedBaseHourTimes - random.randint(0, seedBaseHourTimes - int(math.sqrt(seedBaseHourTimes)))
        
        # taux is an other random seed of ever hour, from 0.1 to 0.3 or from 1.4 to 3.5, 
        # this data comes from google map, the metro use times in every hour 
        if (currHours >= 0 and currHours <= 6):
            taux = random.uniform(0.1, 0.3)
            hourTimes = int(baseHourTimes * taux)
            
        elif(currHours in [7, 8, 12, 13, 19, 20]):
            taux = random.uniform(1.4, 3.5)
            hourTimes = baseHourTimes + int(taux * baseHourTimes)
        else:
            hourTimes = baseHourTimes
        
        #print("hourTimes is " + str(hourTimes) + " at currHours is " + str(currHours))
    
        for i in range(0, hourTimes):
            userId = random.randint(1, clients)
            depId = random.randint(1, parkings)
            arrId = random.choice([i for i in range(1, parkings) if i not in [depId]])
            depDateTime, arrDateTime = getTravelTime(day, currHours)
            lateMin = getLateMin(depDateTime, arrDateTime)
            travelTime = arrDateTime - depDateTime
            basePrice, supPrice = getPrice(lateMin, travelTime)
            oneTube = [histId, userId, depId, arrId, depDateTime, arrDateTime, lateMin, basePrice, supPrice]
            res.append(oneTube)
            histId = histId + 1
    #print("res length : " + str(len(res)) + " index is " + str(histId))
    return res
# generate a random traval's start time and it's duration         
def getTravelTime(day, currHours):
    depMin = random.randint(0, 59)
    duration = random.randint(1, 60)
    depDateTime = day + datetime.timedelta(hours=currHours, minutes = depMin)
    arrDateTime = depDateTime + datetime.timedelta(minutes = duration)
    return depDateTime, arrDateTime;

# generate if a travel is late, the possibility is 85%(maybe here need to correct..)
def getLateMin(depDateTime, arrDateTime):
    seed = random.randint(1, 1000)
    if seed > 850 :
        minutes = arrDateTime - depDateTime;
        minutes = int(minutes.total_seconds()/60)
        return random.randint(1, minutes)
    else: 
        return 0
# calculate a price for a trip
def getPrice(lateMin, travelTime):
    travelTime = int(travelTime.total_seconds()/60)
    seedSign = random.choice(["+", "-"])
    if seedSign is "+" :
        basePrice = travelTime * 1.00 - random.uniform(0.3, 1.2) * travelTime / 4
    else :
        basePrice = travelTime * 1.00 - random.uniform(0.3, 1.2) * travelTime / 2
    if lateMin == 0:
        return round(basePrice, 2), 0;
    else :
        return round(basePrice, 2), lateMin;

def generateYearHistory(base_time_day, year):
    cols = ["id", "client_id", "departure_id", "arrival_id", "depDateTime", "arrDateTime",
            "late_time", "base_price", "sup_price"]
    
    oneYearHist = []
    oneDayHist = []
    currMon = 1
    currDate = 1
    currDay = datetime.datetime(year, currMon, currDate)
    seedSign = random.choice(["+", "-"]);
    
    
    for i in range(0, 356):
        #print("now at " + str(currDay) + " month is " + str(currDay.month))
        if currDay.month in [7, 8]:
            currBaseTimeDay = base_time_day + int(random.uniform(2, 4) * math.sqrt(base_time_day))
        else:
            if seedSign is "+":
                currBaseTimeDay = base_time_day + int(random.uniform(0.3, 1.5) * math.sqrt(base_time_day))
            else : 
                currBaseTimeDay = base_time_day - int(random.uniform(3, 8) * math.sqrt(base_time_day))
        #print("base time of a day is " + str(currBaseTimeDay))
        oneDayHist = getOneDayData(currDay, currBaseTimeDay)
	# Combien two lists of history
        oneYearHist = [*oneYearHist, *oneDayHist] 
        currDay = currDay + datetime.timedelta(days = 1)
    #print("one year history length : " + str(len(oneYearHist)))
    df = pd.DataFrame(oneYearHist, columns=cols)   
    return df

#Ignore this function, it's just for test   
def testOnedayTimes(times):
    res = []
    for i in range(0, times):
        res.append(getOneDayData(347, 2017))
    print(res)

yearHistory = generateYearHistory(347, 2017)
yearHistory.to_csv("yearHistoryTemplate.csv", index=False, encoding='utf8')

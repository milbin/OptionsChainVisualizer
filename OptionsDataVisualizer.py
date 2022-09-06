import sys
import matplotlib
import requests
import json
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from enum import Enum
import math
from functools import cmp_to_key
from pathlib import Path

# SETTINGS:

''' 
Name of the ticker we want to get options data for
'''
TICKERNAME = "BBBY"

''' 
Polygon.io API key. 
In order to use this code you need to create a polygon.io account and subscribe to their starter options package.
'''
APIKEY = "ADD YOUR POLYGON API KEY HERE"

'''
Since getting options data for a ticker takes a while, any new data will be automatically cached.
Change this option to True after the first run in order to used the cached options data.
Change this option to False to ignore cache and fetch new options data.
'''
USECACHE = True

'''
Determines if the graph will show calls or puts.
'''
DISPLAYCALLS = True

'''
Determines weather each bar represents options for only the current strike or for the current strike and all strike prices before.
'''
CUMULATIVEBARS = True

'''
Number of pages to request from Polygon.io. Increase this number to get older data.
'''
NUMBEROFPAGES = 1000


def printJSON(jsonObject):
    print(json.dumps(jsonObject, indent=2))

def cacheOptionsData(data, ticker):
    with open(f"{ticker}OptionsData.pkl", "wb+") as f:
        pickle.dump(data, f)

def getOptionsDataCache(ticker):
    with open(f"{ticker}OptionsData.pkl", "rb") as f:
        return pickle.load(f)



class Plot:
    def __init__(self, options):
        self.options = options
        self.columns = []

    def printDF(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
            print(self.df)

    def optionsCompareSort(self, x, y):
        if x["strike_price"] < y["strike_price"]:
            return -1
        return 1

    def calculateStrikes(self):
        minStrike = sys.maxsize
        maxStrike = 0
        for option in options:
            strike = int(option["strike_price"])
            minStrike = min(strike, minStrike)
            maxStrike = max(strike, maxStrike)
        strikes = list(range(minStrike, maxStrike + 1))
        return strikes

    def makeColumns(self):
        for option in options:
            colName = f'{option["contract_type"]}s-{option["expiration_date"]}'
            self.columns.append(colName)
        self.columns = list(dict.fromkeys(self.columns))
        self.columns.sort()



    def createDF(self):
        self.makeColumns()
        strikes = self.calculateStrikes()
        self.df = pd.DataFrame(index=strikes, columns=self.columns)

    def addOptionsToDF(self, cumulativeBars):
        self.createDF()
        OISum = 0
        options = sorted(self.options, key=cmp_to_key(self.optionsCompareSort))
        previousStrike = -1
        for option in options:
            strike = int(option["strike_price"])
            optionOpenInt = option["properties"]["open_interest"] * 100
            colName = f'{option["contract_type"]}s-{option["expiration_date"]}'

            currentOpenInt = self.df.loc[strike, colName]

            if previousStrike != strike and cumulativeBars:
                OISum += optionOpenInt
                optionOpenInt += OISum
                previousStrike = strike
            else:
                OISum += optionOpenInt


            if math.isnan(currentOpenInt):
                self.df.loc[strike, colName] = int(optionOpenInt)
            else:
                self.df.loc[strike, colName] = int(currentOpenInt + optionOpenInt)

    def plotOptionsData(self, calls=True, cumulativeBars=False):
        self.addOptionsToDF(cumulativeBars)

        sns.set()
        ax = None
        width = 35
        if calls:
            callsDF = self.df.loc[: , (self.df.columns.str.contains("calls"))]  # make a dataframe with only calls
            self.df = callsDF
            if cumulativeBars:
                ax = callsDF.plot(kind='bar', stacked=True, figsize=(width, 8), color=['green'])
            else:
                ax = callsDF.plot(kind='bar', stacked=True, figsize=(width, 8))
        else:
            putsDF = self.df.loc[: , (self.df.columns.str.contains("puts"))]  # make a dataframe with only puts
            if cumulativeBars:
                ax = putsDF.plot(kind='bar', stacked=True, figsize=(width, 8), color=['green'])
            else:
                ax = putsDF.plot(kind='bar', stacked=True, figsize=(width, 8))


        ax.set_xlabel("Strike")
        ax.set_ylabel("Shares")
        ax.get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        ax.legend(bbox_to_anchor=(1, 1))
        plt.show()


class PolygonAPI:

    def __init__(self, apiKey: str):
        self.apiKey = apiKey
        self.baseURL = "https://api.polygon.io"
        self.authHeader = {"Authorization": f"Bearer {apiKey}"}

    def getOptions(self, ticker: str, pageLimit: int = 5):
        if USECACHE and Path(f"{ticker}OptionsData.pkl").is_file():
            return getOptionsDataCache(ticker)

        optionsList = self.getOptionsList(ticker, pageLimit)
        optionNumber = 1
        optionCount = len(optionsList)
        for option in optionsList:
            print(f"Getting Option {optionNumber}/{optionCount}")
            optionSnapshot = self.getOptionSnapshot(option["underlying_ticker"], option["ticker"])
            option["properties"] = optionSnapshot
            optionNumber += 1

        cacheOptionsData(optionsList, ticker)
        return optionsList

    def getOptionsList(self, ticker: str, pageLimit):
        endpoint = "/v3/reference/options/contracts"
        url = self.baseURL + endpoint
        params = {"underlying_ticker": ticker}

        jsonResponse = requests.get(url, headers=self.authHeader, params=params).json()
        optionsData = []

        if "results" in jsonResponse:
            optionsData = jsonResponse["results"]

        pageNumber = 1
        while "next_url" in jsonResponse:
            print(f"Getting Page {pageNumber}")
            url = jsonResponse["next_url"]
            jsonResponse = requests.get(url, headers=self.authHeader, params=params).json()
            if "results" in jsonResponse:
                optionsData.extend(jsonResponse["results"])
            if pageNumber > pageLimit:
                break
            pageNumber += 1

        return optionsData


    def getOptionSnapshot(self, underlyingTicker: str, contractTicker: str):
        endpoint = f"/v3/snapshot/options/{underlyingTicker}/{contractTicker}"
        url = self.baseURL + endpoint
        jsonResponse = requests.get(url, headers=self.authHeader).json()
        return jsonResponse["results"]

if APIKEY == "ADD YOUR POLYGON API KEY HERE":
    print("In order to use this code you need to create a polygon.io account and subscribe to their starter options package. Once you receive a Polygon.io API key, replace the APIKEY constant in the code.")
polygonAPI = PolygonAPI(APIKEY)
options = polygonAPI.getOptions(TICKERNAME, NUMBEROFPAGES)

plot = Plot(options)

plot.plotOptionsData(calls=DISPLAYCALLS, cumulativeBars=CUMULATIVEBARS)

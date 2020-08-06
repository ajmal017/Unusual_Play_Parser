import requests
from io import StringIO
import bs4 as bs
import re
import sys
import os
import openpyxl
import sqlite3

def resetSD(strikeData):
    for i in strikeData:
        strikeData[i] = []

os.chdir("/Users/X/UnusualWhalesHistory/")
smallList = "07-01-20_07-10-20.html"
rawplays = []
argList = []
plays = []
valid_symbols = "!@#$%^&*()_-+={}[]"

strikeData = []
strikeInfo = ["Symbol",
              "Date",
              "Style",
              "Strike",
              "Bid",
              "Ask",
              "Interest",
              "Volume",
              "IV",
              "Diff",
              "Price",
              "ChangePercent",
              "ChangeCost",
              ]

# Read the command line arguments and added file names to list
if len(sys.argv) > 1:
    print("CMD args accepted: ", sys.argv)

    for arg in sys.argv[:]:
        print(arg)
        argList.append(arg)

# If this is being run from the IDE
else:
    # argList = os.listdir()
    # Will be set to a certain file while practicing.
    argList.append(smallList)
    print("Running from IDE: ", argList)

[print("Arg: ", item) for item in sys.argv]
[print(item) for item in argList]

rawplays = []

#   The strikes in the files will be added to a database if they don't exist already.
for inputFile in argList:
    htmlData = open(str(inputFile), 'r')
    contents = htmlData.read()
    soup = bs.BeautifulSoup(contents, "html.parser")

    # For the strike
    strikePlays = soup.find_all("div", {"class": "markdown"})

    # Removes img tag
    for img in soup("img"):
        if isinstance(img, bs.element.Tag):
            img.decompose()

    for i in range(len(strikePlays)):
        string = []

        for j in range(len(strikePlays[i].text)):
            if ord(strikePlays[i].text[j]) < 122:
                string.append(strikePlays[i].text[j])
        strikeData.append(string)

    for i in range(len(strikeData)):
        print('[', i, ']: ', strikeData[i])

        # IndexError: list index out of range
        # [ 178 ]:  []

        while not strikeData[i][0].isalpha():
            del strikeData[i][0]

        strikeData[i] = ''.join(strikeData[i])
        print(strikeData[i])

    pattern_text = re.compile(r'''(?P<Symbol>\w{1,5})\s*
                                    (?P<Date>\d{4}-\d{2}-\d{2})\s*
                                    (?P<Style>\w{1})\s*\$
                                    (?P<Strike>\d{2,5}(\.\d{1,2})?)\s*Bid:\s*\$
                                    (?P<Bid>\d{1,5}(\.\d{1,2})?)\s*Ask:\s*\$
                                    (?P<Ask>\d{1,5}(\.\d{1,2})?)\s*Interest:\s*
                                    (?P<Interest>\d{1,7})\s*Volume:\s*
                                    (?P<Volume>\d{1,7})\s*IV:\s*
                                    (?P<IV>\d{1,4}(\.\d{1,2})?)%\s*%\s*Diff:\s*
                                    (?P<Diff>-?\d{1,4}(\.\d{1,2})?)%\s*Purchase:\s*\$
                                    (?P<Price>\d{1,4}(\.\d{1,2})?)
                                    ''', re.VERBOSE)

    # match = pattern_text.match(strikeData[0])
    # match.group("Date")

    for i in range(len(strikeData)):
        match = pattern_text.match(strikeData[i])

        for j in range(11):
            print(match.group(strikeInfo[j]))

        print('*' * 20)

    # Prints the value in each dict item for number v

    # For every item:
    #   if it doesn't exist in file:
    #       Write to excel file or text or sql

    for play in rawplays:
        all = pattern_text.finditer(play)

        for match in all:
            print(match)

'''
IQ 2020-07-17 P $25

Bid: $2.94
Ask: $2.99
Interest: 6
Volume: 447
IV: 73.12%
% Diff: 6.7%
Purchase: $23.43
'''

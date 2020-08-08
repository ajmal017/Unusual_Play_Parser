# TODO
# add sector
# add gui window
# add search by field name
# add gui progress bar(s)

import os
import re
import sys
import sqlite3
import bs4 as bs
from datetime import date


def resetSD(data):
    for i in data:
        data[i] = []


files = os.listdir("/Users/X/UnusualWhalesHistory/")
# Check the current date
# Make sure a file exists for everyday since and including 06-16-2020
# Run each file through this program and add it to the database
# Store variable of last run date and time


conn = sqlite3.connect("WhalePlays.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Plays(symbol TEXT, date TEXT, style TEXT, strike REAL,
                                                      bid REAL, ask REAL, interest INTEGER, volume INTEGER, iv REAL, diff REAL, price REAL)''')
os.chdir("")
smallList = "07-01-20_07-10-20.html"
strikeData = []
argList = []

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
              "ChangeCost"]

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

print("Gathering data...")

#   The strikes in the files will be added to a database if they don't exist already.
for inputFile in argList:
    htmlData = open(str(inputFile), 'r')
    contents = htmlData.read()
    soup = bs.BeautifulSoup(contents, "html.parser")

    # Removes img tag
    for img in soup("img"):
        if isinstance(img, bs.element.Tag):
            img.decompose()

    # For the strike
    strikePlays = soup.find_all("div", {"class": "chatlog__message"})

    for i in range(len(strikePlays)):
        string = []

        for j in range(len(strikePlays[i].text)):
            if strikePlays[i].text != 0:
                if ord(strikePlays[i].text[j]) < 122:
                    string.append(strikePlays[i].text[j])
        strikeData.append(string)

    for i in range(len(strikeData)):
        while not strikeData[i][0].isalpha():
            del strikeData[i][0]

        strikeData[i] = ''.join(strikeData[i])

    pattern_text = re.compile(r'''(?P<Symbol>\w{1,5})\s*
                                    (?P<Date>\d{4}-\d{2}-\d{2})\s*
                                    (?P<Style>\w)\s*\$
                                    (?P<Strike>\d{1,5}(\.\d{1,2})?)\s*Bid:\s*\$
                                    (?P<Bid>\d{1,5}(\.\d{1,2})?)\s*Ask:\s*\$
                                    (?P<Ask>\d{1,5}(\.\d{1,2})?)\s*Interest:\s*
                                    (?P<Interest>\d{1,7})\s*Volume:\s*
                                    (?P<Volume>\d{1,7})\s*IV:\s*
                                    (?P<IV>\d{1,4}(\.\d{1,2})?)%\s*%\s*Diff:\s*
                                    (?P<Diff>-?\d{1,4}(\.\d{1,2})?)%\s*Purchase:\s*\$
                                    (?P<Price>\d{1,4}(\.\d{1,2})?.*)''', re.VERBOSE)

    for i in range(len(strikeData)):
        details = []
        match = pattern_text.match(strikeData[i])

        for j in range(11):
            if j <= 2:
                details.append(match.group(strikeInfo[j]))
            else:
                details.append(float(match.group(strikeInfo[j])))
        #     print(strikeInfo[j], ":", details[j])
        # print('*' * 35)

        cursor.execute('''INSERT INTO Plays (symbol, date, style, strike, bid, ask, interest, volume, iv, diff, price)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', details)
        print("Inserted", i)

    conn.commit()

    print("File analysis complete, {0} records created.".format(len(strikeData)))
# strikeInfo = ["Symbol",  # string
#                   "Date",  # string or int int int
#                   "Style",  # string
#                   "Strike",  # int
#                   "Bid",  # int
#                   "Ask",  # int
#                   "Interest",  # int
#                   "Volume",  # int
#                   "IV",  # int
#                   "Diff",  # int
#                   "Price",  # int
#                   "ChangePercent",  # int, (price - strike) / price
#                   "ChangeCost"  # int, (price - strike)
#                   ]
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

# TODO
# add sector
# add gui window
# add search by field name
# add gui progress bar(s)
# Add date scanned
# Add csv and json support along side the existing html parsing

# https://github.com/Tyrrrz/DiscordChatExporter/wiki/
# Created the discord scraper, DiscordChatExporter

import os
import re
import sqlite3
import bs4 as bs
import subprocess
from datetime import date, timedelta, datetime


def getHTML(playdate = "", after = "", before = "", numberday = "", outputFile = "", override = False):
    holidayList = []
    os.chdir(base_dir)
    fileName, afterDate, beforeDate = "", "", ""

    # arguments passed to terminal to execute the dotnet command necessary to capture discord plays
    terminalCommands = ["dotnet",  # invokes dotnet command with the following as arguments
                        dllLocation,  # location of exporter program
                        "export",  # option that specifies we will be exporting a channel
                        "-t", userToken,  # use authorization token of user's account
                        "-c", channelID,  # channel ID of channel to be exported
                        "-o", outputFilePrefix + fileName,  # output file for the exported data
                        "--dateformat", "\"dd-MM-yy hh:mm tt\"",  # date format for the after and before parameters
                        "--after", afterDate,  # Get all channel messages after this date and time
                        "--before", beforeDate]  # Get all channel messages before this date and time

    if playdate != "":
        sdate = date(playdate[0], playdate[1], playdate[2])
    else:
        sdate = date(2020, 6, 16)

    edate = date.today()

    if numberday != "":
        delta = timedelta(days=numberday)
    else:
        delta = edate - sdate

    for i in range(delta.days + 1):
        days = sdate + timedelta(days = i)

        month = days.timetuple()[2]
        day = days.timetuple()[1]
        year = str(days.timetuple()[0])[-2:]

        dateFileName = "{0:02d}-{1:02d}-{2}".format(day, month, year)
        fileName = dateFileName + ".html"

        if days.weekday() > 4:
            print(fileName + " is a weekend, skipping.")
        elif fileName == "07-03-20.html":  # fileName[0:8] in holidayList:
            print(fileName + " is a trading holiday, skipping")
        elif os.path.exists(base_dir + fileName) and override is False:
            print(fileName + " exists.")
        else: # if exists and override is True OR not exists
            print(fileName + " does not exists, creating...")

            if after != "" and before != "" and playdate != "":
                afterDate = dateFileName + " " + after
                beforeDate = dateFileName + " " + before
            else:
                afterDate = dateFileName + " 06:25"
                beforeDate = dateFileName + " 13:05"

            if outputFile != "":
                outputFile = dateFileName + ".html"

            terminalCommands[8] = base_dir + outputFile
            terminalCommands[12] = afterDate
            terminalCommands[14] = beforeDate

            [print(terminalCommands[i]) for i in range(len(terminalCommands))]
            list = " ".join(terminalCommands)
            print(list)
            input("Pause and check arg list elements.")

            subprocess.call(terminalCommands)
            print(fileName + " has been created.")

            print(fileName, "will be passed to html to DB.")
            html_to_DB(fileName, "practice.db")

        # hour = day.timetuple()[3]
        # minute = day.timetuple()[4]
        # seconds = day.timetuple()[5]


def html_to_DB(htmlFile = "", dbName = ""):  # argList is a list of files that need to be parsed and contents added to db of plays
    # Organization of plays in html file
    # IQ 2020-07-17 P $25
    #
    # Bid: $2.94
    # Ask: $2.99
    # Interest: 6
    # Volume: 447
    # IV: 73.12%
    # % Diff: 6.7%
    # Purchase: $23.43
    if dbName == "":
        conn = sqlite3.connect("WhalePlays.db")
    else:
        conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Plays(symbol TEXT, date TEXT, style TEXT, strike REAL,
                                                       bid REAL, ask REAL, interest INTEGER, volume INTEGER,
                                                       iv REAL, diff REAL, price REAL)''')

    argList = []
    os.chdir(base_dir)

    if htmlFile == "":
        [argList.append(i) for i in os.listdir(base_dir) if i.endswith(".html")]
        argList.sort()
    else:
        argList.append(htmlFile)

    # Other methods will be needed to extract data from cvs and json files.
    for inputFile in argList:
        # print("Checking file: [{}]".format(inputFile))
        htmlData = open(str(inputFile), 'r')
        contents = htmlData.read()
        soup = bs.BeautifulSoup(contents, "html.parser")

        # Removes img tag
        for img in soup("img"):
            if isinstance(img, bs.element.Tag):
                img.decompose()

        # For the strike
        strikePlays = soup.find_all("div", {"class": "chatlog__message"})

        for play_iter in range(len(strikePlays)):
            string = []

            for char_iter in range(len(strikePlays[play_iter].text)):
                if strikePlays[play_iter].text != 0:
                    if ord(strikePlays[play_iter].text[char_iter]) < 122:
                        string.append(strikePlays[play_iter].text[char_iter])
            strikeData.append(string)

        for char_iter in range(len(strikeData)):
            while not strikeData[char_iter][0].isalpha():
                del strikeData[char_iter][0]

            strikeData[char_iter] = ''.join(strikeData[char_iter])

        pattern = re.compile(r'''(?P<Symbol>\s*\w{1,5})\s*
                                        (?P<Date>\d{4}-\d{2}-\d{2})\s*
                                        (?P<Style>\w)\s*\$
                                        (?P<Strike>\d{1,5}(\.\d{1,2})?)\s*Bid:\s*\$
                                        (?P<Bid>\d{1,5}(\.\d{1,2})?)\s*Ask:\s*\$
                                        (?P<Ask>\d{1,5}(\.\d{1,2})?)\s*Interest:\s*
                                        (?P<Interest>\d{1,9})\s*Volume:\s*
                                        (?P<Volume>\d{1,9})\s*IV:\s*
                                        (?P<IV>\d{1,4}(\.\d{1,2})?)%\s*%\s*Diff:\s*
                                        (?P<Diff>-?\d{1,4}(\.\d{1,2})?)%\s*(Purchase|Underlying):\s*\$
                                        (?P<Price>\d{1,4}(\.\d{1,2})?.*)''', re.VERBOSE)

        backup_pattern = re.compile(r'''(?P<Symbol>\s*\w{1,5})\s*
                                        (?P<Date>\d{4}-\d{2}-\d{2})\s*
                                        (?P<Style>\w)\s*\$
                                        (?P<Strike>\d{1,5}(\.\d{1,2})?)\s*Bid\-Ask:\s*\$
                                        (?P<Bid>\d{1,5}(\.\d{1,2})?)\s*\-\s*\$
                                        (?P<Ask>\d{1,5}(\.\d{1,2})?)\s*Interest:\s*
                                        (?P<Interest>[0-9,]{1,10})\s*Volume:\s*
                                        (?P<Volume>[0-9,]{1,10})\s*IV:\s*
                                        (?P<IV>\d{1,4}(\.\d{1,2})?)%\s*%\s*Diff:\s*
                                        (?P<Diff>-?\d{1,4}(\.\d{1,2})?)%\s*(Purchase|Underlying):\s*\$
                                        (?P<Price>\d{1,4}(\.\d{1,2})?.*)''', re.VERBOSE)

        for play_iter in range(len(strikeData)):
            details = []
            match = pattern.match(strikeData[play_iter])

            if match is None:
                # print("Match is none, here is the play")
                # print('*' * 20, '\n', strikeData[play_iter], '\n', '*' * 20)
                match = backup_pattern.match(strikeData[play_iter])
                # print("Backup pattern utilized")

                if match is None:
                    print("Backup pattern failed")
                    print('*' * 20, '\n', strikeData[play_iter], '\n', '*' * 20)
                    # input("Confirm: ")

            for group_iter in range(11):
                # print('-' * 78)
                # print(group_iter)
                # print(strikeInfo[group_iter])
                # print(match.group(strikeInfo[group_iter]))
                # print('-' * 78)
                # input("Wait and see.")

                if group_iter <= 2: # The first three are strings and the everything after is numeric.
                    details.append(match.group(strikeInfo[group_iter]))
                else:
                    details.append(float(match.group(strikeInfo[group_iter]).replace(',', '')))

            cursor.execute('''INSERT INTO Plays (symbol, date, style, strike, bid, ask, interest, volume, iv, diff, price)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', details)
            # print("Inserted", i)

        conn.commit()

        print("File analysis complete, {0} records created.".format(len(strikeData)))


strikeData = []
tokens = open("/Users/X/tokens.txt", 'r')
base_dir = "/Users/X/UnusualWhalesHistory/"
userToken = tokens.readline().split("\"")[1]
channelID = tokens.readline().split("\"")[1]
outputFilePrefix = "/Users/X/UnusualWhalesHistory/"
files = os.listdir(outputFilePrefix)
dllLocation = tokens.readline().split("\"")[1]
tokens.close()

strikeInfo = ["Symbol",  # string
              "Date",  # string or int int int
              "Style",  # string
              "Strike",  # int
              "Bid",  # int
              "Ask",  # int
              "Interest",  # int
              "Volume",  # int
              "IV",  # int
              "Diff",  # int
              "Price",  # int
              "ChangePercent",  # int, (price - strike) / price
              "ChangeCost"  # int, (price - strike)
              ]


# getHTML()
# html_to_DB()
# argList = []
## [argList.append(i) for i in os.listdir(base_dir) if i.endswith(".html")]
## argList.sort()
##
## for file in argList:
##     html_to_DB(file)
##
## print("All done!")

# Get plays for one day, start time, end time, number of days to project, save name and True
# getHTML((2020, 7, 1), "06:25", "19:00", 0, "practice.html", True)

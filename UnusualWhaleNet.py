# TODO
# add sector for each play
# add getting plays for the same day and only get plays from previous runtime until now
# add gui window
# add search by field name
# add gui progress bar(s)
# Add date scanned
# add play to bd if doesnt exist
# Add csv and json support along side the existing html parsing

# Emoji Guide
# :rotating_light: - Options expire within the week
# :rocket: - Extra Unusual Movement
# :slot_machine: - Lottos
# :stopwatch: - Intraday play
# :calendar_spiral: - Overnights/Extended play

# https://github.com/Tyrrrz/DiscordChatExporter/wiki/
# Created the discord scraper, DiscordChatExporter

import os
import re
import time
import sqlite3
import hashlib
import shutil
import bs4 as bs
import subprocess
import logging
from datetime import date, timedelta, datetime
import pyperclip


def cleanDuplicatesFromDB(file):
    conn = sqlite3.connect(file)
    cur = conn.cursor()
    fileCopy = file[:file.rfind('.')] + '2' + file[file.rfind('.'):]
    shutil.copy(file, fileCopy)

    if getHash(file) != getHash(fileCopy):
        raise Exception("Plays damaged, abort.")

    cur.execute('''SELECT DISTINCT * FROM Plays''')
    data = cur.fetchall()
    cur.execute('''DELETE FROM Plays''')

    cur.executemany('''INSERT INTO Plays VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

    conn.commit()
    cur.close()
    conn.close()


# Gets either the sah1 or md5 hash to make sure copies are equivalent
def getHash(fileName, whichHash = 'md5'):
    # https: // stackoverflow.com / a / 22058673 / 1902959
    # Heavily borrowed from Randall Hunt's answer over at StackOverflow
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    hashFunction = None
    hashOutput = None

    if whichHash == 'sha1':
        hashFunction = hashlib.sha1()
    else:
        hashFunction = hashlib.md5()

    with open("/Users/X/DB/WhalePlays.db", 'rb') as file:
        while True:
            data = file.read(BUF_SIZE)

            if not data:
                break

            hashFunction.update(data)

    hashOutput = hashFunction.hexdigest

    logging.debug("{0}: {1}".format(whichHash, hashOutput()))

    return hashOutput()


def getHTML(playdate = None, after = None, before = None, numberday = None, outputFile = None, override = False):
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

    if playdate is not None:
        sdate = date(playdate[0], playdate[1], playdate[2])
    else:
        sdate = date(2020, 6, 16)

    edate = date.today()

    if numberday is not None:
        delta = timedelta(days=numberday)
    else:
        delta = edate - sdate

    # starts at s(tart)date and moves delta days forward to get range of dates
    for i in range(delta.days + 1):
        days = sdate + timedelta(days = i)

        month = days.timetuple()[2]
        day = days.timetuple()[1]
        year = str(days.timetuple()[0])[-2:]

        dateFileName = "{0:02d}-{1:02d}-{2}".format(day, month, year)
        fileName = dateFileName + ".html"

        if days.weekday() > 4:
            print(fileName + " is a weekend, skipping.")
        elif fileName[0:8] in holidayList:
            print(fileName + " is a trading holiday, skipping")
        elif os.path.exists(base_dir + fileName) and override is False:
            print(fileName + " exists.")
        elif (os.path.exists(base_dir + fileName) and override is True) or (not os.path.exists(base_dir + fileName)):
            print(fileName + " does not exists, creating...")

            if after is not None and before is not None and playdate is not None:
                afterDate = dateFileName + " " + after
                beforeDate = dateFileName + " " + before
            else:
                afterDate = dateFileName + " 06:25"
                beforeDate = dateFileName + " 13:05"
                # afterDate = "\"" + dateFileName + " 06:25" + "\""
                # beforeDate = "\"" + dateFileName + " 13:05" + "\""

            if outputFile is None:
                outputFile = dateFileName + ".html"

            terminalCommands[8] = base_dir + outputFile
            terminalCommands[12] = afterDate
            terminalCommands[14] = beforeDate

            [print(terminalCommands[i]) for i in range(len(terminalCommands))]

            # if the file should be copied, here it is easy to copy
            commandList = " ".join(terminalCommands)
            pyperclip.copy(commandList)
            print(commandList)
            # input("Pause and check arg list elements...")

            subprocess.call(terminalCommands)
            print('\n' + fileName + " has been created.")

            print(fileName, "will be passed to html to DB.")

            dbName = "/Users/X/DB/WhalePlays.db"
            print("DB name - ", dbName)
            # It is not necessary to call the htmldb function here and can be called from main
            html_to_DB(fileName, dbName)
        else:
            print("The else clause.")

        # When getting play for today if file exists, will need to keep of time last accessed
        # hour = day.timetuple()[3]
        # minute = day.timetuple()[4]
        # seconds = day.timetuple()[5]

# htmlFile is an optional parameter. It is an html file that should have the option plays scraped from its contents
# dbName is an optional parameter. It is the name of the database the plays should be added to. Defaults to "/Users/X/DB/WhalePlays.db"
def html_to_DB(htmlFile = None, dbName = None):  # argList is a list of files that need to be parsed and contents added to db of plays
    # Organization of plays in html file
    #    #  IQ 2020-07-17 P $25
    #    #  
    #    #  Bid: $2.94
    #    #  Ask: $2.99
    #    #  Interest: 6
    #    #  Volume: 447
    #    #  IV: 73.12%
    #    #  % Diff: 6.7%
    #    #  Purchase: $23.43
    logging.debug("DB name: ", dbName)

    if dbName is None:  # If no db is specified, use the default
        conn = sqlite3.connect("/Users/X/DB/WhalePlays.db")
    else:  # Use dbName database
        conn = sqlite3.connect(dbName)
        
    cursor = conn.cursor()
    # Each  field is data that will be obtained for each options play
    cursor.execute('''CREATE TABLE IF NOT EXISTS Plays(symbol TEXT, date TEXT, style TEXT, strike REAL,
                                                       bid REAL, ask REAL, interest INTEGER, volume INTEGER,
                                                       iv REAL, diff REAL, price REAL)''')

    argList = []  # Will hold the files to parse for option plays
    os.chdir(base_dir)

    if htmlFile is None:  # if no file specified for play parsing, all files in play directory will be added
        [argList.append(i) for i in os.listdir(base_dir) if i.endswith(".html")]
        argList.sort()  # To keep them in numerical order
    else:
        argList.append(htmlFile)  # Only add the specified html file

    # Other methods will be needed to extract data from cvs and json files.
    for inputFile in argList:  # Checks every file in arglist
        logging.debug("Checking file: [{}]".format(inputFile))

        # Dates not a weeked or holiday where nothing was uploaded.
        logging.debug("Bad dates: ", badDates)

        # Uses bs4 to grab the data for the html file in question
        htmlData = open(str(inputFile), 'r')
        contents = htmlData.read()
        soup = bs.BeautifulSoup(contents, "html.parser")

        # Removes img tag
        for img in soup("img"):
            if isinstance(img, bs.element.Tag):
                img.decompose()

        # For the strike, this is the class tag where the strike plays are held
        strikePlays = soup.find_all("div", {"class": "chatlog__message"})

        ############################
        # There is other data mixed in with the characters from the file. Emojis and other various text are filtered out here.
        for play_iter in range(len(strikePlays)):
            string = []

            for char_iter in range(len(strikePlays[play_iter].text)):
                if strikePlays[play_iter].text != 0:  # If there is text here, otherwise skip
                    if ord(strikePlays[play_iter].text[char_iter]) < 122:  # If it is a printable character
                        string.append(strikePlays[play_iter].text[char_iter])  # append it to the string
            strikeData.append(string)  # Finalize the changes and add it to the list of cleaned up data

        for char_iter in range(len(strikeData)):  # Delete excess escaped characters in the first indexes of data.
            while not strikeData[char_iter][0].isalpha():
                del strikeData[char_iter][0]

            strikeData[char_iter] = ''.join(strikeData[char_iter])  # Creates a new string with without extra characters, ready to be parsed for data.

        ###############################


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

        # holds the raw data minus img tags and emoji chars
        for play_iter in range(len(strikeData)): # each play is scraped for the play strike, price, date etc.
            details = []  # The data captured will be stored here and then passed to the database
            match = pattern.match(strikeData[play_iter]) # A single play is captured here and the data about it will be parsed through regular expression.

            if match is None: # if the way the data is organized, the pattern will fail
                logging.info("Match is none, here is the play")
                logging.debug('*' * 20, '\n', strikeData[play_iter], '\n', '*' * 20)
                match = backup_pattern.match(strikeData[play_iter])
                logging.info("Backup pattern utilized")

                if match is None: # if the backup pattern fails
                    logging.warning("Backup pattern failed")
                    logging.debug('*' * 20, '\n', strikeData[play_iter], '\n', '*' * 20)
                    logging.debug(input("Confirm: "))

            for group_iter in range(11):
                # When the output and organization of the html changes, a new regex expression is necessary to capture data.
                # This show how the new data is organized so I can create backup patterns.
                logging.debug('-' * 78)
                logging.debug(group_iter)
                logging.debug(strikeInfo[group_iter])
                logging.debug(match.group(strikeInfo[group_iter]))
                logging.debug('-' * 78)
                logging.debug(input("Wait and see."))

                if group_iter <= 2:  # The first three are strings
                    details.append(match.group(strikeInfo[group_iter]))
                else:  # Everything after is numeric.
                    details.append(float(match.group(strikeInfo[group_iter]).replace(',', '')))

            cursor.execute('''INSERT INTO Plays (symbol, date, style, strike, bid, ask, interest, volume, iv, diff, price)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', details)

            logging.debug("Inserted", group_iter)

        conn.commit()
        cursor.close()
        conn.close()

        print("File analysis complete, {0} records created.".format(len(strikeData)))


def main():
    logging.basicConfig(level = logging.DEBUG, format = ' %(asctime)s -  %(levelname)s -  %(message)s')
    # logging.basicConfig(filename = 'unusualLogs.txt',level = logging.DEBUG, format = ' %(asctime)s -  %(levelname)s -  %(message)s')

    getHTML()  # Gets an html file for every for every day that the program runs. Another function is called that creates and fills the database
    cleanDuplicatesFromDB("/Users/X/DB/WhalePlays.db")  # Many duplicates are listed and this function removes them from the database

    print("All done!")

    # Get plays for one day, start time, end time, number of days to project, save name and True
    # getHTML((2020, 7, 1), "06:25", "19:00", 0, "practice.html", True)


strikeData = []  # Will hold the information after data is scraped from html files
tokens = open("/Users/X/tokens.txt", 'r')  # Holds discord user token, channel id and discord scraper dll file
base_dir = "/Users/X/UnusualWhalesHistory/"  # Where the html files will be held after downloading
userToken = tokens.readline().split("\"")[1]
channelID = tokens.readline().split("\"")[1]
dllLocation = tokens.readline().split("\"")[1]
outputFilePrefix = "/Users/X/UnusualWhalesHistory/"  # Same as base_dir, needs to be removed
files = os.listdir(outputFilePrefix)  # Gathers all the html files downloaded by the program
tokens.close()

# Column titles for the SQL database entries
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

holidayList = [] # A list of trading holidays that markets don't trade on
file = open("/Users/X/tradingHolidays.txt", 'r')
[holidayList.append(i[:-1]) for i in file.readlines()]
file.close()

badDates = [] # In case there are days plays are not uploaded, none so far
file = open("/Users/X/badDays.txt", 'r')
[badDates.append(i[:-1]) for i in file.readlines()] # Dates are recorded as 07-17-20, the -1 takes off the null terminator
file.close()

if __name__ == "__main__":
    main()


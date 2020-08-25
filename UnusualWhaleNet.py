# TODO
# add sector for each play
# add getting plays for the same day and only get plays from previous runtime until now
#   This was to avoid duplicates more than save time, is not an issue anymore
# add gui window
# add search by field name
# add gui progress bar(s)
# Add date scanned
# add play to db if doesnt exist
# Add csv and json support along side the existing html parsing
# Multi-threading so db work can be done as the net file is downloading.
# Add command line access
# Fetching the plays individually takes too much time.
# Collect the date range as one file and separate by date in own file with BeautifulSoup Magic.
# Add list of days to be scanned to db
# Add list of days already inputted to db

# Emoji Guide
# :rotating_light: - Options expire within the week 128680
# :rocket: - Extra Unusual Movement 128640
# :slot_machine: - Lottos
# :stopwatch: - Intraday play
# :calendar_spiral: - Overnights/Extended play 128467

# https://github.com/Tyrrrz/DiscordChatExporter/wiki/
# Created the discord scraper, DiscordChatExporter

import os  # For navigating the file system
import re  # Parsing for selective text
import time  # Used to measure complete run time of program
import json  # Necessary for parsing json objects
import shutil  # Copying files
import sqlite3  # Managing database storage
import hashlib  # Retrieving and comparing hashes
import logging  # For selectively writing program information to the console
import subprocess  # Used to issues terminal commands
from datetime import date, timedelta  # Very useful in calculations involving dates


def errorLog():
    """
    Plays that aren't captured by the current regex patterns are logged. A new backup pattern will be added to capture it.
    """

    if not os.path.exists("/config/designChangeLog.txt"):
        open("/config/designChangeLog.txt", 'x').close()  # Creates if it doesn't exist,

    else:
        textList = []
        with open("/config/designChangeLog.txt", 'r') as designChangeLog:
            allText = designChangeLog.read()

            if allText == '':
                print("No errors reported.")
            else:
                allText = allText.split("#####")
                for erroriter in range(len(allText)):
                    textList.append(allText[erroriter])

                [print(textList[listiter] + '\n') for listiter in range(len(textList))]


def prepareFiles():
    """
    This function prepares the files and folders necessary for the program to run
    BASE_DIR parameter is the directory where the mandatory files will be placed
    """

    # Make sure the necessary directories are in place
    toCreate = [BASE_DIR, CONFIG_DIR, FILE_DIR]
    for i in range(len(toCreate)):
        if not os.path.exists(toCreate[i]):
            os.mkdir(toCreate[i])
            logging.info(toCreate[i] + "has been created.")
        else:
            logging.info(toCreate[i] + " already exists.")

    os.chdir(BASE_DIR)

    if not os.path.exists("config/badDays.txt"):
        open("config/badDays.txt", 'x').close()

    # The file that holds the user's Discords token, channel id and dll location.
    # The Unusual Whales channel ID is already filled as can be seen
    if not os.path.exists("config/tokens.txt"):
        with open("config/tokens.txt", 'w') as file:
            file.write("userToken = \"\"\nchannelID = \"721759406089306223\"\ndllLocation = \"\"\n")

    # A list of holidays during which markets don't trade
    if not os.path.exists("config/tradingHolidays.txt"):
        with open("config/tradingHolidays.txt", 'w') as file:
            file.write("01-01-20\n01-20-20\n02-17-20\n04-10-20\n05-25-20\n07-03-20\n09-07-20\n11-26-20\n12-25-20\n\n" +
                       "01-01-21\n01-18-21\n02-15-21\n04-02-21\n05-31-21\n07-05-21\n09-06-21\n11-25-21\n12-24-21\n\n" +
                       "01-01-22\n01-17-22\n02-21-22\n04-15-22\n05-30-22\n07-04-22\n09-05-22\n11-24-22\n12-26-22\n\n")


def cleanDuplicatesFromDB(file):
    """
    Used to filter out duplicate plays from daabase file
    """

    if not os.path.exists(CONFIG_DIR + file):
        file = DEFAULT_DB

    conn = sqlite3.connect(CONFIG_DIR + file)
    cur = conn.cursor()
    fileCopy = file[:file.rfind('.')] + '2' + file[file.rfind('.'):]  # Takes the filename and makes another filename with a '2' before the '.' - A.html & A2.html
    shutil.copy(CONFIG_DIR + file, CONFIG_DIR + fileCopy)  # Creates the copy

    if getHash(file) != getHash(fileCopy):  # Makes sure that the two file are the same
        os.unlink(CONFIG_DIR + fileCopy)
        raise Exception("Plays damaged, abort.")
    else:
        os.unlink(CONFIG_DIR + fileCopy)

    cur.execute('''SELECT DISTINCT * FROM Plays''')  # Selects entries that are not duplicates
    data = cur.fetchall()
    cur.execute('''DELETE FROM Plays''')

    # Instead of using a for loop, you can use execute many with the variable that holds the data
    cur.executemany('''INSERT INTO Plays VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

    conn.commit()
    cur.close()
    conn.close()


def getHash(fileName, whichHash = 'md5'):
    """
    Gets either the sha1 or md5 hash, used to make sure database copies are not corrupted
    """

    # https: // stackoverflow.com / a / 22058673 / 1902959
    # Heavily borrowed from Randall Hunt's answer over at StackOverflow
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    if not os.path.exists(CONFIG_DIR + fileName):
        logging.critical("Files hashes not equal.")

        raise FileNotFoundError

    if whichHash == 'sha1':
        hashFunction = hashlib.sha1()
    else:
        hashFunction = hashlib.md5()

    with open(CONFIG_DIR + fileName, 'rb') as file:
        while True:
            data = file.read(BUF_SIZE)

            if not data:
                break

            hashFunction.update(data)

    hashOutput = hashFunction.hexdigest
    logging.debug("{0}: {1}".format(whichHash, hashOutput()))

    return hashOutput()


def downloadPlays(end = None, startDate = None, after = None, before = None, override = False):
    """
    Using the DiscordChatExporter, the discord chat messages are exported to an html
    There is an html file for each date and the data for only the plays is extracted
    FileType is a required argument for the output file type: HtmlDark, HtmlLight, PlainText Json or Csv
    End is an optional parameter specifying the number of days to capture data for
    StartDate is an optional parameter which is the date to begin at, will default to 06-16-20, the first day the plays are available
    After is an optional parameter specifying that all plays after that time will be captured
    Before is an optional parameter specifying that all plays before that time will be captured
    Override is an optional parameter, used to specify if the dates should be downloaded if it already exists
    """

    with open("config/tokens.txt", 'r') as tokens:
        userToken = tokens.readline().split("\"")[1]
        channelID = tokens.readline().split("\"")[1]
        dllLocation = tokens.readline().split("\"")[1]

    # Exit if any of these fields are blank, exit. All three are necessary for the program to work
    if userToken == '' or dllLocation == '' or channelID == '':
        print("Please insert the below items in the \"UnusualWhales/config/tokens.txt\" and restart program:\n" +
              "\tDiscord user token\n\tThe location of the DiscordChatExporter.Cli.dll file")
        exit(1)

    ######################################

    holidayList = []
    with open("config/tradingHolidays.txt", 'r') as holidays:
        [holidayList.append(i[:-1]) for i in holidays.readlines()]  # Dates are recorded as 07-17-20, the [:-1] takes off the null terminator

    badDates = []  # Dates where nothing was uploaded but should have due to error etc.. None so far
    with open("config/badDays.txt", 'r') as file:
        [badDates.append(i[:-1]) for i in file.readlines()]  # Dates are recorded as 07-17-20, the -1 takes off the null terminator

    ######################################

    if startDate is None:
        sdate = date(2020, 6, 16)  # Start is 06/16/2020, first date plays were generated by Unusual Whales
    else:
        sdate = date(startDate[0], startDate[1], startDate[2])  # Year, month and date

    if type(end) == date:
        edate = date(end[0], end[1], end[2])
    elif type(end) is int:
        edate = sdate + timedelta(days = end)
    else:  # If it is a new day and before the market opens, don't include the current day
        if date.today().timetuple()[3] <= 6 and date.today().timetuple()[4] < 30:
            edate = date.today() - timedelta(days = 1)
        else:
            edate = date.today()

    delta = edate - sdate

    ######################################

    # starts at s(tart)date and moves delta days forward to get range of dates
    for i in range(delta.days + 1):
        os.chdir(FILE_DIR)
        days = sdate + timedelta(days = i)
        month = days.timetuple()[2]  # Time tuple returns a tuple of year, day month
        day = days.timetuple()[1]
        year = str(days.timetuple()[0])[-2:]
        dateFileName = "{0:02d}-{1:02d}-{2}".format(day, month, year)  # Month and date are formatted to two decimal places
        fileName = dateFileName + '.' + "json"

        if days.weekday() > 4:
            print(fileName + " is a weekend, skipping.\n")
        elif fileName[0:8] in holidayList:
            print(fileName + " is a trading holiday, skipping.\n")
        elif os.path.exists(FILE_DIR + fileName) and override is False:
            print(fileName + " exists.\n")
        # If the file exists and the override is set to True OR the file doesnt exists, download the files
        elif (os.path.exists(FILE_DIR + fileName) and override is True) or (not os.path.exists(BASE_DIR + '/' + fileName)):
            if override:
                print(fileName + " exists but override is signaled, creating...")
            else:
                print(fileName + " does not exists, creating...")

            # If playdate, after and before are all passed in as parameters
            if after is not None and before is not None and startDate is not None:
                afterDate = dateFileName + " " + after
                beforeDate = dateFileName + " " + before
            else:
                afterDate = dateFileName + " 06:25"  # 6:25 in case plays start a bit earlier, just in case preparation
                beforeDate = dateFileName + " 13:05"  # 1:05 in case plays start a bit late or get delayed, just in case preparation

            logging.debug("Output: " + fileName)

            # arguments passed to terminal to execute the dotnet command necessary to capture discord plays
            terminalCommands = ["dotnet",  # invokes dotnet command with the following as arguments
                                dllLocation,  # location of exporter program
                                "export",  # option  that specifies we will be exporting a channel
                                "-t", userToken,  # use authorization token of user's account
                                "-c", channelID,  # channel ID of channel to be exported
                                "-o", FILE_DIR + fileName,  # output file for the exported data
                                "--dateformat", "\"dd-MM-yy hh:mm\"",  # date format for the after and before parameters
                                "--after", afterDate,  # Get all channel messages after this date and time
                                "--before", beforeDate,  # Get all channel messages before this date and time
                                "-f", "json"]  # HtmlDark, HtmlLight, PlainText Json or Csv

            # [print(terminalCommands[arg]) for arg in range(len(terminalCommands))]

            # input("Verify: ")

            subprocess.call(terminalCommands)

            if not CONFIG_DIR + fileName:
                print("File not created.")
                logging.error("File not created.")

                raise FileNotFoundError
        else:
            logging.info("The weekday, holiday else clause.")


def file_to_DB(sourceFile = None, dbName = None):
    """
    Dates is an optional parameter representing a list of dates to be passed to the db creator
    SourceFile is an optional parameter. It is an html file that should have the option plays scraped from its contents
    DbName is an optional parameter. It is the name of the database the plays should be added to. Defaults to "/Users/X/DB/WhalePlays.db"
    """

    argList = []  # Will hold the files to parse for option plays
    os.chdir(FILE_DIR)

    if sourceFile is None:  # if no file specified for play parsing, all files in play directory will be added
        [argList.append(fileiter) for fileiter in os.listdir() if fileiter.endswith("json")]
        argList.sort()  # To keep them in numerical order
    else:
        argList.append(sourceFile)  # Only add the specified html file

    if dbName is None:  # If no db is specified, use the default
        conn = sqlite3.connect(CONFIG_DIR + DEFAULT_DB)
    else:  # Use dbName database
        conn = sqlite3.connect(CONFIG_DIR + dbName)

    cursor = conn.cursor()
    # Each field is data that will be obtained for each options play
    cursor.execute('''CREATE TABLE IF NOT EXISTS Plays(symbol TEXT, date TEXT, style TEXT, strike REAL,
                                                       bid REAL, ask REAL, interest INTEGER, volume INTEGER,
                                                       iv REAL, diff REAL, price REAL, createdDate TEXT, createdTime TEXT)''')

    # The pattern used by  majority of the html files
    # Expiration date, Call/Put, Strike, Bid, Ask, Interest, Volume IV, and Underlying are gathered by the below patterns
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

    # The newer files use a different pattern
    backup_pattern = re.compile(r'''(?P<Symbol>\s*\$?\w{1,5})\s*
                                    (?P<Date>\d{4}-\d{2}-\d{2})\s*
                                    (?P<Style>\w)\s*\$
                                    (?P<Strike>\d{1,5}(\.\d{1,2})?)\s*Bid-Ask:\s*\$
                                    (?P<Bid>\d{1,5}(\.\d{1,2})?)\s*-\s*\$
                                    (?P<Ask>\d{1,5}(\.\d{1,2})?)\s*Interest:\s*
                                    (?P<Interest>[0-9,]{1,10})\s*Volume:\s*
                                    (?P<Volume>[0-9,]{1,10})\s*IV:\s*
                                    (?P<IV>\d{1,4}(\.\d{1,2})?)%\s*%\s*Diff:\s*
                                    (?P<Diff>-?\d{1,4}(\.\d{1,2})?)%\s*(Purchase|Underlying):\s*\$
                                    (?P<Price>\d{1,4}(\.\d{1,2})?.*)''', re.VERBOSE)

    backup__pattern = re.compile(r'''(?P<Symbol>\w{1,5})]\([a-zA-Z/\\%-:.]{65,70}\)\s*
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

    backup___pattern = re.compile(r'''''', re.VERBOSE)

    # Other methods will be needed to extract data from cvs and json files
    for inputFile in argList:  # Checks every file in arglist
        logging.info("Checking file: [{0}]".format(inputFile))
        strikeData = []  # Will hold the information after data is scraped from html files
        strikePlays = []

        # logging.info("USING JSON FILES")

        with open(inputFile, 'r') as jsonfile:
            parsejson = json.loads(jsonfile.read())

        for i in range(len(parsejson["messages"])):
            data = parsejson["messages"][i]["content"]

            if data != '':
                strikePlays.append(parsejson["messages"][i]["content"])
            else:
                strikePlays.append(parsejson["messages"][i]["embeds"][0]["title"] + parsejson["messages"][i]["embeds"][0]["description"])
                # print("Parse addition: ", strikePlays[-1])

        for i in range(len(strikePlays)):
            string = []

            for j in range(len(strikePlays[i])):
                if ord(strikePlays[i][j]) < 122:  # If it is a printable character
                    string.append(strikePlays[i][j])  # append it to the string
            strikeData.append(string)  # Finalize the changes and add it to the list of cleaned up data

        for k in range(len(strikeData)):  # Delete excess escaped characters located in the front of the string
            while not strikeData[k][0].isalpha():  # Stops deleting characters when the unnecessary characters are gone.
                del strikeData[k][0]
            strikeData[k] = ''.join(strikeData[k])  # sd[k] is a list of strings, this turns said list into one string

        for i in range(len(strikeData)):  # each play is scraped for the play strike, price, date etc
            details = []  # The data captured will be stored here and then passed to the database
            # logging.debug('*' * 20 + str(i) + '*' * 20)
            match = pattern.match(strikeData[i])  # A single play is captured here and the data about it will be parsed through regular expression

            # logging.debug("FIRST MATCH")

            if match is None:  # if the way the data is organized in the html file changes, the pattern will fail
                match = backup_pattern.match(strikeData[i])  # Backup pattern is used
                # logging.debug("SECOND MATCH")

                if match is None:
                    match = backup__pattern.match(strikeData[i])
                    # logging.debug("THIRD MATCH")

                    if match is None:  # if the backup pattern fails
                        # input("Stop here and proceed with caution, match is None.")

                        # When the output and organization of the file changes, a new regex expression is necessary to capture data
                        # This show how the new data is organized so I can create backup patterns
                        logging.error("Backup pattern failed, new pattern necessary")
                        logging.error('*' * 20 + '\n' + strikeData[i] + '\n' + '*' * 20)

                        with open(CONFIG_DIR + "designChangeLog.txt", 'a+') as designChangeLog:
                            designChangeLog.write(strikeData[i] + "#####")

            for group_iter in range(11):
                if group_iter <= 2:  # The first three are strings
                    details.append(match.group(STRIKEINFO[group_iter]))
                else:  # Everything after is numeric
                    details.append(float(match.group(STRIKEINFO[group_iter]).replace(',', '')))

            # Append the date and time created
            details.append(parsejson["messages"][i]["timestamp"][:10])
            details.append(parsejson["messages"][i]["timestamp"][11:19])

            logging.info(details)

            cursor.execute('''INSERT INTO Plays (symbol, date, style, strike, bid, ask, interest, volume, iv, diff, price, createdDate, createdTime)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', details)
            conn.commit()

        print("File analysis complete, {0} records inserted into database.{1}".format(len(strikeData), "\n\t" + '*' * 25))

    cursor.close()
    conn.close()


def main():
    # Logging displays select info to the console
    # Debug, info, warning, error, critical is the order of levels
    logging.basicConfig(level = logging.DEBUG, format = "%(levelname)s -  %(message)s")
    logging.disable(logging.WARNING)  # Only show warning and higher, disables levels below warning

    print("Plays will be collected and added to the database.\nData is being gathered, wait for it to finish....")
    prepareFiles()
    downloadPlays()
    file_to_DB()
    cleanDuplicatesFromDB(DEFAULT_DB)


# GLOBAL DATA
BASE_DIR = os.getcwd() + "/UnusualWhales"  # Where the files for this program will be stored
CONFIG_DIR = BASE_DIR + "/config/"
FILE_DIR = BASE_DIR + "/historyByDate/"
DEFAULT_DB = "WhalePlays.db"
# The below list contains the column titles for the SQL database entries
STRIKEINFO = ["Symbol",  # string
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
              "ChangeCost"]  # int, (price - strike)
                # createdDate is added on in file_to_DB function
                # createdTime is added on in file_to_DB function

if __name__ == "__main__":
    start = time.time()  # Used to measure run time of the program
    main()
    print("All done!\nTotal runtime: {0:02} seconds.".format(time.time() - start))

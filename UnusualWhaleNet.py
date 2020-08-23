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

# Emoji Guide
# :rotating_light: - Options expire within the week
# :rocket: - Extra Unusual Movement
# :slot_machine: - Lottos
# :stopwatch: - Intraday play
# :calendar_spiral: - Overnights/Extended play

# https://github.com/Tyrrrz/DiscordChatExporter/wiki/
# Created the discord scraper, DiscordChatExporter

import os  # For navigating the file system
import re  # Parsing for selective text
import sqlite3  # Managing database storage
import hashlib  # Retrieving and comparing hashes
import shutil  # Copying files
import time
import bs4 as bs  # Navigating and gathering data from html files
import subprocess  # Used to issues terminal commands
import logging  # For selectively writing program information to the console
from datetime import date, timedelta  # Very useful in calculations involving dates
# import pyperclip  # Copies the terminal comm


# For some reason, the Unusual Whales program does not filter out duplicates, this function removes duplicates from database
def cleanDuplicatesFromDB(file):
    if not os.path.exists(config_dir + file):
        file = defaultDB

    conn = sqlite3.connect(config_dir + file)
    cur = conn.cursor()
    fileCopy = file[:file.rfind('.')] + '2' + file[file.rfind('.'):]  # Takes the filename and makes another filename with a '2' before the '.' - A.html & A2.html
    shutil.copy(config_dir + file, config_dir + fileCopy)  # Creates the copy

    if getHash(file) != getHash(fileCopy):  # Makes sure that the two file are the same
        os.unlink(config_dir + fileCopy)
        raise Exception("Plays damaged, abort.")
    else:
        os.unlink(config_dir + fileCopy)

    cur.execute('''SELECT DISTINCT * FROM Plays''')  # Selects entries that are not duplicates
    data = cur.fetchall()
    cur.execute('''DELETE FROM Plays''')

    # Instead of using a for loop, you can use execute many with the variable that holds the data
    cur.executemany('''INSERT INTO Plays VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

    conn.commit()
    cur.close()
    conn.close()


# Gets either the sha1 or md5 hash, used to make sure database copies are not corrupted
def getHash(fileName, whichHash = 'md5'):
    # https: // stackoverflow.com / a / 22058673 / 1902959
    # Heavily borrowed from Randall Hunt's answer over at StackOverflow
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    logging.critical("Hash file: ", fileName)
    if not os.path.exists(config_dir + fileName):
        raise FileNotFoundError

    if whichHash == 'sha1':
        hashFunction = hashlib.sha1()
    else:
        hashFunction = hashlib.md5()

    with open(config_dir + fileName, 'rb') as file:
        while True:
            data = file.read(BUF_SIZE)

            if not data:
                break

            hashFunction.update(data)

    hashOutput = hashFunction.hexdigest
    logging.debug("{0}: {1}".format(whichHash, hashOutput()))

    return hashOutput()


# Using the DiscordChatExporter, the discord char messages are exported to an html
# There is an html file for each date and the data for only the plays is extracted
# FileType is a required argument for the output file type: HtmlDark, HtmlLight, PlainText Json or Csv
# StartDate is an optional parameter which is the date to begin at, will default to 06-16-20, the first day the plays are available
# After is an optional parameter specifying that all plays after that time will be captured
# Before is an optional parameter specifying that all plays before that time will be captured
# End is an optional parameter specifying the number of days to capture data for
# Override is an optional parameter, used to specify if the dates should be downloaded if it already exists
def downloadPlays(fileType, end = None, startDate = None, after = None, before = None, override = False):
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
        os.chdir(file_dir)
        days = sdate + timedelta(days = i)

        month = days.timetuple()[2]  # Time tuple returns a tuple of year, day month
        day = days.timetuple()[1]
        year = str(days.timetuple()[0])[-2:]

        dateFileName = "{0:02d}-{1:02d}-{2}".format(day, month, year)  # The month and date are formatted in two decimal places
        fileName = dateFileName + returnFileType(fileType)

        if days.weekday() > 4:
            logging.info(fileName + " is a weekend, skipping.")
        elif fileName[0:8] in holidayList:
            logging.info(fileName + " is a trading holiday, skipping")
        elif os.path.exists(file_dir + fileName) and override is False:
            logging.info(fileName + " exists.")
        # If the file exists and the override is set to True OR the file doesnt exists, download the files
        elif (os.path.exists(file_dir + fileName) and override is True) or (not os.path.exists(base_dir + fileName)):

            if override:
                logging.info(fileName + " exists but override is signaled, creating...")
            else:
                logging.info(fileName + " does not exists, creating...")

            # If playdate, after and before are all passed in as parameters
            if after is not None and before is not None and startDate is not None:
                afterDate = dateFileName + " " + after
                beforeDate = dateFileName + " " + before
            else:
                afterDate = dateFileName + " 06:25"  # 6:25 in case plays start a bit earlier, just in case preparation
                beforeDate = dateFileName + " 13:05"  # 1:05 in case plays start a bit late or get delayed, just in case preparation

            # outputFile = fileName
            logging.debug("Output: ", fileName)

            # arguments passed to terminal to execute the dotnet command necessary to capture discord plays
            terminalCommands = ["dotnet",  # invokes dotnet command with the following as arguments
                                dllLocation,  # location of exporter program
                                "export",  # option  that specifies we will be exporting a channel
                                "-t", userToken,  # use authorization token of user's account
                                "-c", channelID,  # channel ID of channel to be exported
                                "-o", file_dir + fileName,  # output file for the exported data
                                "--dateformat", "\"dd-MM-yy hh:mm tt\"",  # date format for the after and before parameters
                                "--after", afterDate,  # Get all channel messages after this date and time
                                "--before", beforeDate,  # Get all channel messages before this date and time
                                "-f", fileType]  # HtmlDark, HtmlLight, PlainText Json or Csv
            # terminalCommands[8] = file_dir + fileName
            # terminalCommands[12] = afterDate
            # terminalCommands[14] = beforeDate

            [logging.debug(terminalCommands[arg]) for arg in range(len(terminalCommands))]

            subprocess.call(terminalCommands)

            if not config_dir + fileName:
                print("File not created.")
                logging.error("File not created.")
                raise FileNotFoundError

            logging.info(fileName + " has been created and will be passed to html to DB.")

        else:
            logging.info("The weekday, holiday else clause.")


# FileType is a parameter that specifies the return type of the plays file
def returnFileType(fileType):
    if fileType == "HtmlDark":
        return ".html"
    elif fileType == "HtmlLight":
        return ".html"
    elif fileType == "Json":
        return ".json"
    elif fileType == "PlainText":
        return ".txt"
    elif fileType == "Csv":
        return ".csv"


# htmlFile is an optional parameter. It is an html file that should have the option plays scraped from its contents
# dbName is an optional parameter. It is the name of the database the plays should be added to. Defaults to "/Users/X/DB/WhalePlays.db"
def html_to_DB(fileType, htmlFile = None, dbName = None):  # argList is a list of files that need to be parsed and contents added to db of plays
    strikeData = []  # Will hold the information after data is scraped from html files

    if dbName is None:  # If no db is specified, use the default
        conn = sqlite3.connect(config_dir + defaultDB)
    else:  # Use dbName database
        conn = sqlite3.connect(config_dir + dbName)

    logging.debug("DB name: ", config_dir + dbName)

    cursor = conn.cursor()
    # Each field is data that will be obtained for each options play
    cursor.execute('''CREATE TABLE IF NOT EXISTS Plays(symbol TEXT, date TEXT, style TEXT, strike REAL,
                                                       bid REAL, ask REAL, interest INTEGER, volume INTEGER,
                                                       iv REAL, diff REAL, price REAL)''')

    argList = []  # Will hold the files to parse for option plays
    os.chdir(file_dir)

    if htmlFile is None:  # if no file specified for play parsing, all files in play directory will be added
        [argList.append(fileiter) for fileiter in os.listdir() if fileiter.endswith(".html")]
        argList.sort()  # To keep them in numerical order
    else:
        argList.append(htmlFile)  # Only add the specified html file

    # Other methods will be needed to extract data from cvs and json files
    for inputFile in argList:  # Checks every file in arglist
        logging.info("Checking file: [{0}]".format(inputFile))

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
        # There is other data mixed in with the characters from the file. Emojis and other various text are filtered out here
        for play_iter in range(len(strikePlays)):
            string = []

            for char_iter in range(len(strikePlays[play_iter].text)):
                if strikePlays[play_iter].text != 0:  # If there is text here, otherwise skip
                    if ord(strikePlays[play_iter].text[char_iter]) < 122:  # If it is a printable character
                        string.append(strikePlays[play_iter].text[char_iter])  # append it to the string
            strikeData.append(string)  # Finalize the changes and add it to the list of cleaned up data

        for char_iter in range(len(strikeData)):  # Delete excess escaped characters located in the front of the string
            while not strikeData[char_iter][0].isalpha():
                del strikeData[char_iter][0]

            strikeData[char_iter] = ''.join(strikeData[char_iter])  # Creates a new string with without extra characters, ready to be parsed for data
        ###############################

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
        backup_pattern = re.compile(r'''(?P<Symbol>\s*\w{1,5})\s*
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
        # conn = sqlite3.connect()
        # cursor = conn.cursor()
        # holds the raw data minus img tags and emoji chars
        for play_iter in range(len(strikeData)):  # each play is scraped for the play strike, price, date etc
            details = []  # The data captured will be stored here and then passed to the database
            match = pattern.match(strikeData[play_iter])  # A single play is captured here and the data about it will be parsed through regular expression

            if match is None:  # if the way the data is organized in the html file changes, the pattern will fail
                cursor = conn.cursor()
                match = backup_pattern.match(strikeData[play_iter])  # Backup pattern is used
                logging.info("Backup pattern #1 utilized")

                if match is None:  # if the backup pattern fails
                    logging.error("Backup pattern failed, new pattern necessary")
                    logging.error('*' * 20, '\n', strikeData[play_iter], '\n', '*' * 20)

                    with open(base_dir + "config/designChangeLog.txt", 'a+') as designChangeLog:
                        designChangeLog.write(strikeData[play_iter] + "#####")

            for group_iter in range(11):
                # When the output and organization of the html changes, a new regex expression is necessary to capture data
                # This show how the new data is organized so I can create backup patterns
                logging.debug('-' * 78)
                logging.debug(group_iter)
                logging.debug(strikeInfo[group_iter])
                logging.debug(match.group(strikeInfo[group_iter]))
                logging.debug('-' * 78)

                if group_iter <= 2:  # The first three are strings
                    details.append(match.group(strikeInfo[group_iter]))
                else:  # Everything after is numeric
                    details.append(float(match.group(strikeInfo[group_iter]).replace(',', '')))

            cursor.execute('''INSERT INTO Plays (symbol, date, style, strike, bid, ask, interest, volume, iv, diff, price)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', details)

            logging.debug("Inserted", play_iter)

        conn.commit()

        print("File analysis complete, {0} records inserted into database.{1}".format(len(strikeData), "\n\t" + '*' * 25))

    cursor.close()
    conn.close()


# If a play is not able to be captured by the regex or the backup regex, the text is stored in this file so a new pattern can be derived.
def errorLog():
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


# This function prepares the files and folders necessary for the program to run
# Base_dir parameter is the directory where the mandatory files will be placed
def prepareFiles():
    # Make sure the necessary directories are in place
    toCreate = [base_dir, config_dir, file_dir]
    for i in range(len(toCreate)):
        if not os.path.exists(toCreate[i]):
            os.mkdir(toCreate[i])
            logging.info(toCreate[i] + "has been created.")
        else:
            logging.info(toCreate[i] + " already exists.")

    os.chdir(base_dir)

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


def main():
    # I want to know how long a full run of the program takes
    start = time.time()

    # Setting up the log to display information about the program as it runs
    # debug, info, warning, error, critical is the order of levels
    logging.basicConfig(level = logging.DEBUG, format = "%(levelname)s -  %(message)s")
    # logging.disable(logging.WARNING)  # Only show warning and higher, disables levels below warning
    # files = os.listdir(file_dir)  # Gathers all the html files downloaded by the program

    print("Plays will be collected and added to the database.\nData is being gathered, wait for it to finish....")
    prepareFiles()
    downloadPlays("Json", 1)
    # html_to_DB()
    # cleanDuplicatesFromDB(defaultDB)
    print("All done!\nTotal runtime: {0:02} seconds.".format(time.time() - start))


# GLOBAL DATA
base_dir = os.getcwd() + "/UnusualWhales/"  # Where the files for this program will be stored
config_dir = base_dir + "/config/"
file_dir = base_dir + "/historyByDateX/"
defaultDB = "WhalePlays.db"
# The above list are the column titles for the SQL database entries
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
              "ChangeCost"]  # int, (price - strike)

if __name__ == "__main__":
    main()

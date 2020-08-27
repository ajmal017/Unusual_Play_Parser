# TODO
# add sector for each play
# add gui window
# add search by field name
# add gui progress bar(s)
# Add command line access
# Fetching the plays individually takes extra much time.
#   Scan in whole chat history and separate by date


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
from colorama import Style, Fore, init, deinit  # For turning the terminal text different colors


def error_log():
    """
    Plays that aren't captured by the current regex patterns are logged to be studied. Helps in making new regexes.

    Function has no parameters except the global ones

    Has no return value
    """

    if not os.path.exists(CONFIG_DIR + "designChangeLog.txt"):
        open(CONFIG_DIR + "designChangeLog.txt", 'x').close()  # Creates if it doesn't exist,

    else:
        textList = []
        with open(CONFIG_DIR + "designChangeLog.txt", 'r') as designChangeLog:
            allText = designChangeLog.read()

            if allText == '':
                logging.info("No errors reported, no new patterns necessary.")
            else:
                allText = allText.split("#####")
                for erroriter in range(len(allText)):
                    textList.append(allText[erroriter])

                [print(textList[listiter] + '\n') for listiter in range(len(textList))]


def prepare_files():
    """
    This function prepares the files and folders necessary for the program to run

    Function has no parameters except the global ones

    Has no return value
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

    if not os.path.exists(CONFIG_DIR + "database.txt"):
        open(CONFIG_DIR + "database.txt", 'x').close()

    if not os.path.exists(CONFIG_DIR + "badDays.txt"):
        open(CONFIG_DIR + "badDays.txt", 'x').close()

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

    # If removing duplicates from dates list
    # old_list = lambda old_list: list(set(numbers))


def remove_extras_from_db(file):
    """
    Used to filter out duplicate plays from database file

    File parameter is the name of the file to remove duplicates from

    Has no return value
    """

    if not os.path.exists(CONFIG_DIR + file):
        file = DEFAULT_DB

    conn = sqlite3.connect(CONFIG_DIR + file)
    cur = conn.cursor()
    fileCopy = file[:file.rfind('.')] + '2' + file[file.rfind('.'):]  # Takes the filename and makes another filename with a '2' before the '.' - A.html & A2.html
    shutil.copy(CONFIG_DIR + file, CONFIG_DIR + fileCopy)  # Creates the copy

    if get_hash(file) != get_hash(fileCopy):  # Makes sure that the two file are the same
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


def date_in_db(dateFile):
    """
    Checks if the file represented by the parameter has already been added to the database

    DataFile parameter is the date that is added to a list of dates which have been added to the database

    Returns True if passed in file is in the list of dates already in the database, false if not added to database
    """

    with open(CONFIG_DIR + "database.txt", 'r') as file:
        argList = []
        [argList.append(i[:-1]) for i in file.readlines()]
        argList.sort()

        if dateFile in argList:
            return True
        else:
            return False


def get_hash(fileName, whichHash = 'md5'):
    """
    Gets either the sha1 or md5 hash, used to make sure database copies are not corrupted

    FileName parameter is a string of the file that will be checked for hash
    WhichHash parameter specifies which hash style to use

    Returns the hash value of the file
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


def file_to_db(sourceFile = None, dbName = None):
    """
    Takes a file and extracts the option play data adding it to the database of all plays

    Dates is an optional parameter representing a list of dates to be passed to the db creator
    SourceFile is an optional parameter. It is an html file that should have the option plays scraped from its contents
    DbName is an optional parameter. It is the name of the database the plays should be added to. Defaults to "/Users/X/DB/WhalePlays.db"

    Has no return value
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

    ######################################

    for inputFile in argList:  # Checks every file in arglist
        if not date_in_db(inputFile[:8], ""):
            logging.info("Checking file: [{0}]".format(inputFile))
            strikeData = []  # Will hold the information after data is scraped from html files
            strikePlays = []  # Will hold the data as received from the files, before cleaning up text

            # logging.info("USING JSON FILES")

            with open(inputFile, 'r') as jsonfile:
                parsejson = json.loads(jsonfile.read())

            for i in range(len(parsejson["messages"])):
                data = parsejson["messages"][i]["content"]

                if data != '':
                    strikePlays.append(parsejson["messages"][i]["content"])
                else:
                    strikePlays.append(parsejson["messages"][i]["embeds"][0]["title"] + parsejson["messages"][i]["embeds"][0]["description"])

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

            ######################################

            for i in range(len(strikeData)):  # each play is scraped for the play strike, price, date etc
                details = []  # The data captured will be stored here and then passed to the database
                match = pattern.match(strikeData[i])  # A single play is captured here and the data about it will be parsed through regular expression
                logging.debug("FIRST MATCH")

                if match is None:  # if the way the data is organized in the html file changes, the pattern will fail
                    match = backup_pattern.match(strikeData[i])  # Backup pattern is used
                    logging.debug("SECOND MATCH")

                    if match is None:
                        match = backup__pattern.match(strikeData[i])
                        logging.debug("THIRD MATCH")

                        if match is None:  # if the backup pattern fails
                            logging.debug(input("Stop here and proceed with caution, match is None."))

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

                ######################################

                # Append the date and time created
                details.append(parsejson["messages"][i]["timestamp"][:10])
                details.append(parsejson["messages"][i]["timestamp"][11:19])
                logging.info(details)
                cursor.execute('''INSERT INTO Plays (symbol, date, style, strike, bid, ask, interest, volume, iv, diff, price, createdDate, createdTime)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', details)
                conn.commit()

            print("File analysis complete, {0} records inserted into database.{1}".format(len(strikeData), "\n\t" + '*' * 25))

            with open(CONFIG_DIR + "database.txt", 'a+') as file:
                file.write(inputFile[:8] + '\n')
        else:
            logging.info(inputFile + " already in database.")

    cursor.close()
    conn.close()


def download_date(fileName, days = None, override = False):
    """
    Every day has a file which contains all the Unusual Whale plays issued on that day

    FileName is a parameter that is used to determine if the date it represents needs to be downloaded
    Days is a parameter used to determine if the day passed in is a weekday or not
    Override parameter is used to flag a file that exists but should be downloaded again

    Returns True if the file for the passed in date needs to be downloaded, otherwise false if no download specified or needed
    """

    if days is not None and days.weekday() > 4:
        logging.info(fileName + " is a weekend, skipping.\n")
        return False

    elif fileName[0:8] in HOLIDAY_LIST:
        logging.info(fileName + " is a trading holiday, skipping.\n")
        return False

    elif fileName[0:8] in BAD_DATES:
        logging.info(fileName + " is a trading holiday, skipping.\n")
        return False

    elif os.path.exists(FILE_DIR + fileName) and override is False:
        logging.info(fileName + " exists.\n")
        return False

    else:
        return True


def download_plays(end = None, startDate = None, after = None, before = None, override = False):
    """
    Using the DiscordChatExporter, the discord chat messages are exported to a json file. A file for each date.

    FileType is a required argument for the output file type: HtmlDark, HtmlLight, PlainText Json or Csv
    End is an optional parameter specifying the number of days to capture data for
    StartDate is an optional parameter which is the date to begin at, will default to 06-16-20, the first day the plays are available
    After is an optional parameter specifying that all plays after that time will be captured
    Before is an optional parameter specifying that all plays before that time will be captured
    Override is an optional parameter, used to specify if the dates should be downloaded if it already exists

    Has no return value
    """

    with open(CONFIG_DIR + "tokens.txt", 'r') as tokens:
        userToken = tokens.readline().split("\"")[1]
        channelID = tokens.readline().split("\"")[1]
        dllLocation = tokens.readline().split("\"")[1]

    # Exit if any of these fields are blank, exit. All three are necessary for the program to work
    if userToken == '' or dllLocation == '' or channelID == '':
        init()  # Only needed for Windows
        print(f"{Fore.CYAN}\nPlease insert the below items in the \"UnusualWhales/config/tokens.txt\" and restart program:\n" +
              f"\tDiscord user token\n\tThe location of the DiscordChatExporter.Cli.dll file{Style.RESET_ALL}")
        deinit()
        exit(1)

    ######################################
    with open(CONFIG_DIR + "tradingHolidays.txt", 'r') as holidays:
        [HOLIDAY_LIST.append(i[:-1]) for i in holidays.readlines()]  # Dates are recorded as 07-17-20, the [:-1] takes off the null terminator

    with open(CONFIG_DIR + "badDays.txt", 'r') as file:  # Dates where nothing was uploaded but should have due to error etc.. None so far
        [BAD_DATES.append(i[:-1]) for i in file.readlines()]  # Dates are recorded as 07-17-20, the -1 takes off the null terminator

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
        if (time.localtime()[3] < 6) or (time.localtime()[3] == 6 and date.today().timetuple()[4] < 30):
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
        fileName = dateFileName + ".json"

        if download_date(fileName, days):
            # If the file exists and the override is set to True OR the file doesnt exists, download the files
            if (os.path.exists(FILE_DIR + fileName) and override is True) or (not os.path.exists(BASE_DIR + '/' + fileName)):
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

                [logging.debug(i) for i in terminalCommands]

                subprocess.call(terminalCommands)

                if not CONFIG_DIR + fileName:
                    print("File not created.")
                    logging.error("File not created.")

                    raise FileNotFoundError
            else:
                logging.info("The weekday, holiday else clause.")


def main():
    """
    Executes other functions and carries out the overall goal of downloading files and adding plays from files to a database.

    Function has no parameters except global ones

    Has no return value
    """
    # Logging displays select info to the console
    # Debug, info, warning, error, critical is the order of levels
    logging.basicConfig(level = logging.DEBUG, format = "%(levelname)s -  %(message)s")
    logging.disable(logging.ERROR)  # Only show warning and higher, disables levels below warning

    prepare_files()
    error_log()

    print(f"\n{Fore.BLUE}Plays will be collected and added to the database.\nData is being gathered, wait for it to finish....{Style.RESET_ALL}")
    download_plays()
    file_to_db()
    remove_extras_from_db(DEFAULT_DB)


# GLOBAL DATA
DB_LIST = []
BAD_DATES = []
HOLIDAY_LIST = []
BASE_DIR = os.getcwd() + "/UnusualWhales"  # Where the files for this program will be stored
CONFIG_DIR = BASE_DIR + "/config/"
FILE_DIR = BASE_DIR + "/historyByDate/"
DEFAULT_DB = "WhalePlays.db"
# The below list contains the column titles for the SQL database entries.
#   There are two other columns createdDate and createdTime that are added on in file_to_db function.
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
                # createdDate is added on in file_to_db function
                # createdTime is added on in file_to_db function

if __name__ == "__main__":
    start = time.time()  # Used to measure run time of the program
    main()
    print("\n***All done, total runtime: {0:.05} seconds***".format(time.time() - start))

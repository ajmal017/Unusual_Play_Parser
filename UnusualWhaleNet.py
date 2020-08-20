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

import os  # For navigating the file system
import re  # Parsing for selective text
import sqlite3  # Managing database storage
import hashlib  # Retrieving and comparing hashes
import shutil  # Copying files
import bs4 as bs  # Navigating and gathering data from html files
import subprocess  # Used to issues terminal commands
import logging  # For selectively writing program information to the console
from datetime import date, timedelta  # Very useful in calculations involving dates
import pyperclip  # Copies the terminal comm


# For some reason, the Unusual Whales program does not filter out duplicates, this function removes duplicates from database
def cleanDuplicatesFromDB(file):
    if not os.path.exists(base_dir + "/config/" + file):
        file = defaultDBName

    conn = sqlite3.connect(base_dir + "/config/" + file)
    cur = conn.cursor()
    fileCopy = file[:file.rfind('.')] + '2' + file[file.rfind('.'):]  # Takes the filename and makes another filename with a '2' before the '.' - A.html & A2.html
    shutil.copy(base_dir + "/config/" + file, base_dir + "/config/" + fileCopy)  # Creates the copy

    if getHash(file) != getHash(base_dir + "/config/" + fileCopy):  # Makes sure that the two file are the same
        raise Exception("Plays damaged, abort.")

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
    hashFunction = None
    hashOutput = None

    if not os.path.exists(base_dir + "/config/" + fileName):
        raise FileNotFoundError

    if whichHash == 'sha1':
        hashFunction = hashlib.sha1()
    else:
        hashFunction = hashlib.md5()

    with open(base_dir + "/config/" + fileName, 'rb') as file:
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
# Playdate is an optional parameter which is the date to begin at, will default to 06-16-20, the first day the plays are available
# After is an optional parameter specifying that all plays after that time will be captured
# Before is an optional parameter specifying that all plays before that time will be captured
# Numberday is an optional parameter specifying the number of days to capture data for
# OutputFile is an optional parameter, it is the name of the html output file that contains all the plays for the date range
# Override is an optional parameter, used to specify if the dates should be downloaded if it already exists
# DbName is an optional parameter for suing a database nme of your choice
def getHTML(playdate = None, after = None, before = None, numberday = None, outputFile = None, override = False, dbName = None):
    os.chdir(base_dir + "/historyByDate")
    fileName, afterDate, beforeDate = "", "", ""

    # arguments passed to terminal to execute the dotnet command necessary to capture discord plays
    terminalCommands = ["dotnet",  # invokes dotnet command with the following as arguments
                        dllLocation,  # location of exporter program
                        "export",  # option that specifies we will be exporting a channel
                        "-t", userToken,  # use authorization token of user's account
                        "-c", channelID,  # channel ID of channel to be exported
                        "-o", base_dir + fileName,  # output file for the exported data
                        "--dateformat", "\"dd-MM-yy hh:mm tt\"",  # date format for the after and before parameters
                        "--after", afterDate,  # Get all channel messages after this date and time
                        "--before", beforeDate]  # Get all channel messages before this date and time

    if playdate is not None:
        sdate = date(playdate[0], playdate[1], playdate[2])  # Year, month and date
    else:
        sdate = date(2020, 6, 16)

    if type(numberday) == date:
        edate = date(numberday[0], numberday[1], numberday[2])
    else:
        edate = date.today()

    if type(numberday) is int:
        delta = timedelta(days = numberday)
    else:
        delta = edate - sdate

    # starts at s(tart)date and moves delta days forward to get range of dates
    for i in range(delta.days + 1):
        days = sdate + timedelta(days = i)

        month = days.timetuple()[2]  # Time tuple returns a tuple of year, day month
        day = days.timetuple()[1]
        year = str(days.timetuple()[0])[-2:]

        dateFileName = "{0:02d}-{1:02d}-{2}".format(day, month, year)  # The month and date are formatted in two decimal places
        fileName = dateFileName + ".html"

        if days.weekday() > 4:
            logging.info(fileName + " is a weekend, skipping.")
        elif fileName[0:8] in holidayList:
            logging.info(fileName + " is a trading holiday, skipping")
        elif os.path.exists(base_dir + "/historyByDate/" + fileName) and override is False:
            logging.info(fileName + " exists.")
        # If the file exists and the override is set to True OR the file doesnt exists, download the files
        elif (os.path.exists(base_dir + "/historyByDate/" + fileName) and override is True) or (not os.path.exists(base_dir + '/' + fileName)):
            if override:
                logging.info(fileName + " exists but override is signaled, creating...")
            else:
                logging.info(fileName + " does not exists, creating...")

            # If playdate, after and before are all passed in as parameters
            if after is not None and before is not None and playdate is not None:
                afterDate = dateFileName + " " + after
                beforeDate = dateFileName + " " + before
            else:
                afterDate = dateFileName + " 06:25"  # 6:25 in case plays start a bit earlier, just in case preparation
                beforeDate = dateFileName + " 13:05"  # 1:05 in case plays start a bit late or get delayed, just in case preparation
                # afterDate = "\"" + dateFileName + " 06:25" + "\""
                # beforeDate = "\"" + dateFileName + " 13:05" + "\""

            if outputFile is None:
                outputFile = dateFileName + ".html"

            terminalCommands[8] = base_dir + outputFile
            terminalCommands[12] = afterDate
            terminalCommands[14] = beforeDate

            [logging.debug(terminalCommands[arg]) for arg in range(len(terminalCommands))]

            # if the file should be copied, here it is easy to copy
            commandList = " ".join(terminalCommands)
            pyperclip.copy(commandList)
            logging.info("Command string copied to clipboard.\n", commandList)
            # input("Pause and check arg list elements...")

            subprocess.call(terminalCommands)
            logging.info('\n' + fileName + " has been created.")

            logging.info(fileName + " will be passed to html to DB.")

            if dbName is None or not os.path.exists("/config" + '/' + dbName):
                dbName = defaultDBName
                logging.info("DB name: " + dbName)

            # Each file is created, the play is passed to the database
            # It is not necessary to call the htmldb function here and can be called from main
            #   by creating a list of all html files in the folder and passing that list to html_to_DB
            html_to_DB(fileName, dbName)
        else:
            logging.info("The weekday, holiday else clause.")

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

    designChangeLog = open("/config/designChangeLog.txt", 'w')
    logging.debug("Passed in db name: ", dbName)

    if dbName is None:  # If no db is specified, use the default
        conn = sqlite3.connect(defaultDBName)
    else:  # Use dbName database
        conn = sqlite3.connect(dbName)
        
    cursor = conn.cursor()
    # Each  field is data that will be obtained for each options play
    cursor.execute('''CREATE TABLE IF NOT EXISTS Plays(symbol TEXT, date TEXT, style TEXT, strike REAL,
                                                       bid REAL, ask REAL, interest INTEGER, volume INTEGER,
                                                       iv REAL, diff REAL, price REAL)''')

    argList = []  # Will hold the files to parse for option plays
    os.chdir(base_dir + '/' + "/historyByDate")

    if htmlFile is None:  # if no file specified for play parsing, all files in play directory will be added
        [argList.append(i) for i in os.listdir() if i.endswith(".html")]
        argList.sort()  # To keep them in numerical order
    else:
        argList.append(htmlFile)  # Only add the specified html file

    # Other methods will be needed to extract data from cvs and json files
    for inputFile in argList:  # Checks every file in arglist
        logging.info("Checking file: [{0}]".format(inputFile))

        # Dates not a weekend or holiday where nothing was uploaded
        logging.info("Bad dates: ", badDates)

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

        # holds the raw data minus img tags and emoji chars
        for play_iter in range(len(strikeData)):  # each play is scraped for the play strike, price, date etc
            details = []  # The data captured will be stored here and then passed to the database
            match = pattern.match(strikeData[play_iter])  # A single play is captured here and the data about it will be parsed through regular expression

            if match is None:  # if the way the data is organized in the html file changes, the pattern will fail
                logging.info("Match is none, here is the play")
                logging.info('*' * 20, '\n', strikeData[play_iter], '\n', '*' * 20)
                match = backup_pattern.match(strikeData[play_iter])  # Backup pattern is used
                logging.info("Backup pattern utilized")

                if match is None:  # if the backup pattern fails
                    logging.error("Backup pattern failed")
                    logging.error('*' * 20, '\n', strikeData[play_iter], '\n', '*' * 20)
                    logging.error("New pattern necessary, format has changed.")
                    logging.error("Acknowledged and logged to designChangeLog.txt for analysis.")

                    designChangeLog = open("/config/designChangeLog.txt", "r+")
                    designChangeLog.write(strikeData[play_iter] + "#####")
                    designChangeLog.close()

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
        cursor.close()
        conn.close()

        print("File analysis complete, {0} records inserted into database.".format(len(strikeData)))


# If a play is not able to be captured by the regex or the backup regex, the text is stored in this file so a new pattern can be derived.
def errorLog():
    if not os.path.exists("/config/designChangeLog.txt"):
        with open("/config/designChangeLog.txt", 'x') as designChangeLog:  # Creates if it doesn't exist,
            print("No errors reported.")

    else:
        textList = []
        with open("/config/designChangeLog.txt", 'r') as designChangeLog:
            allText = designChangeLog.read()

            if allText == '':
                print("No errors reported.")
            else:
                for i in allText.split("#####"):
                    textList.append()

                [print(textList[i] + '\n') for i in range(len(textList))]


def main():
    # Setting up the log to display information about the program as it runs
    logging.basicConfig(level = logging.DEBUG, format = "%(levelname)s -  %(message)s")
    # logging.basicConfig(filename = 'unusualLogs.txt',level = logging.DEBUG, format = ' %(asctime)s -  %(levelname)s -  %(message)s')

    print("Plays will be collected and added to the database.\nData is being gathered, wait for it to finish....")

    getHTML()  # Gets an html file for every for every day that the program runs. Another function is called that creates and fills the database
    cleanDuplicatesFromDB(defaultDBName)  # Many duplicates are listed and this function removes them from the database

    print("All done!")
    logging.info("Database queries complete.")


strikeData = []  # Will hold the information after data is scraped from html files
base_dir = os.getcwd() + "/UnusualWhales"  # Where the files for this program will be stored
toCreate = ["UnusualWhales", "UnusualWhales/config", "UnusualWhales/config/backup", "UnusualWhales/historyByDate"]

os.chdir(base_dir)

defaultDBName = "WhalePlays.db"

for i in range(len(toCreate)):
    if not os.path.exists(toCreate[i]):
        os.mkdir(toCreate[i])
        logging.info(toCreate[i] + "has been created.")
    else:
        logging.info(toCreate[i] + " already exists.")

logging.debug(os.getcwd() + "/UnusualWhales exists: ", os.path.exists(base_dir + "/UnusualWhales"))
logging.debug(os.getcwd() + "/UnusualWhales/config exists: ", os.path.exists(base_dir + "/UnusualWhales/config"))
logging.debug(os.getcwd() + "/UnusualWhales/WhalePlays.db exists: ", os.path.exists(base_dir + "/UnusualWhales/WhalePlays.db"))
logging.debug(os.getcwd() + "/UnusualWhales/historyByDate exists: ", os.path.exists(base_dir + "/UnusualWhales/historyByDate"))
logging.debug(os.getcwd() + "/UnusualWhales/config/backup exists: ", os.path.exists(base_dir + "/UnusualWhales/config/backup"))

try:
    tokens = open("config/tokens.txt", 'r')  # Holds discord user token, channel id and discord scraper dll file
    userToken = tokens.readline().split("\"")[1]
    channelID = tokens.readline().split("\"")[1]
    dllLocation = tokens.readline().split("\"")[1]
    tokens.close()

except FileNotFoundError:
    # if not os.path.exists("config/tokens.txt"):
    print(os.getcwd())
    with open(base_dir + "/config/tokens.txt", 'w') as file:
        file.write("userToken = \"\"\nchannelID = \"721759406089306223\"\ndllLocation = \"\"\n")

    print("The program cannot continue without the following.\n" +
          "Please insert the below items in the \"UnusualWhales/config/tokens.txt\" file:\n" +
          "\tDiscord user token\n\tThe location of the DiscordChatExporter.Cli.dll file")

if not os.path.exists("/config/tradingHolidays.txt"):
    with open("/config/tradingHolidays.txt", 'w') as file:
        file.write("01-01-20\n01-20-20\n02-17-20\n04-10-20\n05-25-20\n07-03-20\n09-07-20\n11-26-20\n12-25-20\n\n" +
                   "01-01-21\n01-18-21\n02-15-21\n04-02-21\n05-31-21\n07-05-21\n09-06-21\n11-25-21\n12-24-21\n\n" +
                   "01-01-22\n01-17-22\n02-21-22\n04-15-22\n05-30-22\n07-04-22\n09-05-22\n11-24-22\n12-26-22\n\n")

holidayList = []  # A list of trading holidays that markets don't trade on
holidays = open(base_dir + "/config/tradingHolidays.txt", 'r')
[holidayList.append(i[:-1]) for i in holidays.readlines()]  # Dates are recorded as 07-17-20, the -1 takes off the null terminator
holidays.close()

# files = os.listdir(base_dir + "/historyByDate")  # Gathers all the html files downloaded by the program

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
              "ChangeCost"]  # int, (price - strike)


badDates = []  # In case there are days plays are not uploaded, none so far
file = open(base_dir + "/config/badDays.txt", 'a+')
[badDates.append(i[:-1]) for i in file.readlines()]  # Dates are recorded as 07-17-20, the -1 takes off the null terminator
file.close()

if __name__ == "__main__":
    main()

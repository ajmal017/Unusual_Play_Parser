# TODO
# Add gui and progress bar(s)
# Add search by field name
# Add command line access
# Fetching the plays individually takes extra much time.
#   Scan in whole chat history and separate by date
# Incorporate the bid and ask into the Moneyness
# Add function to update new column with data
# Create error log for rds rdsa
# If ticker fails, try with one less letter and try with a period before the last letter
# Add a file cleanup function and searching for json duplicate entries
# subCategorize foreign etfs and indexes
# except IndexError: return 0 in get_expiration_price, add bad symbols to a bad_list
# def check_date_for_adding_to_db(dateFile): # add time last run for checking todays plays
# Rename symbols that need a name change or alteration
#   Replace bgg with BGGSQ in Industrials, chk to chkq in energy, LLEX to llexq in energy etc
# Add "IsETF" column to database
# Update option chain for OI
# Check database lists for blanks
# Ask to view missed regex captures befre continuing with plays.
# except IndexError: return 0
#   What conditions cause IndexError?


# https://github.com/Tyrrrz/DiscordChatExporter/wiki/
# Created the discord scraper, DiscordChatExporter
# https://github.com/Tyrrrz/DiscordChatExporter/releases/download/2.22/DiscordChatExporter.CLI.zip

# Database browser for SQLite, very handy and insanely easy to use
# https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3.12.0/DB.Browser.for.SQLite-3.12.0.dmg

import os  # For navigating the file system
import re  # Parsing for selective text
import json  # Necessary for parsing json objects
import time  # Used to measure complete run time of program
import shutil  # Copying files
import hashlib  # Retrieving and comparing hashes
import logging  # For selectively writing program information to the console
import sqlite3  # Managing database storage
from zipfile import ZipFile  # Unzipping the CLI download
import requests  # Downloading the CLI and db browser files
from subprocess import call  # Used to issues terminal commands
import webbrowser  # Open file in the user's web browser
import configparser
from pathlib import Path  # Using path.name to get access to filename in url
from datetime import date, timedelta  # Very useful in calculations involving dates
from colorama import Style, Fore, init, deinit  # For turning the terminal text different colors
import openpyxl
import bs4 as bs
import CleanUp


def count_successful_plays_by_sector():
    """
    Shows the number of successful plays to date per sector

    Takes no parameters

    Returns no values
    """

    conn = sqlite3.connect(CONFIG_DIR + DEFAULT_DB)
    cur = conn.cursor()
    plays = []

    for i in STOCK_SECTORS:
        s = "\"%s\"" % i
        cur.execute("SELECT COUNT (*) FROM Plays WHERE moneyness > 0 AND sector = %s AND date LIKE \"2020-09\"" % s)
        data = cur.fetchall()[0][0]
        plays.append(data)

    print("Number of successful plays per sector")

    for i in range(len(STOCK_SECTORS)):
        print(STOCK_SECTORS[i] + ": " + str(plays[i]))

    # SELECT * FROM Plays WHERE moneyness > 0 AND date LIKE "2020-09%" ORDER BY sector
    # SELECT COUNT (*) FROM Plays WHERE moneyness > 0 AND sector = "Energy" AND date LIKE "2020-09%"


def error_log(erase = False):
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
                allText = allText.split("\n#####\n")

                for i in range(len(allText)):
                    textList.append(allText[i])

                # Prints plays that were not captured by regex
                [print(textList[i] + '\n') for i in range(len(textList))]

    if erase:
        open(CONFIG_DIR + "designChangeLog.txt", 'w').close()


def prepare_files():
    """
    This function prepares the files and folders necessary for the program to run

    Function has no parameters except the global ones

    Has no return value
    """

    global USER_TOKEN  # Declared below

    # Make sure the necessary directories are in place
    toCreate = [BASE_DIR, CONFIG_DIR, FILE_DIR, DOWNLOAD_DIR]

    for i in range(len(toCreate)):
        if not os.path.exists(toCreate[i]):
            os.mkdir(toCreate[i])
            logging.info(toCreate[i] + "has been created.")

        else:
            logging.info(toCreate[i] + " already exists.")

    if not os.path.exists(CONFIG_DIR + "DiscordChatExporter.CLI/"):
        os.mkdir(CONFIG_DIR + "DiscordChatExporter.CLI/")

        download_file("https://github.com/Tyrrrz/DiscordChatExporter/releases/download/2.22/DiscordChatExporter.CLI.zip")

        file_zip = ZipFile(DOWNLOAD_DIR + "DiscordChatExporter.CLI.zip")
        file_zip.extractall(CONFIG_DIR + "DiscordChatExporter.CLI/")
        file_zip.close()

        logging.info("DiscordChatExporter has been created.")

    os.chdir(BASE_DIR)

    if not os.path.exists(CONFIG_DIR + "database.txt"):
        open(CONFIG_DIR + "database.txt", 'x').close()

    if not os.path.exists(CONFIG_DIR + "badDays.txt"):
        open(CONFIG_DIR + "badDays.txt", 'x').close()

    # The file that holds the user's Discords token
    # Prepares creates the file with necessary text
    if not os.path.exists(CONFIG_DIR + "user_token.txt"):
        with open(CONFIG_DIR + "user_token.txt", 'w') as file:
            file.write("user_token = \"\"\n")

    # A list of holidays during which markets don't trade
    if not os.path.exists(CONFIG_DIR + "tradingHolidays.txt"):
        with open(CONFIG_DIR + "tradingHolidays.txt", 'w') as file:
            file.write("01-01-20\n01-20-20\n02-17-20\n04-10-20\n05-25-20\n07-03-20\n09-07-20\n11-26-20\n12-25-20\n\n" +
                       "01-01-21\n01-18-21\n02-15-21\n04-02-21\n05-31-21\n07-05-21\n09-06-21\n11-25-21\n12-24-21\n\n" +
                       "01-01-22\n01-17-22\n02-21-22\n04-15-22\n05-30-22\n07-04-22\n09-05-22\n11-24-22\n12-26-22\n\n")

    # If removing duplicates from dates list
    # old_list = lambda old_list: list(set(numbers))

    # Database browser, very useful for examining SQL databases
    # download_file("https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3.12.0/DB.Browser.for.SQLite-3.12.0.dmg")

    # Copy the user token from the file
    with open(CONFIG_DIR + "user_token.txt", 'r') as tokens:
        USER_TOKEN = tokens.readline().split("\"")[1]

    # If user token is blank, warn, show how to find it and then exit
    if USER_TOKEN == '':
        # init()  # Only needed for Windows, is part of changing the text color. Initializes the color changes.
        print(f"{Fore.CYAN}\nPlease insert the following into \"UnusualWhales/config/user_token.txt\" and restart program:\n" +
              f"\t**** Discord user token ****{Style.RESET_ALL}")
        # deinit()  # Only needed for Windows, is part of changing the text color. Stops the color change.

        answer = input("Would you like to open your web browser and see how to locate your user token?\nY / N: ")

        if answer[0].lower() == 'y':
            webbrowser.open("https://github.com/Tyrrrz/DiscordChatExporter/wiki/Obtaining-Token-and-Channel-IDs#how-to-get-user-token")

        exit(1)

    ######################################
    with open(CONFIG_DIR + "tradingHolidays.txt", 'r') as holidays:
        [HOLIDAY_LIST.append(i[:-1]) for i in holidays.readlines()]  # Dates are recorded as 07-17-20, the [:-1] takes off the null terminator

    with open(CONFIG_DIR + "badDays.txt", 'r') as file:  # Dates where nothing was uploaded but should have due to error etc.. None so far
        [BAD_DATES.append(i[:-1]) for i in file.readlines()]  # Dates are recorded as 07-17-20, the [:-1] takes off the null terminator

    with open(CONFIG_DIR + "database.txt", 'r') as file:  # Dates of all files that have already been added to the database
        [DB_LIST.append(i[:-1]) for i in file.readlines()]  # Dates are recorded as 07-17-20, the [:-1] takes off the null terminator


def get_sector(ticker, hide_found = False):
    """
    Gives the financial sector of the stock symbol passed in

    Ticker parameter is the symbol the stock uses on a given exchange

    Returns the ticker symbol or returns "ETF" since etf's don't have a sector according to pandas_finance
    """

    sector_base = CONFIG_DIR + "json_xlsx/"
    # print("Sector: ", sector_base)
    os.chdir(sector_base + "JSONS/")

    for sector_json_file in os.listdir():  # Change directory to folder with json sector files
        if sector_json_file.endswith(".json"):
            with open(sector_json_file, 'r') as json_file_reader:
                json_file_object = json.loads(json_file_reader.read())

                for entry in json_file_object:
                    if ticker is None:
                        input(ticker + ":")

                    if ticker.upper() == entry.get("name"):
                        if not hide_found:
                            # print(ticker + " found, sector is " + entry.get("sector"))
                            pass

                        if sector_json_file != "bad_symbols.json":
                            return entry.get("sector")
                        else:
                            return "N/A"

                    else:
                        # print("Ticker:", ticker.upper())
                        # print("Entry.name:", entry.get("name"))
                        pass
    try:
        """
        Consumer Staples, Consumer Defensive
        Financials, Financial Services
        Information Technology, Technology
        Communication, Communications, Communication Services
        Consumer Discretionary, Consumer Cyclical
        Health Care, Healthcare, Health
        Materials, Basic Materials
        Industrials, Industrial Services
        Energy
        Utilities
        Real Estate
        """
        r = requests.get("https://finance.yahoo.com/quote/XPEV/profile?p=%s" % ticker)
        soup = bs.BeautifulSoup(r.text, "html.parser")

        s = soup.find("span", text = "Sector(s)")
        s = s.find_next_sibling().text.replace('\n', '')

        if s == "Consumer Cyclical":
            return "Consumer Discretionary"

        elif s == "Consumer Defensive":
            return "Consumer Staples"

        elif s == "Financial Services":
            return "Financials"

        elif s == "Communication Services":
            return "Communications"

        elif s == "Basic Materials":
            return "Materials"

        elif s == "Communication Services":
            return "Communications"

        else:
            print(ticker + " not found.")
            return None

    except KeyError:
        print(ticker + " not found.")
        return None


def download_file(file_url):
    """
    Downloads a file from a passed in url

    File_url parameter is the url of the file needing downloading

    Returns True if file has been downloaded and false if it has not
    """

    req = requests.get(file_url, stream = True)
    p = Path(file_url)

    if not os.path.exists(DOWNLOAD_DIR + p.name):
        print("{} download beginning.".format(p.name))  # p.name is the file name and extension for a url / file aka "test.txt"

        # Downloads the file piece by piece and builds the whole file
        with open(DOWNLOAD_DIR + p.name, "wb") as file:
            for chunk in req.iter_content(chunk_size = 1024):
                # writing one chunk at a time to the file while there is more to get
                if chunk:
                    file.write(chunk)

    else:
        logging.debug(p.name + " already exists.")

    if req.status_code == requests.codes.ok:  # Literally means if the status of the download is OK
        print("{} download completed.".format(p.name))
        return True

    else:
        print("File has not been downloaded.")
        return False


def check_date_for_adding_to_db(dateFile):
    """
    Checks if the file represented by the parameter has already been added to the database

    DataFile parameter gets added to the file if its plays have been added to the database

    Returns True if passed in file is in the list of dates already in the database, false if not added to database
    """

    today_string = "{0:02d}-{1:02d}-{2}".format(time.localtime()[1], time.localtime()[2], str(time.localtime()[0])[-2:])

    if dateFile not in DB_LIST:
        return True

    # elif dateFile[:8] == today_string and time.localtime()[3:5] < (13, 1):
    #     logging.error(dateFile + " is today, probably new plays so now creating...")
    #     return True
    #
    # elif dateFile[:8] == today_string and time.localtime()[3:5] >= (13, 1):
    #     logging.error(dateFile + " is today, but no plays because it is after market close.")
    #     return False

    elif dateFile in DB_LIST:
        return False

    else:
        return True


def get_expiration_price(details):
    """
    Function gets the price at expiration

    Details parameter is the list that holds the information for the strike play

    Returns the value at expiration or null if expiration not yet passed
    """

    symbol = details[0]
    todays_date = date.today().timetuple()
    todays_date = "{0:02d}-{1:02d}-{2:02}".format(todays_date[0], todays_date[1], todays_date[2])

    # After 1pm of the trading day, the price is then used.
    # Or is the expiration day has already passed, it doesnt matter the time
    if(details[1] < todays_date) or (details[1] == todays_date and time.localtime()[3] >= 13):
        params = {"api_token": EOD_API_KEY, "from": details[1], "to": details[1]}

        try:  # https://eodhistoricaldata.com/api/eod/%s.US?api_token=5f5438fb96d006.32507074&from=2020-09-14&to=2020-09-14
            req = requests.get("https://eodhistoricaldata.com/api/eod/%s.US?" % symbol, params = params)

            eod_regex = re.compile(r"""(?P<Date>\d{4}\-\d{2}\-\d{2}),
                                       (?P<Open>\d{1,6}(\.\d{1,4})?),
                                       (?P<High>\d{1,5}(\.\d{1,4})?),
                                       (?P<Low>\d{1,5}(\.\d{1,4})?),
                                       (?P<Close>\d{1,5}(\.\d{1,4})?),
                                       (?P<Adjusted_Close>\d{1,6}(\.\d{1,4})?),
                                       (?P<Volume>\d{1,9})""", re.VERBOSE)

            req_data = req.text.splitlines()
            req_data.remove(req_data[0])
            req_data.remove(req_data[-1])

            try:
                exp = (re.match(eod_regex, req_data.pop())).group("Close")
                return exp

            except IndexError:
                return 0

        except KeyError:
            return None

    else:
        return None


def get_moneyness(details):
    """
    Checks expired plays in the database to see if they expired in, at or out of the money

    Details parameter is the list that holds the strike data that will be added to the database

    Returns the percentage the play was in (positive value) or out (negative value) of the money or None if not expired
    """

    if details[2].lower() == "c" and details[14] is not None:
        return ((float(details[14]) / float(details[3]) - 1))

    elif details[2].lower() == "p" and details[14] is not None:  # details[2] == "P".lower():
        return (1 - (float(details[14]) / float(details[3])))

    else:
        return None

    # y = "{0}-{1:02}-{2:02}".format(time.localtime()[0], time.localtime()[1], time.localtime()[2])


def remove_extras_from_db(file):
    """
    Used to filter out duplicate plays from database file. Makes a copy in case something goes wrong

    File parameter is the name of the file to remove duplicates from

    Has no return value
    """

    if not os.path.exists(CONFIG_DIR + file):
        file = DEFAULT_DB

    conn = sqlite3.connect(CONFIG_DIR + file)
    cur = conn.cursor()

    fileCopy = file[:file.rfind('.')] + '2' + file[file.rfind('.'):]  # Takes the filename and makes another filename with a '2' before the '.' - A.json & A2.json
    shutil.copy(CONFIG_DIR + file, CONFIG_DIR + fileCopy)  # Creates the copy

    if get_hash(file) != get_hash(fileCopy):  # Makes sure that the two file are the same
        os.unlink(CONFIG_DIR + fileCopy)
        raise Exception("Plays damaged, abort.")  # Where the copy comes into play, when the file is damaged

    else:
        os.unlink(CONFIG_DIR + fileCopy)  # Delete copy after, it is no longer needed

    cur.execute('''SELECT DISTINCT * FROM Plays''')  # Selects entries that are not duplicates
    data = cur.fetchall()
    cur.execute('''DELETE FROM Plays''')

    # Instead of using a for loop, you can use execute many with the variable that holds the data
    cur.executemany('''INSERT INTO Plays VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

    conn.commit()
    cur.close()
    conn.close()


def get_hash(fileName, whichHash = 'md5'):
    """
    Gets either the sha1 or md5 hash, used to make sure database copies are not corrupted

    FileName parameter is a string of the file that will be checked for hash
    WhichHash parameter specifies which hash style to use

    Returns the hash value of the file
    """

    # https: // stackoverflow.com / a / 22058673 / 1902959
    # Heavily borrowed from Randall Hunt's answer over at StackOverflow
    BUF_SIZE = 65536  # Read stuff in 64kb chunks

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


def plays_from_file_to_db(sourceFile = None, dbName = None):
    """
    Takes a file and extracts the option play data adding it to the database of all plays

    Dates is an optional parameter representing a list of dates to be passed to the db creator
    SourceFile is an optional parameter. It is an html file that should have the option plays scraped from its contents
    DbName is an optional parameter. It is the name of the database the plays should be added to.

    Has no return value
    """

    argList = []  # Will hold the files to parse for option plays
    os.chdir(FILE_DIR)

    if sourceFile is None:  # if no file specified for play parsing, all files in play directory will be added
        [argList.append(file) for file in os.listdir() if file.endswith("json")]
        print("None.")

    elif isinstance(sourceFile, list):
        for file in sourceFile:
            argList.append(file)
            print("List.")

    else:
        argList.append(sourceFile)  # Only add the specified html file
        print("Not list.")

    argList.sort()  # To keep them in numerical order

    if dbName is None:  # If no db is specified, use the default
        conn = sqlite3.connect(CONFIG_DIR + DEFAULT_DB)

    else:  # Use dbName database
        conn = sqlite3.connect(CONFIG_DIR + dbName)

    cursor = conn.cursor() # "4_TO-73_O20200709_00113995.pdf"
    # Each field is data that will be obtained for each options play
    cursor.execute('''CREATE TABLE IF NOT EXISTS Plays(symbol TEXT, date TEXT, style TEXT, strike REAL, bid REAL, ask REAL,
                                                        interest INTEGER, volume INTEGER, iv REAL, diff REAL, price REAL,
                                                        createdDate TEXT, createdTime TEXT, sector TEXT, exp_price REAL, moneyness REAL)''')

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
                                    (?P<Style>\w)\s*\$?
                                    (?P<Strike>\d{1,5}(\.\d{1,2})?)\s*Bid-Ask:\s*\$
                                    (?P<Bid>\d{1,5}(\.\d{1,2})?)\s*-\s*\$
                                    (?P<Ask>\d{1,5}(\.\d{1,2})?)\s*Interest:\s*
                                    (?P<Interest>[0-9,]{1,10})\s*Volume:\s*
                                    (?P<Volume>[0-9,]{1,10})\s*IV:\s*
                                    (?P<IV>\d{1,4}(\.\d{1,2})?)%\s*%\s*Diff:\s*
                                    (?P<Diff>-?\d{1,4}(\.\d{1,2})?)%\s*(Purchase|Underlying):\s*\$
                                    (?P<Price>\d{1,4}(\.\d{1,2})?.*)''', re.VERBOSE)

    # The above and this regex can be combined, but it is more readable separate. The below accounts for urls in play text
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
        print("Working with", inputFile)

        os.chdir(FILE_DIR)

        if check_date_for_adding_to_db(inputFile[:8]):  # Just check for the digits of file name and not the extension
            logging.info("Checking file: [{0}]".format(inputFile))
            strikeData = []  # Will hold the information after data is scraped from html files
            strikePlays = []  # Will hold the data as received from the files, before cleaning up text

            # logging.info("USING JSON FILES")
            # print("File location: ", os.path.abspath(inputFile))

            with open(inputFile, 'r') as jsonfile:
                parsejson = json.loads(jsonfile.read())  # ParseJson holds the json loaded from the datefile where the json was downloaded

            for i in range(len(parsejson["messages"])):
                data = parsejson["messages"][i]["content"]  # Content is the field where the play data is held

                if data != '':
                    strikePlays.append(parsejson["messages"][i]["content"])

                else:  # If the content field is empty then the data is held in the title and description fields
                    strikePlays.append(parsejson["messages"][i]["embeds"][0]["title"] + parsejson["messages"][i]["embeds"][0]["description"])

            for play in range(len(strikePlays)):  # StrikePlays holds the raw text with emojis and unnecessary characters, time to get clean
                string = []

                for character in range(len(strikePlays[play])):
                    if ord(strikePlays[play][character]) < 122:  # If it is a printable character
                        string.append(strikePlays[play][character])  # append it to the string
                strikeData.append(string)  # Finalize the changes and add it to the list of cleaned up data

            for play in range(len(strikeData)):  # Delete excess escaped characters located in the front of the string
                while not strikeData[play][0].isalpha():  # Stops deleting characters when the unnecessary characters are gone.
                    del strikeData[play][0]
                strikeData[play] = ''.join(strikeData[play])  # sd[k] is a list of strings, this turns said list into one string

            ######################################

            for play in range(len(strikeData)):  # each play is scraped for the play strike, price, date etc
                details = []  # The data captured will be stored here and then passed to the database
                match = pattern.match(strikeData[play])  # A single play is captured here and the data about it will be parsed through regular expression
                # logging.debug("FIRST MATCH")

                if match is None:  # if the way the data is organized in the html file changes, the pattern will fail
                    match = backup_pattern.match(strikeData[play])  # Backup pattern is used
                    # logging.debug("SECOND MATCH")

                    if match is None:
                        match = backup__pattern.match(strikeData[play])
                        # logging.debug("THIRD MATCH")

                        if match is None:  # if the backup pattern fails
                            logging.debug(input("Stop here and proceed with caution, match is None."))

                            # When the output and organization of the file changes, a new regex expression is necessary to capture data
                            # This show how the new data is organized so I can create backup patterns
                            logging.error("Backup pattern failed, new pattern necessary")
                            logging.error('*' * 20 + '\n' + strikeData[play] + '\n' + '*' * 20)

                            with open(CONFIG_DIR + "designChangeLog.txt", 'a+') as designChangeLog:
                                designChangeLog.write(strikeData[play] + "\n#####\n")

                            continue

                for group_number in range(11):
                    if group_number <= 2:  # The first three are strings
                        details.append(match.group(STRIKEINFO[group_number]))  # append(match.group("Bid")) etc.

                    else:  # Everything after is numeric
                        details.append(float(match.group(STRIKEINFO[group_number]).replace(',', '')))

                ######################################

                # Append the date and time created
                details.append(parsejson["messages"][i]["timestamp"][:10])  # Date play was scanned from the chain
                details.append(parsejson["messages"][i]["timestamp"][11:19])  # Time scanned from the options chain
                details.append(get_sector(details[0]))
                details.append(get_expiration_price(details))
                details.append(get_moneyness(details))
                logging.info(details)
                cursor.execute('''INSERT INTO Plays (symbol, date, style, strike, bid, ask, interest, volume, iv,
                                                     diff, price, createdDate, createdTime, sector, exp_price, moneyness)
                                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', details)
                conn.commit()

            print("File analysis complete, {0} records inserted into database.{1}".format(len(strikeData), "\n\t" + '*' * 25))

            with open(CONFIG_DIR + "database.txt", 'a+') as file:  # Append date to file when it has been added to the database
                if inputFile[:8] not in DB_LIST:
                    print("Adding {} to db_list.".format(inputFile[:8]))
                    file.write(inputFile[:8] + '\n')
                    DB_LIST.append(inputFile[:8])

                else:
                    logging.info("Already in db_list, {}.".format(inputFile[:8]))

        else:
            logging.info(inputFile + " already in database.")

    cursor.close()
    conn.close()


def check_if_need_download_date_file(file_name, days = None, override = []):
    """
    Every day has a file which contains all the Unusual Whale plays issued on that day

    file_name is a parameter that is used to determine if the date it represents needs to be downloaded
    Days is a parameter used to determine if the day passed in is a weekday or not
    Override parameter is used to flag a file that exists but should be downloaded again

    Returns True if the file for the passed in date needs to be downloaded, otherwise false if no download specified or needed
    """

    today_string = "{0:02d}-{1:02d}-{2}".format(time.localtime()[1], time.localtime()[2], str(time.localtime()[0])[-2:])

    if days is not None and days.weekday() > 4:
        logging.info(file_name + " is a weekend, skipping.\n")
        return False

    elif file_name[:8] in HOLIDAY_LIST:
        logging.info(file_name + " is a trading holiday, skipping.\n")
        return False

    elif file_name[:8] in BAD_DATES:
        logging.info(file_name + " is a trading holiday, skipping.\n")
        return False

    elif file_name[:8] == today_string:
        return True  # Need to add time last run to save unnecessary calls

    elif not os.path.exists(FILE_DIR + file_name):
        logging.info(file_name + " does not exists, creating...\n")
        return True

    elif os.path.exists(FILE_DIR + file_name) and file_name[:8] in override:
        logging.info(file_name + " exists but override is signaled, creating....\n")
        return True

    elif os.path.exists(FILE_DIR + file_name) and file_name[:8] not in override:
        logging.info(file_name + " exists, will not creating....\n")
        return False

    elif file_name[:8] == today_string and time.localtime()[3:5] < (13, 1):
        logging.info(file_name + " is today, probably new plays so now creating...\n")
        return True

    elif file_name[:8] == today_string and time.localtime()[3:5] >= (13, 1):
        logging.info(file_name + " is today but the market is closed.\n")
        return False

    else:
        return False


def download_plays(end = None, startDate = None, after = None, before = None, override = None):
    """
    Using the DiscordChatExporter, the discord chat messages are exported to a json file. A file for each date.

    FileType is a required argument for the output file type: HtmlDark, HtmlLight, PlainText Json or Csv
    End is an optional parameter specifying the number of days to capture data for or date to end at yyyy-mm-dd
    StartDate is an optional parameter which is the date to begin at, will default to 06-16-20, the first day the plays are available
    After is an optional parameter specifying that all plays after that time will be captured
    Before is an optional parameter specifying that all plays before that time will be captured
    Override is an optional parameter, used to specify if the dates should be downloaded if it already exists

    Has no return value
    """

    ######################################

    if override is None:
        override = []

    if startDate is None:
        sdate = date(2020, 6, 16)  # Start is 06/16/2020, first date plays were generated by Unusual Whales

    else:
        sdate = date(startDate[0], startDate[1], startDate[2])  # Year, month and date

    if type(end) == date:
        edate = date(end[0], end[1], end[2])  # Year, month, date

    elif type(end) is int:
        edate = sdate + timedelta(days = end - 1)

    else:
        # If it is a new day and before the market opens (before 06:30), don't include the current day
        if (time.localtime()[3] < 6) or (time.localtime()[3:5] < (6,30)):
            edate = date.today() - timedelta(days = 1)
            logging.info("The US market is not open yet.")

        else:
            edate = date.today()

    delta = edate - sdate  # Delta is the change or number of days to count forward from the starting date

    ######################################

    # starts at s(tart)date and moves delta days forward to get range of dates
    for day_number in range(delta.days + 1):
        os.chdir(FILE_DIR)

        days = sdate + timedelta(days = day_number)
        month = days.timetuple()[2]  # Time tuple returns a tuple of year, day month
        day = days.timetuple()[1]
        year = str(days.timetuple()[0])[-2:]

        date_file_name = "{0:02d}-{1:02d}-{2}".format(day, month, year)  # Month and date are formatted to two decimal places
        file_name = date_file_name + ".json"

        if check_if_need_download_date_file(file_name, days, override):
            # If the file exists and the override is set to True OR the file doesnt exists, download the files
            if file_name[:8] in override:
                logging.info(file_name + " exists but override is signaled, creating...")
            #
            # else:
            #     logging.info(file_name + " does not exists, creating...")

            # If playdate, after and before are all passed in as parameters
            if after is not None and before is not None and startDate is not None:
                afterDate = date_file_name + " " + after
                beforeDate = date_file_name + " " + before

            else:
                afterDate = date_file_name + " 06:25"  # 6:25 in case plays start a bit earlier, just in case preparation
                beforeDate = date_file_name + " 13:05"  # 1:05 in case plays start a bit late or get delayed, just in case preparation

            # arguments passed to terminal to execute the dotnet command necessary to capture discord plays
            terminalCommands = ["dotnet",  # invokes dotnet command with the following as arguments
                                DLL_LOCATION,  # location of exporter program
                                "export",  # option  that specifies we will be exporting a channel
                                "-t", USER_TOKEN,  # use authorization token of user's account
                                "-c", CHANNEL_ID,  # channel ID of channel to be exported
                                "-o", FILE_DIR + file_name,  # output file for the exported data
                                "--dateformat", "\"dd-MM-yy hh:mm\"",  # date format for the after and before parameters
                                "--after", afterDate,  # Get all channel messages after this date and time
                                "--before", beforeDate,  # Get all channel messages before this date and time
                                "-f", "json"]  # HtmlDark, HtmlLight, PlainText Json or Csv

            # Show the terminal commands for each play
            # [logging.debug(i) for i in terminalCommands]

            # For Windows
            # terminalCommands = terminalCommands[1:]

            # Subprocess take a list as an argument
            call(terminalCommands)
            print(date_file_name + " downloaded.\n\t")
            print(f"{Fore.RED}-------------------------{Style.RESET_ALL}")

            if not CONFIG_DIR + file_name:
                print("File not created.")
                logging.error("File not created.")

                raise FileNotFoundError


def main():
    """
    Executes other functions and carries out the overall goal of downloading files and adding plays from files to a database.

    Function has no parameters except global ones

    Has no return value
    """

    # Logging displays select info to the console
    # Debug, info, warning, error, critical is the order of levels
    # logging.basicConfig(level = logging.DEBUG, format = "%(levelname)s -  %(message)s")
    logging.disable(logging.WARNING)  # Only show warning and higher, disables levels below warning

    prepare_files()  # Files need to be prepared and created so program can work properly
    error_log(True)  # Shows if errors occurred when parsing plays

    # Fore.color changes the color of the text, Style.reset changes the color back to white
    print(f"\n{Fore.BLUE}Plays will be collected and added to the database.\nData is being gathered, wait for it to finish....\n{Style.RESET_ALL}")

    download_plays()
    plays_from_file_to_db()
    remove_extras_from_db(DEFAULT_DB)


STOCK_SECTORS = ["Communications",
                 "Consumer Discretionary",
                 "Consumer Staples",
                 "Technology",
                 "Energy",
                 "Healthcare",
                 "Industrials",
                 "Materials",
                 "Utilities",
                 "Real Estate"]

# GLOBAL DATA
BASE_DIR = os.getcwd() + "/UnusualWhales"  # Where the files for this program will be stored
CONFIG_DIR = BASE_DIR + "/config/"
FILE_DIR = BASE_DIR + "/historyByDate/"
DOWNLOAD_DIR = BASE_DIR + "/downloads/"
DEFAULT_DB = "WhalePlays.db"
DEFAULT_DB_LOCATION = CONFIG_DIR + DEFAULT_DB
KEYS = ["name", "sector"]
DB_LIST = []
BAD_DATES = []
HOLIDAY_LIST = []
USER_TOKEN = ""
CHANNEL_ID = "721759406089306223"
DLL_LOCATION = CONFIG_DIR + "DiscordChatExporter.CLI/DiscordChatExporter.Cli.dll"

config = configparser.ConfigParser()
config.read(CONFIG_DIR + "CONFIG_APIS.ini")
EOD_API_KEY = config["EOD_HISTORICAL"]["LIVE_KEY"]

# The below list contains the column titles for the SQL database entries.
#   There are two other columns, createdDate and createdTime, that are added on in plays_from_file_to_db function.
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

if __name__ == "__main__":
    start = time.time()  # Used to measure run time of the program
    main()
    print("\n***All done, total runtime: {0:.05} seconds***".format(time.time() - start))

# https://programtalk.com/python-examples/PyPDF2.PdfFileMerger/
# Books 1 -6 can be run with the functionality so far.
# Find YellowPacket file
# Workbook has 105 as a start and an end

import os, PyPDF2, logging, re
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logging.disable(logging.DEBUG)

# 0 - 13
# 9 - 17

def get_merged_pdf(fileList, outputPDF):
    # Gets the starting page from the pdf name, 1_[000]-123_O.pdf
    def getStart(pdf):
        return int(pdf.name[pdf.name.index('_') + 1 : pdf.name.index('-')])

    # Gets the ending page from the pdf name, 1_000-[123]_O.pdf
    def getEnd(pdf):
        return int(pdf.name[pdf.name.index('-') + 1 : pdf.name.rfind('_')])

    merger = PyPDF2.PdfFileMerger()
    pdfs = [open(pdf, 'rb') for pdf in fileList]

    # Stops are len - 1 to prevent out of bounds
    for i in (len(pdfs) - 1):
        if i  == 0:
            merger.append(pdfs[0])
        else:
            currStart = getStart(pdfs[i])
            currEnd = getEnd(pdfs[i])

            prevStart = getStart(pdfs[i-1])
            prevEnd = getEnd(pdfs[i-1])

            # If the starting page of next file is less than the ending page of current file,
            #   then there is an overlap. #1 is [000-123] and #2 is [121-149].
            #   Pages 121 and 123 are already covered by the first file
            if currStart <= prevEnd:
                # So the overlapping pages are excluded from the final pdf
                # /Users/X/Uncompressed/Temp will be used to store the files temporarily
                if currEnd <= prevEnd:
                    pass
                else:
                    merger.append(extractPage(pdfs[i].name, str((currStart - prevEnd)/2), "/Users/X/Uncompressed/Temp" + str(i) + ".pdf")[0])
            else: # If no overlap occurs, simply add the file
                merger.append(pdfs[i])

    # Delete the contents of temp folder. /Users/X/Uncompressed/Temp
    for file in os.listdir("/Users/X/Uncompressed/Temp"):
        try:
            os.unlink(file)
        except Exception as e:
            print(str(e))

    # The name of the new file
    outFile = outputPDF

    # Closes open files and writes pdf
    with open(outFile, 'wb') as pdf:
        merger.write(pdf)
    [fp.close() for fp in pdfs]
    print(outputPDF + " has been saved.")
    merger.close()

# merger = PdfFileMerger()
# for filename in filenames:
#     merger.append(PdfFileReader(file(filename, 'rb')))
#
# merger.write("document-output.pdf")

# Returns a tuple of the (filepath, filename)
def extractPage(fileName, prompt = "", outputName = ""):
    whichPages = [] # Stores the pages to be extracted
    filepath = Path(fileName)

    pdf = open(fileName, "rb")
    reader = PyPDF2.PdfFileReader(pdf)
    writer = PyPDF2.PdfFileWriter()

    # Can pass in a negative number to indicate the last x amount of pages, -2 for the last two
    if not prompt.startswith('-'):
        if prompt == "": # if page numbers are not passed in to function, get them
            prompt = input("Enter pages separated by spaces, 1 2 3 or a page range 2-3:")
        else:  # Removes spaces from input and turns 2 - 3 into 2-3
            prompt = prompt.replace(" ", "")

        # Takes pages and turns them into a list, whichPages
        if '-' in prompt: # If page range passed in, 2-3
            prompt = prompt.split('-')

            for page in range(int(prompt[0]), int(prompt[1]) + 1):
                whichPages.append(page)
        # else if individual and separate pages are passed, add those, 1 3 5 7 10 etc..
        else:
            for num in prompt.split(' '):
                whichPages.append(int(num))

        # Adds the pages in the list to the queue to become part of the final pdf
        for page in range(reader.numPages):
            if page + 1 in whichPages:
                page = reader.getPage(page)
                writer.addPage(page)

    # If prompt begins with a - that signals the amount of pages from the end to return
    else:
        prompt = int(prompt.replace('-', ''))

        for page in range(reader.numPages - prompt, reader.numPages):
            page = reader.getPage(page)
            writer.addPage(page)

    # If no output name is passed in, the new file name will reflect the pages in it
    prefix = ""
    if outputName == "":
        if len(whichPages) > 1:
            for page in whichPages:
                prefix += str(whichPages[page]) + "-"
            prefix = prefix.rsplit('-', 1)[0]
        else:
            prefix = str(whichPages[0]) + '_'

        outputName = prefix + filepath.name

    if not outputName.endswith(".pdf"):
        outputName += ".pdf"

    outputName = str(filepath.parent) + '/' + outputName

    print(outputName + " is the name of the new file.")

    newPdf = open(outputName, "wb")
    writer.write(newPdf)

    pdf.close()
    newPdf.close()

    outputName = Path(outputName)

    return(str(outputName), outputName.name)


def get_reverse_pdf(fileName, outputPDF = ""):
    if outputPDF == "":
        outputPDF = fileName

    pdf = open(fileName, "rb")
    reader = PyPDF2.PdfFileReader(pdf)
    writer = PyPDF2.PdfFileWriter()

    for page in range(reader.getNumPages() - 1, -1, -1):
        page = reader.getPage(page)
        writer.addPage(page)

    newPDF = open(outputPDF, "wb")
    writer.write(newPDF)

    pdf.close()
    newPDF.close()

    print(fileName, "has been reversed.")


folders = []
folderBase = "/Users/X/Uncompressed"
os.chdir(folderBase)

for name in os.listdir():
    if os.path.isdir(name):
        folders.append(name)

folders.sort()

logging.debug("Folders:")

for name in folders:
    logging.debug(name)

logging.debug("-------------------")

for name in folders:
    os.chdir(folderBase + '/' + name)
    files = {"FileName": []}

    for file in os.listdir():
        if os.path.isfile(file) and file.endswith(".pdf"):
            files["FileName"].append(file)

    # This is the only folder where the files are arranged differently
    # folderRegex = re.compile(r'\w*\d{4}')
    # if folderRegex.search(files[0]):
    if name == "YellowPacket":  # Files are organized differently, needs special care
        get_merged_pdf(files, folderBase + "/Final/" + name + ".pdf")

    elif name == ""

    else:
        fileList = []
        even = []
        odd = []

        # Add the pdfs to a list, filters out other file types
        for file in os.listdir():
            if os.path.isfile(file) and file.endswith(".pdf"):
                fileList.append(file)

        # Go through the file names
        for file in fileList:
            originalName = file

            # Create a list from file name since strings don't have an insert function
            file = list(file)

            # check for TO or TE in file name and removes it
            # Replaces it with 000 since it represents the first page
            if 'T' in file:
                remove = file.index('T')
                del file[remove: remove + 2]

                for i in range(2, 5):
                    file.insert(remove, '0')

            # All page numbers should be three digits
            # The first index of '-' minus the first index of '_' should be 4 spaces apart
            # _000- aka indexes 9,10,11,12,13 or 1,2,3,4
            while file.index('-') - file.index('_') <= 4:
                file.insert(file.index('_') + 1, '0')

            file = "".join(file)

            os.rename(originalName, file)

            # Adds it to the even or odd list
            if "_O" in file:
                odd.append(file)
            elif "_E" in file:
                even.append(file)

        # Sorts the list and makes a creates one pdf with the odd page sheets
        odd.sort(key = lambda x: x[1:5])
        get_merged_pdf(odd, name + "_odd.pdf")

        # Sorts the list and makes a creates one pdf with the even page sheets
        # Even pages are reversed because they were scanned in reverse order
        even.sort(key = lambda x: x[1:5], reverse = True)
        get_merged_pdf(even, name + "_even.pdf")

        # Creates one large pdf containing even and od pages in the correct order
        get_merged_pdf([name + "_odd.pdf", name + "_even.pdf"], folderBase + "/Final/" + name + ".pdf")


#
# def reset():
#     start = perf_counter()
#
#     for file in os.listdir("/Users/X/Uncompressed/503_12"):
#         os.unlink(file)
#         if os.path.exists(file):
#             print("FILE NOT DELETED")
#
#         for file in os.listdir("/Users/X/Uncompressed/503_1"):
#             shutil.copytree("/Users/X/Uncompressed/503_1", "/Users/X/Uncompressed/503_12", dirs_exist_ok = True)
#
#     if os.path.exists(os.listdir("/Users/X/Uncompressed/503_12")[0]):
#         print("Reset complete.")
#
#     print("Took %s seconds" % str(perf_counter() - start))

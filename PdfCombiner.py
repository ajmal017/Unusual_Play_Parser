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
    merger = PyPDF2.PdfFileMerger()

    pdfs = [open(pdf, 'rb') for pdf in fileList]


    def getStart():
        pass


    def getEnd():
        pass

    for pdf in pdfs:
    for i in (len(pdfs) - 1):
        # get start and end for current
        currStart = int(pdfs[i].name[pdfs[i].name.index('_') + 1 : pdfs[i].name.index('-')])
        currEnd = int(pdfs[i].name[pdfs[i].name.index('-') + 1 : pdfs[i].name.rfind('_')])
        
        nextStart = int(pdfs[i+1].name[pdfs[i+1].name.index('_') + 1 : pdfs[i+1].name.index('-')])
        nextEnd = int(pdfs[i+1].name[pdfs[i+1].name.index('-') + 1 : pdfs[i+1].name.rfind('_')])

        if  nextStart <=  currEnd:
        #     add (next end - current end) / 2 from the end of next
            merger.append(
                extractPage() # add neccessary sheets only
            )
        else:
            merger.append(pdf)

    outFile = outputPDF

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


def extractPage(fileName, prompt = "", outputName = ""):
    whichPages = []
    filepath = Path(fileName)

    if prompt == "":
        prompt = input("Enter pages separated by spaces, 1 2 3 or a page range 2-3:")
    else:
        prompt = prompt.replace(" ", "")

    if '-' in prompt:
        prompt = prompt.split('-')

        for j in range(int(prompt[0]), int(prompt[1]) + 1):
            whichPages.append(j)
    else:
        for num in prompt.split(' '):
            whichPages.append(int(num))

    pdf = open(fileName, "rb")
    reader = PyPDF2.PdfFileReader(pdf)
    writer = PyPDF2.PdfFileWriter()

    for page in range(reader.numPages):
        if page + 1 in whichPages:
            page = reader.getPage(page)
            writer.addPage(page)

    suffix = ""
    if outputName == "":
        if len(whichPages) > 1:
            suffix = str(whichPages[0]) + '-' + str(whichPages[-1]) + '_'
        else:
            suffix = str(whichPages[0]) + '_'

        outputName = suffix + filepath.name

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


#    print("\n-----------------------------------------------------------------")
#
# https://stackoverflow.com/questions/17104926/pypdf-merging-multiple-pdf-files-into-one-pdf
#
# from PyPDF2 import PdfFileMerger, PdfFileReader
#
# [...]
#
# merger = PdfFileMerger()
# for filename in filenames:
#     merger.append(PdfFileReader(file(filename, 'rb')))
#
# merger.write("document-output.pdf")


###############################################
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

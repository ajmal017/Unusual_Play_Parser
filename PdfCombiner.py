# Import necessary modules
import os, PyPDF2 as pypdf
from pathlib import Path

folders = []
folderBase = "/Users/X/Uncompressed"
os.chdir(folderBase)

for name in os.listdir():
    if os.path.isdir(name):
        folders.append(name)

folders.sort()

print("Folders:")

for name in folders:
    print(name)

print("-------------------")

# The folder name will be the name of the resulting pdf
# Open folders
for name in folders:
    os.chdir(folderBase + '/' + name)
    files = {"FileName" : [], "PdfObject" : [], "BookNumber" : [], "StartPage" : [], "EndPage" : [], "EvenOdd" : []}

    for file in os.listdir():
        if os.path.isfile(file):
            files["FileName"].append(file)

    # files.sort()
    for file in files:
        print(file, end = '\n')

    if name == "Yellow":  # Files are organized differently
        # Extract number from pdf file name or sort
        # The first one has no number
        reader1 = pypdf.PdfFileReader("YellowPacket.pdf")
        reader2 = pypdf.PdfFileReader("YellowPacket0001.pdf")
        reader3 = pypdf.PdfFileReader("YellowPacket0002.pdf")
        reader4 = pypdf.PdfFileReader("YellowPacket0003.pdf")
        reader5 = pypdf.PdfFileReader("YellowPacket0004.pdf")

        def combinePdf(pdf1, pdf2):


        # pdfFile1 = open("", "rb")
        # pdfFile2 = open("", "rb")
        # reader1 = pypdf.PdfFileReader(pdfFile1)
        # reader2 = pypdf.PdfFileReader(pdfFile2)
        # writer = pypdf.PdfFileWriter()
        #
        # for pageNum in range(reader1.numPages):
        #     page = reader1.getPage(pageNum)
        #     writer.addPage(pageNum)
        #
        # for pageNum in range(reader2.numPages):
        #     page = reader2.getPage(pageNum)
        #     writer.addPage(pageNum)
        #
        # outputFile = open("", "wb")
        # writer.write(outputFile)
        # outputFile.close()
        # pdfFile1.close()
        # pdfFile2.close()
    else:
        for i in len(files):
            create list for odd pages

        for every file
            determine the bookNum startPage, endPage, EvenOdd

            check if all bookNumbers are the same
                if not
                    exit and throw error
            bookNumList.sort()

            oddPages = []
            evenPages = []

            create list for odd pages
                [0] = startPage == TO
                if end == [i -1] + 1
                    is not last page
                        .append([i])
                    else
                        .append([i])

            create a list for even pages

    print("\n-----------------------------------------------------------------")

# Remove extra characters from file name
#   characters beyond indexOf("_E" | "_O") can be truncated
# Add names of pdf files in folder to a list
# Parse the file name based on name rule
#   BookNumber_StartingPage-EndingPage_EvenOddPageIndicator
#   \d_\d{1,3}-\d{1,3}_((E|e)|(O|o))
#   Create a list for each file, book #, starting page, ending page, even or Odd

# File names cleaned up and organized
# Find files with same book# and starting/ending page# but differing evenOdd character
#   A new file is created and will be filled from _O and _E
#   _O and _E should have same number of pages
#   Odd contributes a page then even



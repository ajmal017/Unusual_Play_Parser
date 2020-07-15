# Import necessary modules
import os, PyPDF2 as pypdf, logging
from pathlib import Path
logging.basicConfig(level=logging.DEBUG)
# logging.disable(logging.DEBUG)

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

# The folder name will be the name of the resulting pdf
# Open folders
for name in folders:
    os.chdir(folderBase + '/' + name)
    files = {"FileName" : [], "PdfObject" : [], "BookNumber" : [], "StartPage" : [], "EndPage" : [], "EvenOdd" : []}

    logging.debug("------" + str(name) + "-----------------------------")
    for file in os.listdir():
        if os.path.isfile(file) and file.endswith(".pdf"):
            files["FileName"].append(file)
            logging.debug(">>>>>>" + str(file))

    if name == "YellowPacket":  # Files are organized differently, needs special care
        logging.debug("......................")

        writer = pypdf.PdfFileWriter()

        for file in ["YellowPacket.pdf", "YellowPacket0001.pdf", "YellowPacket0002.pdf", "YellowPacket0003.pdf", "YellowPacket0004.pdf"]:
            pdf_file = open(file, "rb")
            logging.debug("Working on packet " + str(file))
            reader = pypdf.PdfFileReader(file)
            for pageNum in range(reader.numPages):
                pageNum = reader.getPage(pageNum)
                writer.addPage(pageNum)

        outputFile = open("/Users/X/Uncompressed/Final/YellowFolder.pdf", "wb")
        writer.write(outputFile)
        outputFile.close()
        pdf_file.close()

#     else:
#         for i in len(files):
#             create list for odd pages
#
#         for every file
#             determine the bookNum startPage, endPage, EvenOdd
#
#             check if all bookNumbers are the same
#                 if not
#                     exit and throw error
#             bookNumList.sort()
#
#             oddPages = []
#             evenPages = []
#
#             create list for odd pages
#                 [0] = startPage == TO
#                 if end == [i -1] + 1
#                     is not last page
#                         .append([i])
#                     else
#                         .append([i])
#
#             create a list for even pages
#
#     print("\n-----------------------------------------------------------------")

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
    files = {"FileName": [], "PdfObject": [], "BookNumber": [], "StartPage": [], "EndPage": [], "EvenOdd": []}

    for file in os.listdir():
        if os.path.isfile(file) and file.endswith(".pdf"):
            files["FileName"].append(file)

    if name == "YellowPacket":  # Files are organized differently, needs special care

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

    else:
        even = {"Name": [], "StartPage": [], "EndPage": []}
        odd = {"Name": [], "StartPage": [], "EndPage": []}

        for file in os.listdir(folderBase + '/' + name):
            if "_O" in file:
                newfile = file[:(file.index("_O") + 2)] + ".pdf"
                newfile.replace('-', '_')
                os.rename(file, newfile)
                odd["Name"].append(newfile)
                currentIndex = odd["Name"].index(newfile)
                split = odd["Name"][currentIndex].split('_')

                if split[1] == "TO":
                    split[1] = 0

                odd["StartPage"].append(split[1])
                odd["EndPage"].append(split[2])

            elif "_E" in file:
                newfile = file[:(file.index("_E") + 2)] + ".pdf"
                newfile.replace('-', '_')
                os.rename(file, newfile)
                even["Name"].append(newfile)
                currentIndex = even["Name"].index(newfile)
                split = even["Name"][currentIndex].split('_')
                even["StartPage"].append(split[1])

                if split[1] == "TE":
                    split[1] = 0

                even["EndPage"].append(split[2])


            odd["StartPage"].sort()
            odd["StartPage"].index()
    print("\n-----------------------------------------------------------------")

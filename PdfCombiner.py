# https://programtalk.com/python-examples/PyPDF2.PdfFileMerger/

import os, PyPDF2, logging
logging.basicConfig(level=logging.DEBUG)
logging.disable(logging.DEBUG)


def get_merged_pdf(fileList, outputPDF):
    merger = PyPDF2.PdfFileMerger()

    pdfs = [open(pdf, 'rb') for pdf in fileList]

    for pdf in pdfs:
        merger.append(pdf)

    outFile = outputPDF

    with open(outFile, 'wb') as pdf:
        merger.write(pdf)

    [fp.close() for fp in pdfs]
    print(outputPDF + " has been saved.")
    merger.close()


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

    newPDF.close()
    newPDF.close()
    pdf.close()

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

    if name == "YellowPacket":  # Files are organized differently, needs special care

        writer = PyPDF2.PdfFileWriter()

        for file in ["YellowPacket.pdf", "YellowPacket0001.pdf", "YellowPacket0002.pdf", "YellowPacket0003.pdf", "YellowPacket0004.pdf"]:
            pdf_file = open(file, "rb")
            logging.debug("Working on packet " + str(file))
            reader = PyPDF2.PdfFileReader(file)
            for pageNum in range(reader.numPages):
                pageNum = reader.getPage(pageNum)
                writer.addPage(pageNum)

        outputFile = open("/Users/X/Uncompressed/Final/YellowFolder.pdf", "wb")
        writer.write(outputFile)
        outputFile.close()
        pdf_file.close()

    else:
        fileList = []
        even = []
        odd = []

        fileList = os.listdir(folderBase + '/' + name)

        if os.path.exists(".DS_Store"):
            del fileList[fileList.index(".DS_Store")]

        for file in fileList:
            originalName = file
            file = list(file)

            if 'T' in file:
                remove = file.index('T')
                del file[remove: remove + 2]

                for i in range(2, 5):
                    file.insert(remove, '0')

            while file.index('-') != 5:
                file.insert(2, '0')

            file = "".join(file)

            os.rename(originalName, file)

            if "_O" in file:
                odd.append(file)
            elif "_E" in file:
                even.append(file)

        odd.sort(key = lambda x: x[1:5])
        merge_pdfs(odd, name + "_odd.pdf")

        even.sort(key = lambda x: x[1:5], reverse = True)
        merge_pdfs(even, name + "_even.pdf")

        merge_pdfs(["Book1_odd.pdf", "Book1_even.pdf"], "Book1_Complete.pdf")


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
# Import necessary modules
import os, PyPDF2 as pypdf
from pathlib import Path


def combinePdf(pdf_name1, pdf_name2):
    print(pdf_name1, " + ", pdf_name2, end = "")
    pdf_file1 = open(pdf_name1, "rb")
    pdf_file2 = open(pdf_name2, "rb")
    reader1 = pypdf.PdfFileReader(pdf_file1)
    reader2 = pypdf.PdfFileReader(pdf_file2)
    writer = pypdf.PdfFileWriter()

    for pageNum in range(reader1.numPages):
        pageNum = reader1.getPage(pageNum)
        writer.addPage(pageNum)
        pageNum = reader2.getPage(pageNum)
        writer.addPage(pageNum)

    if not os.path.exists("/Users/X/Uncompressed/Final/YellowPacket1.pdf"):
        if (os.path.exists("/Users/X/Uncompressed/Final/YellowPacket.pdf")):
            outputFile = open("/Users/X/Uncompressed/Final/YellowPacket1.pdf", "wb")
        else:
            outputFile = open("/Users/X/Uncompressed/Final/YellowPacket.pdf", "wb")
    else:
        outputFile = open("/Users/X/Uncompressed/Final/YellowPacket!.pdf")

        writer.write(outputFile)
        outputFile.close()
        pdf_file1.close()
        pdf_file2.close()

    print(" = ", outputFile.name)
    return outputFile.name


folders = []
folderBase = "/Users/X/Uncompressed"
os.chdir(folderBase)

for name in os.listdir():
    if os.path.isdir(name):
        folders.append(name)

folders.sort()

# print("Folders:")
#
# for name in folders:
#     print(name)
#
# print("-------------------")

# The folder name will be the name of the resulting pdf
# Open folders
for name in folders:
    os.chdir(folderBase + '/' + name)
    files = {"FileName" : [], "PdfObject" : [], "BookNumber" : [], "StartPage" : [], "EndPage" : [], "EvenOdd" : []}

    # print("------", name, "-----------------------------")
    for file in os.listdir():
        if os.path.isfile(file) and file.endswith(".pdf"):
            files["FileName"].append(file)
            print(">>>>>>", file)

    if name == "YellowPacket":  # Files are organized differently
        # Extract number from pdf file name or sort
        # The first one has no number
        print("......................")

        # Should combine 1 with 0, 3 with 2 and the combination of those two with 4 to be the new pdf.
        # combinePdf(
       # print(type(files["FileName"][0]))
        combinePdf(files["FileName"][0], files["FileName"][2])
        # combinePdf(files["FileName"][2:4]))



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
#
# # Remove extra characters from file name
# #   characters beyond indexOf("_E" | "_O") can be truncated
# # Add names of pdf files in folder to a list
# # Parse the file name based on name rule
# #   BookNumber_StartingPage-EndingPage_EvenOddPageIndicator
# #   \d_\d{1,3}-\d{1,3}_((E|e)|(O|o))
# #   Create a list for each file, book #, starting page, ending page, even or Odd
#
# # File names cleaned up and organized
# # Find files with same book# and starting/ending page# but differing evenOdd character
# #   A new file is created and will be filled from _O and _E
# #   _O and _E should have same number of pages
# #   Odd contributes a page then even
#
#

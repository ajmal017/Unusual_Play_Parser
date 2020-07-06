import bs4 as bs
import re

# The loan data is located in a <tbody> within a <table id = "postedPaymentsTable">.
f = open("/Users/X/Documents/Documents/SantanderCarLoan.html", 'r')
contents = f.read()
soup = bs.BeautifulSoup(contents, "html.parser")

#  It is in several rows with class = "even" or  class = "odd"
table = soup.find("table", {"id": "postedPaymentsTable"})
tbody = table.find("tbody")
table_rows = tbody.find_all("tr", {"class": re.compile(r"(even)?(odd)?")})

# A list named for each row of data and another list to hold the column name
# I am sure a better way to do this exists
table = {"datePosted": [], "effectiveDate": [], "transactionAmount": [], "balance": [], "principal": [], "interest": [], "lateFees": [], "miscFees": []}
tableLabels = ["datePosted", "effectiveDate", "transactionAmount", "balance", "principal", "interest", "lateFees", "miscFees"]
numColumns = len(tableLabels)

for tr in table_rows:
    td = tr.find_all("td")

    count = 0
    for d in td:
        d = str(d.text)

        # Strips the excess characters from the numbers
        replace = ['$', '(', ')', "--", ',']

        for r in replace:
            if r in d:
                if r == "--":
                    d = str(0)
                else:
                    d = d.replace(r, '')

        if "." in d:
            d = float(d)

        # if "--" == d:
        #     d = float(0)
        # if "$" in d:
        #     d = d.replace('$', '')
        # if "," in d:
        #     d = d.replace(',', '')
        # if "(" in d:
        #     d = d.replace('(', '')
        # if ")" in d:
        #     d = d.replace(')', '')
        # if "." in d:
        #     d = float(d)

        table[tableLabels[count]].append(d)
        count += 1

numEntries = len(table[tableLabels[0]])
print("\n==================" + str(numEntries) + "===================================\n")

# Prints the table column labels
for header in tableLabels:
    print("{0:^19}".format(header), end = "")
print('\n')

# Prints the loan data
for i in range(0, numEntries):
    for j in range(0, numColumns):
        print("{0:^19}".format(table[tableLabels[j]][i]), end = '')
    print('\n')

# The important stats
lateFees = sum(float(value) for value in table[tableLabels[6]])
miscFees = sum(float(value) for value in table[tableLabels[7]])
fees = lateFees + miscFees
totalInterest = sum(float(value) for value in table[tableLabels[5]])
totalPrincipal = sum(float(value) for value in table[tableLabels[4]])
totalPaid = sum(float(value) for value in table[tableLabels[2]]) + fees
amountPaidOff = float(table[tableLabels[3]][-1]) - float(table[tableLabels[3]][0])

print("Extra fees: [${:.2f}] --> (Late fees: ${:.2f} + Misc fees: ${:.2f})".format(fees, lateFees, miscFees))
print("You have paid [${:,.2f}] to Santander overall.".format(totalPaid))
print("But your loan has only decreased by [${:,.2f}].".format(amountPaidOff))
print("This means you have paid [${:,.2f}] in interest.".format(totalInterest))
print("This is not counting late fees etc. so expect a ~$150 discrepancy.")
print("If these numbers hurt you, make plans to change it A.S.A.P.")
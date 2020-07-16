import requests, bs4 as bs, re, sys

if len(sys.argv) >= 1:
    htmlData = open(str(sys.argv[1]), 'r')
else:
    htmlData = open("/Users/X/07-15-20_4-30AM.html", 'r')

contents = htmlData.read()
soup = bs.BeautifulSoup(contents, "html.parser")

# For the strike
strikePlays = soup.find_all("a", {"class": "chatlog__embed-title-link"})
# For the strike details
strikeDetails = soup.find_all("div", {"class": "chatlog__embed-description"})

for item in strikePlays:
    print(item.div.text)

for item in strikeDetails:
    print(item.div.text)

# Create output file to store data
# Add data to excel sheet if it doesnt already exist.


# The parent branch that holds both the strike abd details branch
# <div id="mess-\d16>...
# Hold the Strike Play info
# <a class="chatlog__embed-title-link"><div class="markdown">.text
#   ($name 2020-07-21 P $11)
# Holds the strike details info
# <div class="chatlog__embed-description"><div class="markdown>.text
#   (️ ignore whitespace here
#
# Bid: $1.41
# Ask: $1.63
# Interest: 5
# Volume: 550
# IV: 87.61%
# % Diff: -23.66%
# Purchase: $17.03)

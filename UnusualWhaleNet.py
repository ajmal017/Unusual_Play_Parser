import requests, bs4 as bs, re

htmlData = open("/Users/X/07-15-20_4-30AM.html", 'r')
contents = htmlData.read()
soup = bs.BeautifulSoup(contents, "html.parser")

# <div id="mess-\d16>...

# <a class="chatlog__embed-title-link"><div class="markdown">.text
# $name 2020-07-21 P $11
# Prints the strike
refinedPlays = soup.find_all("a", {"class": "chatlog__embed-title-link"})

# <div class="chatlog__embed-description"><div class="markdown>.text
#   (
#     Bid: $1.41
#     Ask: $1.63
#     Interest: 5
#     Volume: 550
#     IV: 87.61%
#     % Diff: -23.66%
#     Purchase: $17.03)
# Prints the Bid, Ask, Interest, Volume, IV, PercentageChange and StockPrice
refinedPlays = soup.find_all("div", {"class": "chatlog__embed-description"})
for item in refinedPlays:
    print(item.div.text)

for item in refinedPlays:
    print(item.text)

# <div id="mess-\d16>...
# <a class="chatlog__embed-title-link"><div class="markdown">.text
#   ($name 2020-07-21 P $11)
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

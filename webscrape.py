#Importing Libraries
from bs4 import BeautifulSoup
import requests

#Get website link
website = "https://researchops.web.illinois.edu/?page=1"

#request info from site
result = requests.get(website)

#Store info of results in a text manner
content = result.text

#Parse code
soup = BeautifulSoup(content, "lxml")
#print(soup.prettify())

#Get element of website
box = soup.find('span', class_ = 'field field--name-title field--type-string field--label-hidden')
title = box.get_text()
print(title)
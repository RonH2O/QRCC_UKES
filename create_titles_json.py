#-----------------------------------------------------------------------------------------------#
# This script fetches all the title and href for all the songs on the ozbcoz website and stores #
# the details in a dictionary which is dumped into a JSON file. The intent is that the JSON     #
# file will act as a master list of all song titles that can be used subsequently to fetch the  #
# lyrics for any song.                                                                          #
#                                                                                               #
# The JSON file name is hard coded as titles_dict.json in the same folder as the script. The    #
# script may have to run from time to time because new songs may be added to Jim's Songbook     #
# that may be part of the QRCC song collection.                                                 #
#-----------------------------------------------------------------------------------------------#
import requests
from bs4 import BeautifulSoup as bs

import re
import json

def remove_key_suffix(title):
    # Match keys like [C], [G#m], [Fmaj7], [Bbmin], etc.
    return re.sub(r'\s*\[[A-G][#b]?(m|maj|min|dim|aug|sus\d?|add\d?|7|9|11|13)?\d*\]$', '', title)
def clean_title(raw_title):
    # Remove the key in square brackets at the end if present
    title = remove_key_suffix(raw_title)
    # Remove any parenthetical phrases at the beginning or middle of the title
    title = re.sub(r'\(.*?\)', '', title)
    # Remove characters after hyphens in the title
    i = title.find(" - ")
    if i > -1:
        title = title[:i]
    # Strip leading/trailing whitespace and return the 'cleaned' title
    return title.strip()

def clean_href(raw_href):
    # extract the song number from the href
    if raw_href.endswith(',soprano'):
        return raw_href[12:][:-len('.soprano')]

url = 'https://ozbcoz.com/Songs/'        # url of Jim's list of songs
response = requests.get(url, timeout=10) # fetch the list of songs
response.raise_for_status()              # raise any http error
html_content = response.content          # obtain the html content

# Assuming 'html_content' contains your full HTTP response
soup = bs(html_content, 'html.parser')

# Find the <ul> with id="quad"
quad_list = soup.find('ul', id='quad')

# Extract all <a> tags within <li> elements and get their 'title' attributes
titles = []
if quad_list:
    for li in quad_list.find_all('li'):
        a_tag = li.find('a')
        if a_tag and a_tag.has_attr('title'):
            titles.append((clean_title(a_tag['title']),clean_href(a_tag['href'])))

# Output or process the titles
titles_dict = {}
titles_dict.update(titles)
# Save the dictionary to a JSON file
with open("titles_dict.json", "w") as f:
    json.dump(titles_dict, f, indent=4) # indent for pretty-printing
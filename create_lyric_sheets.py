#------------------------------------------------------------------------------------------------------#
# Given a playlist, download lyric sheets for any songs in the playlist that are NOT found in the      #
# lyrics folder. In this way the collection of lyric sheets can be gradually built up.                 #
#                                                                                                      #
# The program is called as a sub process by the CLI application qrcc_ukes.py when the command          #
# create-lyric-sheets is issued.                                                                       #
#                                                                                                      #
# The program assumes the existence of several files whose name are hard-coded. These are:             #
# (1) qrcc_titles_dict.json - this is a file (dictionary) of all songs that are in the QRCC catalogue  #
#     together with the Jim's songbook id. This allows the song lyrics to be downloaded from the ozbcoz#
#     website.                                                                                         #
# (2) playlist.txt - this is the list of songs required for a singalong. The lyrics for any song in the#
#     list that doesn't currently exist in the downloaded_lyrics folder will be fetched from the ozbcoz#
#     website (using qrcc_titles_dict.json)                                                            #
#------------------------------------------------------------------------------------------------------#  

import json
import os
import requests
import sys

#-----------#
# Functions #
#-----------#
def create_uri(id):
    url = f"https://ozbcoz.com/Songs/downloadpdf.php?ID={id},lyrics"
    return url

#------------------#
# Global Constants #
#------------------#
qrcc_titles = "qrcc_titles_dict.json"  # dictionary stored as a json file that contains all the titles
                                       # in the QRCC Ukulele songbook that match Jim's Songbook. Each entry
                                       # is a key, value pair where the key is the song name and the value
                                       # is the ID of the song on the ozboz server
output_dir  = "downloaded_lyrics"      # name of folder to store the lyric sheets 

#--------------------------#
# Main processing workflow # 
#--------------------------#

song_list = sys.argv[1]

# Load the dictionary from the JSON file
with open(qrcc_titles, "r") as f:
    titles_dict = json.load(f)

# Create a list of the songs in the playlist
with open(song_list, "r") as f:
    playlist_titles = f.readlines()

# check for any songs that are not in the dictionary - these will need to be downloaded by a separate
# process (perhaps manual?)
found_titles = []
for title in playlist_titles:
    title = title.strip()
    if title in titles_dict:
        found_titles.append((title, titles_dict[title]))
    else:
        print(f"{title} NOT found in the dictionary") 

# fetch the lyric sheets for all the playlist songs that do not currently in the lyrics folder
output_dir = 'downloaded_lyrics' 
os.makedirs(output_dir, exist_ok=True)
for filename, id in found_titles:
    try:
        filename += ".pdf"
        filepath = os.path.join(output_dir, filename) 
        if not os.path.isfile(filepath):
            uri = create_uri(id)        
            print(f"Downloading: {filename}.pdf - {uri}")
            response = requests.get(uri, timeout=10)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(response.content)
                print(f"Saved: {filepath}")    
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {UserWarning}: {e}")   
              
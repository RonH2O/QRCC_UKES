#-------------------------------------------------------------------------------------------#
# This script creates a JSON file containing the titles in the QRCC Song Collection and the #
# number in Jim's Songbook. This will allow the lyric sheet for any QRCC Song to be created #
# subsequently - provided the song is in Jim's Songbook. QRCC songs that are not in Jim's   #
# songbook are listed in an exception file so the lyrics can be downloaded manually. It is  #
# expected that most QRCC songs will be contained in Jim's collection.                      #
#                                                                                           #
# The QRCC Song Collection is contained in a hardcoded file qrcc_titles.txt which is taken  #
# from the QRCC Ukulele database. This file is assumed to be in the script folder.          #
# The JSON file is hardcoded as qrcc_titles_dict.json in the same folder as the script. The #
# list of unmatched songs is written to a file with hardcoded name qrcc_titles_missing.txt  #
# in the same folder as the script. The SQL to create the list of QRCC songs and this script#
# will need to be re-run as required to ensure the files are up to date.                    #
#-------------------------------------------------------------------------------------------#   
import json

# Load the dictionary from the JSON file
with open("titles_dict.json", "r") as f:
    titles_dict = json.load(f)

# Load the QRCC database titles into a list
with open('qrcc_titles.txt', 'r') as f:
    qrcc_titles = [title.strip() for title in f]

qrcc_titles_dict = {}
qrcc_titles_missing = []
# iterate over qrcc_titles
for title in qrcc_titles:
    if title in titles_dict:
        qrcc_titles_dict[title] = titles_dict[title]
    else:
        qrcc_titles_missing.append(title)    

# write qrcc_titles_dict to a json file
with open("qrcc_titles_dict.json", "w") as f:
    json.dump(qrcc_titles_dict, f, indent=4)

# write qrcc_titles_missing to a txt file
with open("qrcc_titles_missing.txt", "w") as f:
    f.writelines([f"{title}\n" for title in qrcc_titles_missing])     

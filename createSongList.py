#-------------------------------------------------------------------#
# Obtain a list of song titles and their URI from the QRCC Database #
#-------------------------------------------------------------------#

import database as db
import csv

DBDNAME = 'qrcc_ukes.db'
FILE_NAME = 'songs.csv'

#---------------------------------------------#
# select all song titles and song-sheet links #
#---------------------------------------------#
queryText = '''SELECT title, songLink FROM Songs ORDER BY title ASC'''
queryValue = ()
songs = db.select(DBDNAME, queryText, queryValue)

#-----------------------------------------------#
# write the song titles and links to a CSV file #
#-----------------------------------------------#
with open(FILE_NAME, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter='#')
    for song in songs:
        writer.writerow(song)

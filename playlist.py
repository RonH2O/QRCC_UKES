#--------------------------------------------------------------------------#
# Generate a random set of songs (playlist) from the songs in the database #
#--------------------------------------------------------------------------#

import random
import database as db
import sys

def createIncludeExcludeList(filePath):
    try:
        with open(filePath,'r') as file:
            lines = file.readlines()
        return [line.strip() for line in lines]     
    except:
        return []    

#-------------------#
# set database name #
#-------------------#
DBDNAME = 'qrcc_ukes.db'

#----------------------------------------------------------#
# Ask the user to choose the set of songs ([A-L] or [M-Z]) #
#----------------------------------------------------------#
songSet = int(input('''
Enter required set:
       1 for A-L (inclusive)
       2 for M-Z (inclusive)
===> '''))
if songSet == 1:
    cond = '<'
else:
    cond = '>='    

#----------------------------------------------#
# Obtain the available songs from the database #
#----------------------------------------------#
queryText = f'''
SELECT
   title
FROM
   Songs
WHERE
   title {cond} ?      
'''
queryValues = 'M'
songList = db.select(DBDNAME, queryText, queryValues)
songList = [s[0] for s in songList]  # convert list of tuples to list of strings

#------------------------------------------------------------------------------#
# Ask the user for a file of song titles that MUST be included in the playlist #
#------------------------------------------------------------------------------#
includedFile = input('''
(optional) Enter the name of a file holding song titles that MUST be included in the playlist
===>  ''')
includeList = createIncludeExcludeList(includedFile)

#----------------------------------------------------------------------------------#
# Ask the user for a file of song titles that MUST NOT be included in the playlist #
#----------------------------------------------------------------------------------#
excludedFile = input('''
(optional) Enter the name of a file holding song titles that MUST NOT be included in the playlist
===>  ''')
excludeList = createIncludeExcludeList(excludedFile)
songList = list(set(songList) - set(excludeList))

#---------------------------------------------------------------#
# Ask the user for the number of songs required in the playlist #
#---------------------------------------------------------------#
songCount = int( input('''
Enter number of songs required in playlist
===> '''))

#--------------------------------------#
# Generate a random set of song titles #
#--------------------------------------#
if len(includeList) <= songCount:
    playList = includeList + random.sample(songList, songCount - len(includeList))
else:
    playList = random.sample(songList, songCount)  
playList = sorted(playList)

for i in range(0,len(playList)):
    print(f"{(str(i+1)+':').ljust(5)} {playList[i]}")

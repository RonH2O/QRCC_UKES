#------------------------------------------------------------------------------------------------------#
# Create a songbook by collecting a set of songs (PDF files) in a folder, adding page numbers, a table #
# of contents and adding links to make the TOC 'clickable'.                                            #
#                                                                                                      #
# The program is called as a sub process by the CLI application qrcc_ukes.py when the command          #
# create-songbook is issued. This program, in turn, invokes other python scripts as part of the        #
# workflow to create the songbook.                                                                     #
#------------------------------------------------------------------------------------------------------#                                                                            

import subprocess
import json 
import sys

#--------------------------------------------------#
# Required data to be supplied to run the workflow #
#--------------------------------------------------#

#
## Names of scripts that make up the workflow
## ------------------------------------------
#
CREATE_TITLE_PAGE       = 'create_title_page.py'       # create a title page for the songbook
CREATE_INTERIM_SONGBOOK = 'create_interim_songbook.py' # create interim (temp) songbook
CREATE_FINAL_SONGBOOK   = 'create_final_songbook.py'   # create final target songbook 

#target_folder = 'C:/Users/rjbyw/PythonProjects/tkinterGUI/QRCC_Ukes_Dev/' # folder to contain completed songbook



#-----------------#
# Local functions #
#-----------------#
def getTitleFileName():
    titleFile = input("Please enter name of (PDF) file for title page: ")
    if titleFile.endswith('.pdf'):
        return titleFile
    else:
        return titleFile + '.pdf'
    
#--------------------------#
# Main processing workflow # 
#--------------------------#
    
titleFile = 'title_page_temp.pdf'     # set name of title page PDF - deleted once songbook created
#json_data = json.dumps(extra_songs)   # create the title page file
bookType = sys.argv[1]

#
# create the title page
# ---------------------
#
subprocess.run(['python', CREATE_TITLE_PAGE, bookType, titleFile])

#
# download any new songs required
# -------------------------------
#
# subprocess.run(['python',
#                 FETCH_NEW_SONGS, 
#                 'SPECIAL',
#                 json_data])

#
## create the temp songbook - tile page, TOC and songs
## ---------------------------------------------------
#
subprocess.run(['python', CREATE_INTERIM_SONGBOOK, bookType])

#
## create the final songbook with a clickable TOC
## ----------------------------------------------
#
subprocess.run(['python',
                CREATE_FINAL_SONGBOOK,
                #target_folder,
                bookType])

               
print('All Done ......')
#---------------------------------------------------------------------------------------#
# Common functions that can be called from other Python code as part of the application #
# to support the QRCC Ukulele Group                                                     #
#---------------------------------------------------------------------------------------#
import os
import glob
import shutil

def copySongs(songs):
    #------------------------------------------------------------------------------#
    # remove all the songs from the special downloads folder and replace them with #
    # the songs in the play list supplied                                          #
    #------------------------------------------------------------------------------#
    downloadsFolder = 'C:/Users/rjbyw/PythonProjects/QRCC_UKES/downloaded_pdfs/'
    specialDownloadsFolder = 'C:/Users/rjbyw/PythonProjects/QRCC_UKES/downloaded_pdfs_special/'
    #
    ## delete all the PDF files in the special downloads folder
    ## --------------------------------------------------------
    #
    files = glob.glob(f'{specialDownloadsFolder}*.pdf')  
    for f in files:
        os.remove(f)             
    #
    ## copy the songs to the special downloads folder
    ## ----------------------------------------------
    #
    for song in songs:
        if not song.endswith('.pdf'):
           song += '.pdf'
        sourcePath = os.path.join(downloadsFolder, song)
        destPath = os.path.join(specialDownloadsFolder, song)
        shutil.copy(sourcePath, destPath)
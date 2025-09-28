#---------------------------------------------------------------------------------------------------------------#
# This script uses the pymupdf package to add links to the QRCC Songbook to make Table Of Contents 'clickable'. #
# That is, clicking on a song in the Table Of Contents (TOC) will navigate to the song. Also, clicking on the   #
# page number at the bottom of the FIRST page of the song will navigate back to the TOC.                        #
#---------------------------------------------------------------------------------------------------------------#  

#-------------------------------#
# Import the required libraries #
#-------------------------------#
import pymupdf
import sys
import os

def getTOCPages(doc):
#-------------------------------------------------------------------#
# Function to return the text of the TOC entries                    #
# Receives: a PDF document object representing the songbook         #
# Returns : a list of lists where each entry in the outer list is a #
#           list of the TOC entries in the corresponding TOC page   #
#-------------------------------------------------------------------#                         
    tocString = '...... '
    pageCount = 1
    tocPages = []
    while True:
        page = doc.load_page(pageCount)
        txt = page.get_text()
        if tocString in txt:
            tocPage = page.get_text().split('\n')
            del(tocPage[-1])  # remove the last trailing newline character
            if pageCount == 1:
                tocPage = tocPage[1:]
            tocPages.append(tocPage)    
            pageCount += 1
        else:
            return tocPages    
        
def addTocLinks(tocContents, tocPage, tocPageCount):
    for tocEntry in tocContents:
#-------------------------------------------------------------------#
# Function to add links FROM a TOC page TO the song pages of the    #
# songs in the TOC page and a link FROM the song page back to the   #
# first page of the TOC.                                            #
# Receives: a list of TOC entries for a TOC page                    #
#         : a page object for the TOC page                          #
#         : the number of pages that make up the TOC                #
# Returns : None (the links are added to the GLOBAL PDF)            #
#-------------------------------------------------------------------#  
        targetPage = int(tocEntry.rpartition("... ")[2])
        addTocLink(tocEntry, tocPage, targetPage, tocPageCount)   
    return None    

def addTocLink(tocEntry, tocPage, targetPage, tocPageCount):
#-------------------------------------------------------------------#
# Function to a link FROM an TOC entry TO the song page and a link  #
# FROM the song page back TO the Table of Contents                  #
# Receives: a line (string) from the TOC                            #
#         : a page object for the TOC page                          #
#         : the page number of the song page                        #
#         : the number of pages that make up the TOC                #
# Returns : None (the requested links are added to the PDF)         #
#-------------------------------------------------------------------#      
    recList = tocPage.search_for(tocEntry)
    bbox = recList[0]
    pageNo = targetPage + tocPageCount
    # insert a link FROM the TOC entry TO the song page
    page.insert_link( {
        "kind" : pymupdf.LINK_GOTO,
        "page" : pageNo,
        "from" : bbox,
        "to"   : pymupdf.Point(0,0)
    })
    # insert a link FROM the song page TO the TOC
    songPage = doc.load_page(pageNo)
    bbox = songPage.search_for("Page " + str(targetPage))[0]
    songPage.insert_link( {
        "kind" : pymupdf.LINK_GOTO,
        "page" : 1,
        "from" : bbox,
        "to"   : pymupdf.Point(0,0)
    })  
    return None    

def deleteTempFile(file):
    print(f"Deleting temporary file: {file}")
    try:
        os.remove(file)
        print(f"File: {file} deleted")
    except FileNotFoundError:
        print(f"File: {file} not found - cannot be deleted")
    except Exception as e:
        print(f"Unexpected Error: {e}")   

#------------------#
# Global Constants #
#------------------#
pdfFile = "QRCC_Songbook_temp.pdf"                                 # name of songbook PDF without links (input)

if sys.argv[1] == 'SPECIAL':                                       
    clickable = 'QRCC_Songbook_Special.pdf'                        # name of songbook PDF with links (output)                         
else:
    clickable = 'QRCC_Songbook.pdf'                                # name of songbook PDF with links (output)

#---------------------#
# Mainline Processing #
#---------------------#

doc = pymupdf.open(pdfFile)                                # open the input songbook
tocPages = getTOCPages(doc)                                # obtain the TOC pages as a list

#
## iterate over the TOC pages and for each page add links to/from the page entries
## -------------------------------------------------------------------------------
#
for tocPageNo in range(0, len(tocPages)):
    page = doc.load_page(tocPageNo + 1)
    addTocLinks(tocPages[tocPageNo], page, len(tocPages))

#
## save and close the (output) songbook
## ------------------------------------
doc.save(clickable)   
doc.close()                                                # save the output songbook    

#
## delete the interim (input) songbook
## -----------------------------------
#
deleteTempFile(pdfFile)




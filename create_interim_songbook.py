#-----------------------------------------------------------------------------------#
# This script creates a songbook that consists of a title page, a table of contents #
# and a set of songs. It is intermin in that an entry in the table of contents is   #
# not 'clickable'. This is added in a separate script.                              #
#-----------------------------------------------------------------------------------#

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
import sys

#-----------#
# Functions #
#-----------#
def createTocEntry(title, page):
   titleLen = len(title)
   pageLen = len(str(page))
   LINE_LEN = 60
   return f"{title} {'.'*(LINE_LEN-2-pageLen-titleLen)} {str(page)}"

def createBaseSongBook(folder, songpdf, playlist):
    #------------------------------------------------------------------------------#
    # createBaseSongBook(folder, pdf) - create a PDF songbook with no page numbers #
    # folder - the name of the folder containing the individual PDF songs          #
    # songpdf - name of the (unnumbered) songbook PDF                              # 
    #------------------------------------------------------------------------------#
    writer = PdfWriter()
    toc_entries = []
    current_page = 1  # PDF page numbers start at 1
    if len(playlist) == 0:
        playlist = sorted(os.listdir(folder))
    for filename in playlist:    
    #for filename in sorted(os.listdir(folder)):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder, filename)
            try:
                reader = PdfReader(file_path)
                num_pages = len(reader.pages)

                # Extract song title from filename (you can improve this with metadata later)
                title = os.path.splitext(filename)[0].replace("_", " ")
                toc_entries.append((title, current_page))

                for page in reader.pages:
                    writer.add_page(page)

                current_page += num_pages
                print(f"✓ Added {title}: starts on page {toc_entries[-1][1]}")

            except Exception as e:
                print(f"⚠️ Failed to add {filename}: {e}")
    # Save merged PDF
    with open(songpdf, "wb") as out_file:
        writer.write(out_file)  
    return toc_entries

def createTOC(tocEntries, tocFile):
    #---------------------------------------------------------------------------------------------------------#
    # Create a file (PDF) holding the table of contents for the songbook. This file will used when assembling #
    # the completed song book                                                                                 #
    #---------------------------------------------------------------------------------------------------------#
    # define empty list to hold the TOC contents - this will be returned to be saved as a file and used to
    # create a clickable table of contents (hopefully)
    tocContents = []
    tocPageCount = 0

    c = canvas.Canvas(tocFile, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 50, "Table of Contents")

    # Content styling
    c.setFont("Courier-BoldOblique", 12)
    top_margin = 80
    line_height = 16

    entriesPerPage = int((height - top_margin - 50) / line_height)

    for page_num in range(0, len(toc_entries), entriesPerPage):
            for i, (title, page_num) in enumerate(toc_entries[page_num:page_num + entriesPerPage]):
                y = height - top_margin - i * line_height
                entry = f"{title}"
                page_str = f"{page_num}"
                c.setFont("Courier-BoldOblique", 12)
                # Dot leaders logic
                dots = '.' * (60 - len(entry) - len(page_str))
                line = f"{entry} {dots} {page_str}"
                c.drawString(50, y, line)
                tocContents.append(line)
            c.showPage()      #start new page
            tocPageCount += 1

    c.save() 
    tocContents.insert(0, str(tocPageCount))
    return tocContents  

def addPageNumbers(input_pdf, output_pdf):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages, start=1):
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.drawString(450, 10, "Page " + str(i))  # Position and page number
        c.save()
        packet.seek(0)

        overlay = PdfReader(packet).pages[0]
        page.merge_page(overlay)
        writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f)

def prependFrontMatter(main_pdf, frontmatter_pdf, output_pdf):
    writer = PdfWriter()

    # Read and add all pages from the frontmatter
    front_reader = PdfReader(frontmatter_pdf)
    for page in front_reader.pages:
        writer.add_page(page)

    # Read and add all pages from the main songbook
    main_reader = PdfReader(main_pdf)
    for page in main_reader.pages:
        writer.add_page(page)

    # Save the combined PDF
    with open(output_pdf, "wb") as f:
        writer.write(f)
    
def deleteTempFile(file):
    print(f"Deleting temporary file: {file}")
    try:
        os.remove(file)
        print(f"File: {file} deleted")
    except FileNotFoundError:
        print(f"File: {file} not found - cannot be deleted")
    except Exception as e:
        print(f"Unexpected Error: {e}")    

def createPlaylist(playlistFile):
    #---------------------------------------------------------------------------#
    # create a playlist of song titles from the file containing the song titles #
    #---------------------------------------------------------------------------#
    playlist = []
    with open(playlistFile) as file:
        for song in file:
            playlist.append(song.rstrip() + ".pdf")
    return playlist                            
      
#------------------#
# Global Constants #
#------------------#
pdf_folder       = "downloaded_pdfs"            # folder containing individual song PDFs
baseSongBook     = "baseSongBook.pdf"           # songbook name (no page numbers) - will be deleted when songbook assembled
tocPage          = "toc_page.pdf"               # name of TOC PDF - will be deleted when songbook assembled
numberedSongBook = "numberedSongBook.pdf"       # name of songbook with page numbers - will be deleted when songbook assembled
songBookWithTOC  = "songBookWithTOC.pdf"        # name of numbered songbook with a table of contents - will be deleted when songbook assembled
songBook         = "QRCC_Songbook_temp.pdf"     # name of the assembled (complete) songbook - will be deleted when clickable songbook assembled
titlePage        = "title_page_temp.pdf"        # name of the title page PDF

#--------------------------#
# Main processing workflow #
#--------------------------#

#
## set the correct directory that holds the song PDFs to be included in the song book
## ----------------------------------------------------------------------------------
#
if sys.argv[1] == 'SPECIAL':
    pdf_folder = 'downloaded_pdfs_special'
    playlist = createPlaylist(sys.argv[2])
else:
    pdf_folder = 'downloaded_pdfs' 
    playlist = []   

#
## Merge the song PDFs to create a 'super' PDF songbook (no page numbers)
## ----------------------------------------------------------------------
#
toc_entries = createBaseSongBook(pdf_folder, baseSongBook, playlist)

#
## Create a table of contents PDF from the entries just returned and save it as a text file
## ----------------------------------------------------------------------------------------
#
tocContents = createTOC(toc_entries, tocPage)
# with open("toc_summary.txt", "w") as file:
#     for item in tocContents:
#         file.write(item + '\n')

#
## Add page numbers to the songbook
## --------------------------------
#
addPageNumbers(baseSongBook, numberedSongBook)

#
## Prepend the song book with the Table Of Contents
## ------------------------------------------------
#
prependFrontMatter(numberedSongBook, tocPage, songBookWithTOC)

#
## Prepend the song book with the title page
## -----------------------------------------
#
prependFrontMatter(songBookWithTOC, titlePage, songBook)

#
## Cleanup by deleting the 'temporary' files
## -----------------------------------------
#
deleteTempFile(baseSongBook)
deleteTempFile(tocPage)
deleteTempFile(numberedSongBook)
deleteTempFile(songBookWithTOC)
deleteTempFile(titlePage)


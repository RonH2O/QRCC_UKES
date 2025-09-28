from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime
import sys

# def getTitleFileName():
#     titleFile = input("Please enter name of file for title page (omit .pdf): ")
#     return titleFile + '.pdf'

def createCanvas(titlePDF):
    c = canvas.Canvas(titlePDF, pagesize=A4)
    c.setFont("Helvetica-Bold", 24)
    width, height = A4
    return (c, width, height)

def getTitleText():
    titleText = input("Please enter text to be displayed as the Title: ")
    return titleText

def createTitlePage(titleText, c):
    dateToday = datetime.date.today()
    revisionDate = dateToday.strftime("%A %B %d %Y")  
    x = pageWidth / 2
    y = pageHeight / 2 + 20  
    c.drawCentredString(x, y, titleText)
    y = pageHeight / 2 - 20
    date_text = f"Last Updated: {revisionDate}"
    c.drawCentredString(x, y, date_text)
    c.showPage()
    c.save()

#
## obtain file name for title page
## -------------------------------
#
# titlePDF = getTitleFileName()

# 
## create canvas for page
## ----------------------
#
c, pageWidth, pageHeight = createCanvas(sys.argv[2])

#
## get the title text
## ------------------
#
titleText = getTitleText()

#
## create the title page (text + revision date)
## --------------------------------------------
#
createTitlePage(titleText, c)

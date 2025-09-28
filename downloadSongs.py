#-----------------------------------------------------------------------------------#
# Script used to initially download a PDF for each song stored in the QRCC database #
#-----------------------------------------------------------------------------------#

import csv
import requests
from urllib.parse import urlparse
import os

def createSongUrls(songList):
    pdf_urls = [] 
    with open(songList,'r') as file:
        csvreader = csv.reader(file, delimiter="#")
        #header = next(csvreader)
        for record in csvreader:
            addPdfUri(pdf_urls, record[0], record[1])    
    return pdf_urls        

def addPdfUri(pdf_urls, songTitle, songUri):
    pdfUri = derivePdfUri(songTitle, songUri)
    if pdfUri != "unknown":
       pdf_urls.append((songTitle, pdfUri))
    else:
       print(f"Cannot derive pdf uri for {songTitle}")    

def derivePdfUri(title, uri):
    uri = uri.strip()
    if uri.startswith('https://cloud.bytown'):
        uri += "/download"
    elif uri.startswith('https://www.ozbcoz'):
        uri = uri.replace("song.php", "downloadpdf.php")
    elif uri.startswith('https://ozbcoz'):
        uri = uri.replace("song.php", "downloadpdf.php")
    elif uri.endswith('.pdf'):
        uri = uri
    else:
        uri =  'unknown'
    return uri    
    

# Create a list where each entry is a tuple of a song title and a uri that can be used to download the song's pdf
#songList = 'song_links.csv'
songList = 'songs.csv'
song_urls = createSongUrls(songList)

#song_urls = song_urls[20:]
#song_urls = song_urls[:20]

# Create a folder to save PDFs
output_dir = "downloaded_pdfs"
os.makedirs(output_dir, exist_ok=True)

# Iterate over the list and attempt to download the pdf for each song
for song_uri in song_urls:
    try:
        title = song_uri[0]
        url = song_uri[1]
        print(f"Downloading: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad HTTP status

        # Derive filename 
        #filename = os.path.basename(urlparse(url).path)
        filename = title + '.pdf'
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Saved: {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {title} {url}: {e}")





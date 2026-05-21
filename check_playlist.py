# ------------------------------------------------------------------------------------------------------#
# Given a list of songs (playlist) - correct the title of each song and check if it already downloaded #
# ------------------------------------------------------------------------------------------------------#
import os
import string


def adjustSonglist(file):
    # -----------------------------------#
    # correct any typos in the songlist #
    # -----------------------------------#
    with open(file, "r", encoding="utf-8") as f:
        songs = f.read().splitlines()
    songs = [adjustSong(song) for song in songs]
    with open(file, "w", encoding="utf-8") as f:
        for song in songs:
            f.write(f"{song}\n")
    return songs


def adjustSong(song):
    return string.capwords(song.replace("’", "'"))


def isSongDownloaded(song):
    pdfFolder = "C:/Users/rjbyw/PythonProjects/QRCC_UKES/downloaded_pdfs/"
    song = song + ".pdf"
    file = os.path.join(pdfFolder, song)
    if os.path.exists(file):
        return True
    else:
        return False


playlist = input("Please enter the name of the playlist file: ")
songs = adjustSonglist(playlist)
for song in songs:
    if isSongDownloaded(song):
        print(f"Song: {song} is in the downloads folder")
    else:
        print(f"Song: {song} is NOT in the downloads folder")

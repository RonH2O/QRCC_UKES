import sys
import subprocess
import os
import glob
import shutil
from datetime import datetime
from enum import Enum
import requests

import typer
from typing_extensions import Annotated
from rich import print

import database as db

DBNAME = 'qrcc_ukes.db'

class SingalongType(str, Enum):
    qrcc = "qrcc"
    qrccChristmas = "qrccChristmas"
    external = "external"

class SongbookType(str, Enum):
    mini = "mini"
    full = "full"    

app = typer.Typer()

#---------------#
# CLI Commands  #
#---------------#
@app.command()
def add_song(
    title: Annotated[str, typer.Argument(help='Song Title')],
    artist: Annotated[str,typer.Argument(help='Name Of Artist')],
    key: Annotated[str,typer.Argument(help="Key Of The Song")],
    song_uri: Annotated[str,typer.Option(help="Link To Songsheet", rich_help_panel="Can Be Added Now Or Later")]='',
    video_uri: Annotated[str,typer.Option(help="YouTube Link", rich_help_panel="Can Be Added Now Or Later")]=''
):
    '''
    Add a song to the database
    '''
    result = addSong(title, artist, key, song_uri, video_uri)
    if result is None:
        print(f"[bold red]Severe SQL Error![/bold red]")
    elif result == 'SQL_DUPLICATE':
        print(f"[red]Song - Title: {title} Artist: {artist} Key: {key} already exists in the Database[/red]")   
    else:
        print(f"[green]Song - Title: {title} Artist: {artist} Key: {key} added to Database")     
    
@app.command()
def add_songsheet(
    title: Annotated[str, typer.Argument(help='Song Title')],
    key: Annotated[str,typer.Argument(help="Key Of The Song")],
    song_uri: Annotated[str,typer.Argument(help="Link To Songsheet")]   
):    
    '''
    Add a link to a song sheet (chords + lyrics) for the song
    '''
    valid, err =  validateSongSheetReq(title, key)
    if not valid:
        if err == 'NO-SONG':
            print(f"[red]Song - Title: {title} not found in the Database[/red]")
            return
        elif err == 'AMBIGUOUS':
            print(f"[red]Song - Title: {title} occurs more than once in Database. A song key must be provided[/red]")
            return
        elif err == 'NO-KEY':
            print(f"[red]Song - Title: {title} key: {key} not found in Database[/red]")
            return
    result = addSongSheet(title, song_uri, key)    
    if result is None:
        print(f"[bold red]Severe SQL Error![/bold red]")
    else:
        print(f"[green]Song- Title: {title} now has a song sheet link: {song_uri} in the Database")               
    
@app.command()
def add_video(
    title: Annotated[str,typer.Argument(help='Song Title')],
    video_uri: Annotated[str,typer.Argument(help='YouTube link for song')]
):
    '''
    Add a link to a YouTube video of the song
    '''
    valid, _ = validateVideoReq(title, video_uri)
    if not valid:
        print(f"[red]Song - Title: {title} not found in the Database[/red]")
        return
    result = addVideo(title, video_uri)  
    if result is None:
        print(f"[bold red]Severe SQL Error![/bold red]")
    else:
        print(f"[green]Song- Title: {title} now has a video link: {video_uri} in the Database") 

@app.command()
def add_artist(name: Annotated[str, typer.Argument(help='Name Of Artist')]):
    '''
    Add an artist to the database
    '''
    result = addArtist(name)
    if result == 'SQL_OK':
        print(f"[green]Artist {name} added to Database[/green]")
    elif result == 'SQL_DUPLICATE':
        print(f"[red]Artist: '{name}' already exists in the Database[/red]")
    else:
        print(f"[bold red]Severe SQL Error![/bold red]")   

@app.command()
def add_meetup(date: Annotated[datetime,typer.Argument(formats=["%Y-%m-%d"], help='Date (yyyy-mm-dd) of meetup')],
               chair: Annotated[str,typer.Argument(help='Person choosing the songs for this meetup')],
               song_list: Annotated[str,typer.Option(help="File containing list of songs for meetup")]=None):
    '''
    Add details of a meetup to the database
    '''
    date = str(date)
    date = date.split()[0]
    valid, personId = validateMeetupChair(chair)
    if not valid:
        print(f"[red]Person: {chair} not found in database[/red]")
        return
    valid, songs, errors = validateSonglist(song_list)
    if not valid:
        print(f"[red]The playlist cannot be created because one or more songs are in error:[/red]")
        for song in errors:
            print(f"[dark_orange]{song}[/dark_orange]")   
        return     
    result = addMeetup(date, personId, songs)
    if result == 'SQL_OK':
        print(f"[green]Meetup on {date} with chair {chair} added to database[/green]")
        if len(songs) == 0:
            print("No playlist has been supplied and needs to be added")
    elif result == 'SQL_DUPLICATE':
        print(f"[red]A meetup for date: {date} already exists in the database [/red]")
    else:
         print(f"[bold red]Severe SQL Error![/bold red]")   
    
@app.command()
def attach_playlist_to_meetup(date: Annotated[datetime,typer.Argument(formats=["%Y-%m-%d"], help='Date (yyyy-mm-dd) of meetup')],
               chair: Annotated[str,typer.Argument(help='Person choosing the songs for this meetup')],
               song_list: Annotated[str,typer.Argument(help="File containing list of songs for meetup")]):
    '''
    Add list of songs (playlist) to a meetup in the database
    '''
    date = str(date)
    date = date.split()[0]        
    valid, personId = validateMeetupChair(chair)
    if not valid:
        print(f"[red]Person: {chair} not found in database[/red]")
        return
    valid, result = validateMeetupAttach(date, personId) 
    if not valid:
        if result == 'NO_MEET':
            print(f"[red]Meetup on date:{date} with chair:{chair} not found in database[/red]")
            return
        elif result == 'EXISTING_PLAYLIST':
            print(f"[dark_orange]Meetup on date:{date} with chair:{chair} already has a playlist[dark_orange]")
            return
    valid, songs, errors = validateSonglist(song_list)
    if not valid:
        print(f"[red]The playlist cannot be created because one or more songs are in error:[/red]")
        for song in errors:
            print(f"[dark_orange]{song}[/dark_orange]")   
        return       
    result = addMeetupAttach(date, personId, songs)   
    if result == 'SQL_OK':
        print(f"[green]Playlist added to Meetup on {date} with chair {chair}[/green]")
    else:
         print(f"[bold red]Severe SQL Error![/bold red]")    

@app.command()
def add_singalong(date: Annotated[datetime,typer.Argument(formats=["%Y-%m-%d"], help='Date (yyyy-mm-dd) of singalong')],
               type: Annotated[SingalongType,typer.Argument(help='type - qrcc, qrccChristmas, external')]=SingalongType.qrcc,
               song_list: Annotated[str,typer.Option(help="File containing list of songs for singalong")]=None):
    '''
    Add details of a singalong to the database
    '''
    date = str(date)
    date = date.split()[0]  
    valid, songs, errors = validateSonglist(song_list)
    if not valid:
        print(f"[red]The playlist cannot be created because one or more songs are in error:[/red]")
        for song in errors:
            print(f"[dark_orange]{song}[/dark_orange]")   
        return
    result = addSingalong(date, type, songs)
    if result == 'SQL_OK':
        print(f"[green]Singalong on {date} added to database[/green]")
        if len(songs) == 0:
            print("No playlist has been supplied and needs to be added")
    elif result == 'SQL_DUPLICATE':
        print(f"[red]A singalong for {date} already exists in the database [/red]")
    else:
         print(f"[bold red]Severe SQL Error![/bold red]")     

@app.command()
def attach_playlist_to_singalong(date: Annotated[datetime,typer.Argument(formats=["%Y-%m-%d"], help='Date (yyyy-mm-dd) of singalong')],
               song_list: Annotated[str,typer.Argument(help="File containing list of songs for meetup")]):
    '''
    Add list of songs (playlist) to a singalong in the database
    '''
    date = str(date)
    date = date.split()[0]        
    valid, result = validateSingalongAttach(date) 
    if not valid:
        if result == 'NO_SINGALONG':
            print(f"[red]No singalong for {date} found in database[/red]")
            return
        elif result == 'EXISTING_PLAYLIST':
            print(f"[dark_orange]Singalong on date:{date} already has a playlist[dark_orange]")
            return
    valid, songs, errors = validateSonglist(song_list)
    if not valid:
        print(f"[red]The playlist cannot be created because one or more songs are in error:[/red]")
        for song in errors:
            print(f"[dark_orange]{song}[/dark_orange]")   
        return       
    result = addSingalongAttach(date, songs)   
    if result == 'SQL_OK':
        print(f"[green]Playlist added to singalong on {date}[/green]")
    else:
         print(f"[bold red]Severe SQL Error![/bold red]")   

@app.command()
def create_songbook(type: Annotated[SongbookType, typer.Argument(help='Type of Songbook')]=SongbookType.mini):
    '''
    Create a clickable songbook
    '''    
    if type == 'mini':
        bookType = 'SPECIAL'
    else:
        bookType = 'FULL'    
    subprocess.run(['python', 'create_songbook.py', bookType])                   

#------------------------------------#
# Support functions for the commands #
#------------------------------------#
def addArtist(name):        
    queryText = '''
    INSERT INTO Artists(name) VALUES (?)    
    '''
    queryValue = [
            name]
    queryResult = db.insert(DBNAME, queryText, queryValue)
    return queryResult

def selectArtistId(name):
    queryText = '''SELECT oid FROM Artists WHERE name = ?'''
    queryValue = (name,)
    row = db.select(DBNAME, queryText, queryValue)
    if row is not None:
        return row[0][0]
    else:
        return None

def addSong(title, artist, key, song_URI, video_URI):
    result = addArtist(artist)
    if result is None:
        raise typer.Abort(16)
    artistId = selectArtistId(artist)
    queryText = '''
    INSERT
    INTO Songs (title, artist_id, key, songLink, videoLink)
    VALUES (?, ?, ?, ?, ?)
    ''' 
    queryValues = [title, artistId, key, song_URI, video_URI]
    queryResult = db.insert(DBNAME, queryText, queryValues)
    return queryResult

def validateSongSheetReq(title, key):
    queryText = ''' SELECT key FROM Songs where title = ?'''
    queryValue = (title,)
    row = db.select(DBNAME, queryText, queryValue)
    keys = [k[0] for k in row]
    if len(keys) == 0:
        return (False, 'NO-SONG')
    if len(keys) > 1 and len(key) == 0:
        return(False, 'AMBIGUOUS')
    if len(key) > 0 and key not in keys:
        return(False, 'NO-KEY')
    return('True', 'OK')

def validateVideoReq(title, video_uri):
    queryText = '''SELECT 1 FROM Songs where title = ?'''
    queryValue = (title,)
    row = db.select(DBNAME, queryText, queryValue)
    if len(row) == 0:
        return (False, 'NO-SONG')
    else:
        return (True, 'OK')

def addSongSheet(title, songURI, key):
    if len(key) > 0:
        queryText =  '''
        UPDATE Songs SET songLink = ?
        WHERE title = ? AND key = ? 
        '''
        queryValues = [songURI, title, key]
    else:
        queryText = '''
        UPDATE Songs SET songLink = ?
        WHERE title = ?
        '''   
        queryValues = [songURI, title]
    queryResult = db.update(DBNAME, queryText, queryValues) 
    return queryResult   

def addVideo(title, video_uri):
    queryText = '''
    UPDATE Songs 
    SET videoLink = ?
    WHERE title = ? 
    '''
    queryValues = [video_uri, title]
    queryResult = db.update(DBNAME, queryText, queryValues)
    return queryResult

def validateMeetupChair(person):
    queryText = '''SELECT person_id FROM People where firstName = ?'''
    queryValue=(person,)
    row = db.select(DBNAME, queryText, queryValue)
    if len(row) == 0:
        return (False, 'NO-PERSON')
    personId = row[0][0]
    return (True, personId)

def validateSonglist(file):    
    songs = []
    errors = []
    song_titles = []
    if file is None:
        return (True, songs, errors)
    with open(file,'r') as file:
        for song in file:
            song = song.strip()
            valid, songId = getSongId(song)
            if valid:
                songs.append(songId)
                if isSongDownloaded(song):
                    song_titles.append(song)
                else:
                    if downloadSong(songId) != True:
                       print(f'Song: {song} needs to be downloaded')
                       errors.append(f"{song} : NO-DOWNLOAD")    
            else:
                errors.append(f"{song} : {songId}")
    if len(errors) > 0:
       return (False, songs, errors)
    else:
       copySongs(song_titles)
       return (True, songs, errors)	
    
def validateMeetupAttach(date, personId):
    queryText = '''SELECT playlist_id FROM Meetups WHERE date = ? AND chair = ?'''
    queryValues = (date, personId)
    row = db.select(DBNAME, queryText, queryValues)
    if len(row) == 0:
        return (False, 'NO_MEET')
    playlistId = row[0][0]
    if playlistId != 0:
        return (False, 'EXISTING_PLAYLIST')   
    return (True, 'OK' ) 

def validateSingalongAttach(date):
    queryText = '''SELECT playlist_id FROM Singalongs WHERE date = ?'''
    queryValues = (date,)
    row = db.select(DBNAME, queryText, queryValues)
    if len(row) == 0:
        return (False, 'NO_SINGALONG')
    playlistId = row[0][0]
    if playlistId != 0:
        return (False, 'EXISTING_PLAYLIST')   
    return (True, 'OK' ) 

def getSongId(song):
    song = song.split('/')
    title = song[0].strip()
    if len(song) > 1:
       key = song[1].strip()
    else:
       key = None
    queryText = '''SELECT song_id FROM Songs WHERE title = ?'''
    queryValue = (title,)
    if key is not None:
        queryText += ''' AND key = ?'''
        queryValue += (key,)
    row = db.select(DBNAME, queryText, queryValue)
    if len(row) == 1:
        return (True, row[0][0])
    elif len(row) == 0:
        return (False, 'NO-SONG')
    else:
        return (False, 'AMBIGUOUS')
    
def addMeetup(date, personId, songs):
    playlistId = 0
    if len(songs) > 0:
       playlistId =  createPlaylist(songs)
    queryText = '''INSERT INTO Meetups (date, chair, playlist_id) VALUES (?, ?, ?)'''
    queryValues = [date, personId, playlistId] 
    queryResult = db.insert(DBNAME, queryText, queryValues)       
    return queryResult

def addMeetupAttach(date, personId, songs):
    playlistId = createPlaylist(songs)
    queryText = '''
                UPDATE Meetups SET playlist_id = ? 
                WHERE date = ? AND chair = ?
                '''
    queryValues = [playlistId, date, personId]
    queryResult = db.update(DBNAME, queryText, queryValues)
    return queryResult

def addSingalong(date, type, songs):
    playlistId = 0
    if len(songs) > 0:
       playlistId =  createPlaylist(songs)
    if type == 'qrcc':
        type = 1
    elif type == 'qrccChristmas':
        type = 2
    else:
        type = 3           
    queryText = '''INSERT INTO Singalongs (date, type, playlist_id) VALUES (?, ?, ?)'''
    queryValues = [date, type, playlistId] 
    queryResult = db.insert(DBNAME, queryText, queryValues)       
    return queryResult

def addSingalongAttach(date, songs):
    playlistId = createPlaylist(songs)
    queryText = '''
                UPDATE Singalongs SET playlist_id = ? 
                WHERE date = ?
                '''
    queryValues = [playlistId, date]
    queryResult = db.update(DBNAME, queryText, queryValues)
    return queryResult
              
def getPlaylistId():
    queryText = '''SELECT MAX(playlist_id) FROM Playlists'''
    queryValue = ()
    playlistId = (db.select(DBNAME, queryText, queryValue))[0][0]
    return playlistId + 1

def createPlaylist(songs):
    playlistId = getPlaylistId()
    createPlayListSongs(playlistId, songs)
    queryText = '''INSERT INTO Playlists (playlist_id) VALUES (?)'''
    queryValues = [playlistId]
    queryResult = db.insert(DBNAME, queryText, queryValues)
    if queryResult != 'SQL_OK':
       print(f"[bold red]Severe SQL Error![/bold red]") 
       raise typer.Abort(16)  
    return playlistId

def createPlayListSongs(playlistId, songs):
    for song in songs:
        queryText = '''INSERT INTO PlaylistSongs (playlist_id, song_id) VALUES (?, ?)'''
        queryValues = [playlistId, song]
        queryResult = db.insert(DBNAME, queryText, queryValues)
        if queryResult == 'SQL_OK':
            continue
        elif queryResult == 'SQL_DUPLICATE':
            print(f"Row ({playlistId} {song}) already exists in table PlaylistSongs - please check")
        else:
            print(f"[bold red]Severe SQL Error![/bold red]") 
            raise typer.Abort(16)      

def isSongDownloaded(song):
    pdfFolder = 'C:/Users/rjbyw/PythonProjects/QRCC_UKES/downloaded_pdfs/'
    song = song + ".pdf"
    file = os.path.join(pdfFolder, song)
    if os.path.exists(file):
        return True
    else:
        return False

def copySongs(songs):
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
        song += '.pdf'
        sourcePath = os.path.join(downloadsFolder, song)
        destPath = os.path.join(specialDownloadsFolder, song)
        shutil.copy(sourcePath, destPath)

def downloadSong(songId):
    queryText = '''
                   SELECT title, songLink FROM Songs where song_id = ?
                '''    
    queryValue = (songId,)
    row = db.select(DBNAME, queryText, queryValue)
    if len(row) == 1:
        title = row[0][0]
        url = row[0][1]
        return fetchPDF(title, url)
    else:
        return False
    
def fetchPDF(title, url):
    downloadsFolder = 'C:/Users/rjbyw/PythonProjects/QRCC_UKES/downloaded_pdfs/'
    uri = derivePdfUri(url)
    try:
        response = requests.get(uri, timeout=10)
        response.raise_for_status()
        filename = title + ".pdf"
        filepath = os.path.join(downloadsFolder, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        fetched = True            
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        fetched = False            
    return fetched    

def derivePdfUri(uri):
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
        
#-----------------------#
# Main application loop #
#-----------------------#     
if __name__ == '__main__':
    app()

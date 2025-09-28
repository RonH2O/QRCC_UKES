@echo off
set "OUTPUT_FILE=qrcc_ukes_doc.txt"

REM Clear the output file if it exists or create a new one
type nul > "%OUTPUT_FILE%"

echo [INFO] Script started at %DATE% %TIME%

REM Call helper for each command
CALL _generate_doc.bat "" "%OUTPUT_FILE%"
CALL _generate_doc.bat "add-song" "%OUTPUT_FILE%"
CALL _generate_doc.bat "add-songsheet" "%OUTPUT_FILE%"
CALL _generate_doc.bat "add-video" "%OUTPUT_FILE%"
CALL _generate_doc.bat "add-artist" "%OUTPUT_FILE%"
CALL _generate_doc.bat "add-meetup" "%OUTPUT_FILE%"
CALL _generate_doc.bat "attach-playlist-to-meetup" "%OUTPUT_FILE%"
CALL _generate_doc.bat "add-singalong" "%OUTPUT_FILE%"
CALL _generate_doc.bat "attach-playlist-to-singalong" "%OUTPUT_FILE%"

echo [INFO] Script finished at %DATE% %TIME% 
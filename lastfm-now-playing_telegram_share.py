from xml.dom import minidom
from urllib.request import urlopen
import sys
from time import sleep, perf_counter
import threading
from pyrogram import Client

userName = ""
apiKey = ""

minutes_to_wait_until_set_original_telegram_name = 15

# Global Variables
currentTrackURL = ('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&nowplaying="true"&user=' +
                   str(userName) + '&api_key=' + str(apiKey))
runCheck = True
waitTime = 1

global start
currentShowedSong = ""

start = perf_counter()
app = Client("lastfm-now-playing_telegram-share")
with app:
    global previous_name
    previous_name = app.get_users("me").first_name
    print(previous_name)


def elapsed_minutes():
    return (perf_counter()-start)/60


def checkForNewSong():
    global currentShowedSong
    global minutes_to_wait_until_set_original_telegram_name
    # Loads Current Song info from Last FM
    currentTrackXML = urlopen(currentTrackURL).read()
    currentTrack = minidom.parseString(currentTrackXML)
    songName = currentTrack.getElementsByTagName('name')
    songArtist = currentTrack.getElementsByTagName('artist')
    currentSongInfo = '🎶'+songName[0].firstChild.nodeValue + \
        " - " + songArtist[0].firstChild.nodeValue + '🎶'

    if currentShowedSong != currentSongInfo:
        currentShowedSong = currentSongInfo
        print(currentSongInfo)

        with app:
            app.update_profile(first_name=currentSongInfo)

    else:
        if elapsed_minutes() >= minutes_to_wait_until_set_original_telegram_name:
            start = perf_counter()
            try:
                with app:
                    app.update_profile(first_name=previous_name)
            except:
                pass


def main():
    try:
        while True:
            checkForNewSong()
            newSongThread = threading.Thread(target=checkForNewSong)
            newSongThread.start()
    except:
        pass


if __name__ == "__main__":
    main()

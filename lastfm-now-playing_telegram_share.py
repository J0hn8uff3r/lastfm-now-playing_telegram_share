from xml.dom import minidom
# from urllib.request import urlopen
from urllib3 import PoolManager
import sys
from time import sleep, perf_counter
import threading
from pyrogram import Client
import os


userName = ""
apiKey = ""

minutes_to_wait_until_set_original_telegram_name = 20

# Global Variables
currentTrackURL = ('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&nowplaying="true"&user=' +
                   str(userName) + '&api_key=' + str(apiKey))
runCheck = True
waitTime = 5

global start
currentShowedSong = ""
diskCover = ""

start = perf_counter()
http = PoolManager(maxsize=10)
app = Client("lastfm-now-playing_telegram-share")
with app:
    previous_name = app.get_users("me").first_name
    print("Original name: " + previous_name)


def elapsed_minutes():
    return (perf_counter()-start)/60


def checkForNewSong():
    global currentShowedSong
    global minutes_to_wait_until_set_original_telegram_name
    global app
    global diskCover
    # Loads Current Song info from Last FM
    currentTrackXML = http.request('GET', currentTrackURL).data
    currentTrack = minidom.parseString(currentTrackXML)
    songName = currentTrack.getElementsByTagName('name')
    songArtist = currentTrack.getElementsByTagName('artist')
    currentSongInfo = '🎶'+songName[0].firstChild.nodeValue + \
        " - " + songArtist[0].firstChild.nodeValue + '🎶'

    if currentShowedSong != currentSongInfo:
        newdiskCover = currentTrack.getElementsByTagName(
            'image')[3].firstChild.nodeValue
        currentShowedSong = currentSongInfo
        # print(currentSongInfo)
        # newdiskCover = currentTrack.getElementsByTagName(
        #     'image')[3].firstChild.nodeValue
        if newdiskCover != diskCover:
            newdiskCover = newdiskCover.replace("300x300", "1200x1200")
            print(newdiskCover)
            os.system("curl -k -o cover.jpg " + newdiskCover)
            newdiskCover = newdiskCover.replace("1200x1200", "300x300")
            diskCover = newdiskCover
            print(newdiskCover)
            with app:
                app.set_profile_photo(photo="cover.jpg")
            print("Profile picture changed to: " + diskCover)

        with app:
            app.update_profile(first_name=currentSongInfo)
            print("Name changed to: " + currentSongInfo)

    elif elapsed_minutes() >= minutes_to_wait_until_set_original_telegram_name:
        start = perf_counter()
        currentSongInfo = ""
        global previous_name
        try:
            with app:
                # if app.get_users("me").first_name != previous_name:
                app.update_profile(first_name=previous_name)
                print("Name restored to: " + previous_name)
        except:
            pass
    sleep(waitTime)


def main():
    while True:
        try:
            checkForNewSong()
            # newSongThread = threading.Thread(target=checkForNewSong)
            # newSongThread.start()
        except:
            pass


if __name__ == "__main__":
    main()

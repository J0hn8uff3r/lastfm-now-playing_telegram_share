from xml.dom import minidom
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
waitTime = 1

# global start
currentShowedSong = currentSongInfo = diskCover = ""
# global start
# song = ""


start = perf_counter()
http = PoolManager(maxsize=10)
app = Client("lastfm-now-playing_telegram-share")


def elapsed_minutes():
    return (perf_counter()-start)/60


def restore_original_name():
    global app
    global original_name
    try:
        with app:
            app.update_profile(first_name=original_name)
            print("Name restored to: " + original_name)
    except:
        pass


def last_cover_checker(newdiskCover):
    with open("last_cover_url.txt", "r+") as file:
        last_cover_url = file.readline()
        print("last_cover_url: " + last_cover_url)
        print("new_cover_url: " + newdiskCover)
        if last_cover_url != newdiskCover:
            newdiskCover = newdiskCover.replace("300x300", "1200x1200")
            print(newdiskCover)
            os.system("curl -k -o cover_lastfm.jpg " + newdiskCover)
            newdiskCover = newdiskCover.replace("1200x1200", "300x300")
            diskCover = newdiskCover
            print(newdiskCover)
            with app:
                app.set_profile_photo(photo="cover_lastfm.jpg")
                print("Profile picture changed to: " + diskCover)
            file.seek(0)
            file.write(newdiskCover)
            file.truncate()


def checkForNewSong():
    global currentShowedSong
    global minutes_to_wait_until_set_original_telegram_name
    global app
    global diskCover
    global start
    global original_name
    global currentSongInfo
    # Loads Current Song info from Last FM
    try:
        currentTrackXML = http.request('GET', currentTrackURL).data
        currentTrack = minidom.parseString(currentTrackXML)
        songName = currentTrack.getElementsByTagName('name')
        songArtist = currentTrack.getElementsByTagName('artist')
        currentSongInfo = songName[0].firstChild.nodeValue + \
            " - " + songArtist[0].firstChild.nodeValue
    except Exception as e:
        print(e)
        pass

    if currentShowedSong != currentSongInfo:
        start = perf_counter()
        newdiskCover = currentTrack.getElementsByTagName(
            'image')[3].firstChild.nodeValue
        currentShowedSong = currentSongInfo
        # song = currentSongInfo

        if newdiskCover != diskCover:
            last_cover_checker(newdiskCover)

        with app:
            app.update_profile(first_name='🎶'+currentSongInfo+'🎶')
            print("Name changed to: " + '🎶'+currentSongInfo+'🎶')

    if elapsed_minutes() >= minutes_to_wait_until_set_original_telegram_name:
        # global start
        start = perf_counter()
        with app:
            current_name = app.get_users("me").first_name
            if current_name != original_name:
                restore_original_name()
                original_name = current_name
    sleep(waitTime)


if __name__ == '__main__':
    with app:
        original_name = app.get_users("me").first_name
        print("Original name: " + original_name)
    while True:
        try:
            checkForNewSong()
        except KeyboardInterrupt:
            print('KeyboardInterruption')
            try:
                restore_original_name()
                print("TECLADO")
                sys.exit(0)
            except SystemExit:
                restore_original_name()
                sys.exit(0)
                pass

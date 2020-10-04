from xml.dom import minidom
from urllib3 import PoolManager
import sys
from time import sleep, perf_counter
import threading
from pyrogram import Client
import os

userName = ""
apiKey = ""

# Global Variables
apiTrackURL = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&nowplaying="true"&user=' + \
    userName + '&api_key=' + apiKey


currentShowedSong = currentSongInfo = diskCover = ""
start = perf_counter()
http = PoolManager(maxsize=10)
app = Client("lastfm-now-playing_telegram-share")
minutes_to_wait_until_set_original_telegram_name = 20
waitTime = 1


def elapsed_minutes():
    return (perf_counter()-start)/60


def restore_original_name():
    global app
    global original_name
    try:
        with app:
            app.update_profile(first_name=original_name)
            print("Name restored to: " + original_name)
    except Exception as e:
        print(e)
        pass


def remove_first_profile_photo():
    try:
        with app:
            app.delete_profile_photos(app.get_profile_photos("me")[0].file_id)
            print("Removed first profile picture")
    except Exception as e:
        print(e)
        pass


def set_first_profile_photo(newdiskCover):
    global file
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


def profile_name_changer(currentSongInfo):
    with app:
        app.update_profile(first_name='🎶'+currentSongInfo+'🎶')
        print("Name changed to: " + '🎶'+currentSongInfo+'🎶')


def last_cover_checker(newdiskCover):
    if newdiskCover != "https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png":
        with open("last_cover_url.txt", "r+") as file:
            last_cover_url = file.readline()
            print("Last_cover_url: " + last_cover_url)
            print("New_cover_url: " + newdiskCover)
            if last_cover_url != newdiskCover:
                set_first_profile_photo(newdiskCover)


def reset_time_counter():
    global start
    start = perf_counter()


def get_album_information(apiTrackURL):
    global currentTrack
    currentTrackXML = http.request('GET', apiTrackURL).data
    currentTrack = minidom.parseString(currentTrackXML)
    songName = currentTrack.getElementsByTagName('name')
    songArtist = currentTrack.getElementsByTagName('artist')
    currentSongInfo = songName[0].firstChild.nodeValue + \
        " - " + songArtist[0].firstChild.nodeValue
    return currentSongInfo


def get_album_cover():
    newdiskCover = currentTrack.getElementsByTagName(
        'image')[3].firstChild.nodeValue
    return newdiskCover


def checkForNewSong():
    global currentShowedSong
    global minutes_to_wait_until_set_original_telegram_name
    global app
    global diskCover
    global original_name
    global currentSongInfo
    # Loads Current Song info from Last FM
    try:
        currentSongInfo = get_album_information(apiTrackURL)
    except Exception as e:
        print(e)
        pass

    if currentShowedSong != currentSongInfo:
        try:
            reset_time_counter()
            newdiskCover = get_album_cover()
            currentShowedSong = currentSongInfo

            profile_name_changer(currentSongInfo)

            if newdiskCover != diskCover:
                last_cover_checker(newdiskCover)

        except Exception as e:
            print(e)
            pass

    if elapsed_minutes() >= minutes_to_wait_until_set_original_telegram_name:
        reset_time_counter()
        try:
            with app:
                current_name = app.get_users("me").first_name
                if current_name != original_name:
                    restore_original_name()
                    original_name = current_name
        except Exception as e:
            print(e)
            pass
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
                remove_first_profile_photo()
                print("TECLADO")
                sys.exit(0)
            except SystemExit:
                restore_original_name()
                sys.exit(0)
                pass

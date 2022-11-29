import os
import threading
from seleniumwire.utils import decode
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import time
import json
from pygame import mixer  # Load the popular external library
from time import sleep

# Variables
alarmsActive = True
vsfPercentageLimit = 0.0

# Sound alarm
soundAlarmTimeSeconds = 20
lastSoundAlarmTime = time.time() - soundAlarmTimeSeconds

# Voice alarm
voiceAlarmTimeSeconds = 5
lastVoiceAlarmTime = time.time() - voiceAlarmTimeSeconds

# Overlay alarm
overlayAlarmTimeSeconds = "5"
lastOverlayAlarmTime = time.time() - int(overlayAlarmTimeSeconds)

# Initialization
thisFolder = os.path.dirname(os.path.abspath(__file__))
mixer.init()
mixer.music.set_volume(0.5)
mixer.music.load(thisFolder + '/nuclear_alarm.mp3')

def sayTTSLinuxIfNecessary(text):
    if (time.time() - lastVoiceAlarmTime) > voiceAlarmTimeSeconds and alarmsActive:
        os.system("espeak -v en-us -s 150 '" + text + "'")

def overlayTextLinux(text):
    if (time.time() - lastOverlayAlarmTime) > int(overlayAlarmTimeSeconds) and alarmsActive:
        os.system("echo '" + text + "' | osd_cat -A center -p middle -f -*-fixed-medium-r-*-*-20-*-*-*-*-*-*-* -c green -d " + overlayAlarmTimeSeconds)

def playSoundAlarm():
    if (time.time() - lastSoundAlarmTime) > soundAlarmTimeSeconds and alarmsActive:
        mixer.music.play()
        sleep(soundAlarmTimeSeconds)

def notify(text):
    global lastAlarmTime
    # threads for 3 alarms
    t1 = threading.Thread(target=playSoundAlarm)
    t2 = threading.Thread(target=sayTTSLinuxIfNecessary, args=(text,))
    t3 = threading.Thread(target=overlayTextLinux, args=(text,))
    t1.start()
    t2.start()
    t3.start()

def changeVsfPercentageLimitInput():
    global vsfPercentageLimit
    global alarmsActive
    userInput = input("Enter new vsfPercentageLimit or (start) (stop): ")
    if userInput == "start":
        alarmsActive = True
        print("Alarms active")
    if userInput == "stop":
        alarmsActive = False
        print("Alarms stopped")
    else:
        vsfPercentageLimit = float(userInput)

def changeVsfPercentageLimit():
    while True:
        try:
            changeVsfPercentageLimitInput()
        except ValueError:
            print("Not a number")
            continue

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=Options())
# driver = webdriver.Chrome(options=options)

driver.get("https://skyshowtime.globalreliability.sky/")

def main():

    changeVsfPercentageLimitInput()

    # changeVsfPercentageLimit in another thread
    t = threading.Thread(target=changeVsfPercentageLimit)
    t.start()

    # Each 5 seconds
    while True:
        for request in driver.requests:
            if request.response and "video-start-failures" in request.url:
                body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                obj = json.loads(body)

                # if obj.data only has total field
                if len(obj["data"]) == 1:

                    vsfPercentage = float(obj['data']['total'][0]['videoStartFailuresPercentage'])
                    vsfPercentageTwoDecimalPlaces = round(vsfPercentage, 2)

                    if vsfPercentage > vsfPercentageLimit:
                        notify("VsfPercentageLimit has been reached: " + str(vsfPercentageTwoDecimalPlaces))
                        break

        # Clear requests
        driver.requests.clear()

        # Wait 5 seconds
        time.sleep(5)



main()

import os
import threading

# import vlc
from seleniumwire.utils import decode
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import time
import json
from IPython.display import Audio

alarmTimeout = 20

vsfPercentageLimit = 0.0
lastAlarmTime = time.time() - alarmTimeout

def notify(title, text):
    global lastAlarmTime
    if (time.time() - lastAlarmTime) > alarmTimeout:
        os.system("""
                  osascript -e 'display notification "{}" with title "{}"'
                  """.format(text, title))
        Audio(url="https://www.tones7.com/media/nuclear_alarm.mp3")
        lastAlarmTime = time.time()

def changeVsfPercentageLimitInput():
    global vsfPercentageLimit
    vsfPercentageLimit = float(input("Enter new vsfPercentageLimit: "))

def changeVsfPercentageLimit():
    while True:
        try:
            changeVsfPercentageLimitInput()
        except ValueError:
            print("Please enter a number")
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

                    if vsfPercentage > vsfPercentageLimit:
                        notify("VsfPercentageLimit", "VsfPercentageLimit has been reached: " + str(vsfPercentage))
                        break

        # Clear requests
        driver.requests.clear()

        # Wait 5 seconds
        time.sleep(5)



main()

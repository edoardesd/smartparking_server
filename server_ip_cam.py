import base64
import cv2 as cv
import datetime
import json
import paho.mqtt.client as mqtt
import schedule
import sys
import time

IMAGES_FOLDER = "images/"
URL = "http://10.78.78.5/mjpg/video.mjpg"
DEFAULT_PARKING_AVAILABLE = 2
SCHEDULER_PUBLISH_INTERVAL = 5
SCHEDULER_SAVE_INTERVAL = 60
BROKER_URL = "broker.hivemq.com"
RETAIN = True
QUALITY_OF_SERVICE = 2

IMAGE_WIDTH = 720
IMAGE_HEIGHT = 640

image = None


def image_scheduler(_client):
    global image
    image, bts = take_pic()
    # call parking reckognition
    parking_available = DEFAULT_PARKING_AVAILABLE
    data = {'image': bts.decode('ascii'), 'available_slots': parking_available}
    json_data = json.dumps(data)
    _client.publish("smart/parking/polimi/dastu/image",
                    json_data,
                    qos=QUALITY_OF_SERVICE,
                    retain=RETAIN)

    _client.publish("smart/parking/polimi/dastu/prediction",
                    parking_available,
                    qos=QUALITY_OF_SERVICE,
                    retain=RETAIN)
    print("PUBLISH: done")


def save_scheduler():
    global image
    if image is not None:
        print("SAVE: done")
        cv.imwrite(IMAGES_FOLDER + get_filename(), image)


def take_pic():
    result, img = cam.read()
    if result:
        # img = cv.resize(img, (IMAGE_WIDTH, IMAGE_HEIGHT))
        img = cv.resize(img, None, fx=1 / 3, fy=1 / 3, interpolation=cv.INTER_LANCZOS4)
        is_success, _bts = cv.imencode(".png", img)
        if is_success:
            _bts = base64.b64encode(_bts)
            print("ENCODING: done")
    else:
        print("No pic detected. Please try again")

    return img, _bts


def get_filename():
    date_ob = datetime.datetime.now()
    year = '{:02d}'.format(date_ob.year)
    month = '{:02d}'.format(date_ob.month)
    day = '{:02d}'.format(date_ob.day)
    hour = '{:02d}'.format(date_ob.hour)
    minute = '{:02d}'.format(date_ob.minute)
    second = '{:02d}'.format(date_ob.second)
    return "{}{}{}-{}{}{}.png".format(year, month, day, hour, minute, second)


def on_connect(client, _, flags, rc):
    print("Connected flags" + str(flags) + "result_code" + str(rc) + str(client))


def main():
    client = mqtt.Client()
    client.connect(BROKER_URL)
    client.on_connect = on_connect

    schedule.every(SCHEDULER_PUBLISH_INTERVAL).seconds.do(image_scheduler, _client=client)
    schedule.every(SCHEDULER_SAVE_INTERVAL).seconds.do(save_scheduler)
    client.loop_start()

    is_running = True

    while is_running:
        schedule.run_pending()

        time.sleep(1)


def testDevice():
    cap = cv.VideoCapture(URL)
    if cap is None or not cap.isOpened():
        print('Warning: unable to open video source: ', URL)
    else:
        print("Found a video device at url {}".format(URL))
        return cap

    sys.exit('Warning: no valid video sources. Exiting...')


if __name__ == "__main__":
    print("+++ Smart parking camera converter ANTLAB +++")
    cam = testDevice()
    main()

import base64
import cv2 as cv
import json
import paho.mqtt.client as mqtt
import schedule
import sys
import time

DEVICE_RANGE = 10
SCHEDULER_FIRST_EVENT = 1
SCHEDULER_PRIORITY = 1
SCHEDULER_INTERVAL = 10
DEFAULT_PARKING_AVAILABLE = 0
BROKER_URL = "broker.hivemq.com"
RETAIN = True
QUALITY_OF_SERVICE = 2


def image_scheduler(_client):
    image_bts = take_pic()
    # call parking reckognition
    parking_available = DEFAULT_PARKING_AVAILABLE
    data = {'image': image_bts.decode('ascii'), 'available_slots': parking_available}
    json_data = json.dumps(data)
    _client.publish("smart/parking/polimi/image",
                    json_data,
                    qos=QUALITY_OF_SERVICE,
                    retain=RETAIN)

    _client.publish("smart/parking/polimi/prediction",
                    parking_available,
                    qos=QUALITY_OF_SERVICE,
                    retain=RETAIN)
    print("Publishing the pic")


def on_connect(client, _, flags, rc):
    print("Connected flags" + str(flags) + "result_code" + str(rc) + str(client))


def take_pic():
    result, image = cam.read()

    if result:
        # call cv.imwrite()
        is_success, bts = cv.imencode(".png", image)
        if is_success:
            bts = base64.b64encode(bts)
            print("Encoding the pic")
            return bts
    else:
        print("No pic detected. Please try again")


def main():
    client = mqtt.Client()
    client.connect(BROKER_URL)
    client.on_connect = on_connect

    schedule.every(5).seconds.do(image_scheduler, _client=client)
    client.loop_start()

    is_running = True

    while is_running:
        schedule.run_pending()
        time.sleep(1)


def testDevice():
    for source in range(DEVICE_RANGE):
        cap = cv.VideoCapture(source)
        if cap is None or not cap.isOpened():
            print('Warning: unable to open video source: ', source)
        else:
            print("Found a video device at index {}".format(source))
            return cap

    sys.exit('Warning: no valid video sources. Exiting...')


if __name__ == "__main__":
    print("+++ Smart parking camera checker RASPI +++")
    cam = testDevice()
    main()

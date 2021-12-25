import aqi
import paho.mqtt.publish as publish
import re
import subprocess
import time
from datetime import datetime
from decouple import config
from sds011 import *


def temperature_get():
    return_value = subprocess.check_output(
        "sudo vcgencmd measure_temp", stderr=subprocess.STDOUT, shell=True
    )
    return_text = str(return_value)
    return_list = re.findall(r"(?<==).*?(?=\')", return_text)

    return return_list[0]


def pm_query(n=3):
    sensor.sleep(sleep=False)
    time.sleep(18)  # For more acuratete
    pm_2_5 = 0
    pm_10 = 0
    for i in range(n):
        results = sensor.query()
        pm_2_5 += results[0]
        pm_10 += results[1]
        time.sleep(6)
    pm_2_5 = round(pm_2_5 / n, 1)
    pm_10 = round(pm_10 / n, 1)

    return pm_2_5, pm_10


def aqi_convert(pm_2_5, pm_10):
    aqi_2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pm_2_5))
    aqi_10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pm_10))

    return aqi_2_5, aqi_10


def mqtt_sent(pm_2_5, pm_10, aqi_2_5, aqi_10, temp):

    try:
        channel_id = config("CHANNEL_ID")
        apikey_write = config("APIKEY_WRITE")
        mqtt_urn = "channels/" + channel_id + "/publish/" + apikey_write
        mqtt_hostname = config("MQTT_HOSTNAME")
        mqtt_transport = config("MQTT_TRANSPORT")
        mqtt_port = int(config("MQTT_PORT"))
        mqtt_tsl = config("MQTT_TSL")
        mqtt_tsl = None if mqtt_tsl == "None" else mqtt_tsl
    except:
        print("[ERROR]", datetime.now(), "Can't get .env file.", sep=",")

    mqtt_playload = (
        "field1="
        + str(pm_2_5)
        + "&field2="
        + str(aqi_2_5)
        + "&field3="
        + str(pm_10)
        + "&field4="
        + str(aqi_10)
        + "&field5="
        + temp
    )
    publish.single(
        mqtt_urn,
        payload=mqtt_playload,
        hostname=mqtt_hostname,
        port=mqtt_port,
        tls=mqtt_tsl,
        transport=mqtt_transport,
    )


sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)

try:
    pm_2_5, pm_10 = pm_query(3)
    aqi_2_5, aqi_10 = aqi_convert(pm_2_5, pm_10)
    temp = temperature_get()
    mqtt_sent(pm_2_5, pm_10, aqi_2_5, aqi_10, temp)
    print("[INFO]", datetime.now(), pm_2_5, pm_10, aqi_2_5, aqi_10, temp, sep=",")
except TypeError:
    print("[FATAL]", datetime.now(), "Can't get data.", sep=",")
except:
    print("[ERROR]", datetime.now(), pm_2_5, pm_10, aqi_2_5, aqi_10, temp, sep=",")

sensor.sleep(sleep=True)

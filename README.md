# [PMPi](https://thingspeak.com/channels/1414919)

In Thailand particulate matter is very high in October to February. This project aims to demo how to measure particulate matter with a Raspberry Pi. Got inspire from [mjrovai](https://www.instructables.com/A-Low-cost-IoT-Air-Quality-Monitor-Based-on-Raspbe/)

## Requirement

* Raspberry Pi (Raspberry Pi Zero W or greater)
* Micro-SD card
* Power adapter
* Sencor SDS011
* [Optional] Raspberry Pi case

I ordered Raspberry Pi from Cytron and others from Aliexpress, totally below $35.

## Installation

Signup [ThingSpeak](https://thingspeak.com). Got Channel ID and Write API Key to configure .env, and setting

* Field 1: Pm 2.5 in µg/㎥
* Field 2: Pm 2.5 in AQI Index
* Field 3: Pm 10 in µg/㎥
* Field 4: Pm 10 in AQI Index
* Field 5: CPU temperature (must less than 85℃)

Download Image from [Ubuntu Server](http://cdimage.ubuntu.com/ubuntu-server/focal/daily-preinstalled/current/) for Raspberry Pi mostly use [32 bits](http://cdimage.ubuntu.com/ubuntu-server/focal/daily-preinstalled/current/focal-preinstalled-server-armhf+raspi.img.xz) except you have RAM more than 4 GB and that extravagant for use in this project. (You can use Raspberry Pi OS or Debian like OS but I didn't test it)

```bash
# Set hostname to prevent duplication.
sudo hostnamectl set-hostname pmpi

# Set timezone and ntp for precious time. You can change values to your times.
sudo timedatectl set-timezone Asia/Bangkok
echo 'NTP=0.th.pool.ntp.org' | sudo tee -a /etc/systemd/timesyncd.conf
sudo timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd.service

# Make Ubuntu recently agin.
sudo apt update
sudo apt --yes full-upgrade
sudo reboot

# libraspberrypi-bin for monitor CPU temperature.
sudo apt --yes install libraspberrypi-bin python3-pip
sudo apt --yes autoremove

# paho-mqtt for MQTT connection
# py-sds011 for get data fron sensor
# python-aqi for indicating PM
pip install paho-mqtt py-sds011 python-aqi

# Clone this repository.
cd && git clone https://github.com/overbid/pmpi.git

# Configure .env.
cp .env.example .env
sed -i "s/CHANNEL_ID=.*/CHANNEL_ID=<Your Channel ID>/g" .env
sed -i "s/APIKEY_WRITE=.*/APIKEY_WRITE=<Your Write API Key>/g" .env

# Setting crontab to send data to ThingSpeak every 3 minutes.
cd && crontab -e
crontab -l > my-crontab
echo "*/3 * * * * /usr/bin/python3 /home/ubuntu/pmpi/pmpi.py >> ~/cron.log 2>&1" | tee -a my-crontab
crontab my-crontab

# Wait at 3 minutes and checking.
cd && cat cron.log && date
```

## Usage

If everything is working well you can see your AQI data from your channel on ThingSpeak. Good luck.

## License

[MIT](https://choosealicense.com/licenses/mit/)

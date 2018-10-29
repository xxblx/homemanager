
# HomeManager

HomeManager is a simple solution for in-home ip cameras management. It allows to control devices with special politics and streams videos from cameras (rtsp) to web (hls).

HomeManager is designed for personal usage at home's local network (i.e. without access from the internet) with some kind of home server (where the app is installed), Mikrotik router and Xiaomi Xiaofang 1S cameras. You have to flash [custom firmware](https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks) for using these camera models with HomeManager. 

This solution is not suitable for using in the production and may have some security weaknesses (for example, token-based auth mechanism doesn't support tokens renew process and tokens don't have expires time).

## How it works
If user at home rtsp feed and motion detection are disabled, night-mode settings are ignored. When user has left home night-mode settings are configuring according to the current time (depends on sunrise and sunset), rtsp feed and motion detection are turning on. 

* HomeManager is running on some kind of home server
* Router checks status of user's device and notifies HomeManager
* Camera requests settings from HomeManager and apply them 
* User is able to open web ui and watch the stream if rtsp feed is active
* HomeManager sends telegram notifications to user if motion is detected

# Installation
## HomeManager
* Create user 
```
# useradd hmuser -m -s /sbin/nologin
```
* Define identity (id) of your camera, example: `camera-room` 
* Edit `ffmpeg-rtsp-hls.service` and `ffmpeg-rtsp-hls.path`, enter correct paths and address of rtsp feed
  * _**Note**: use the same replacement for "/path/camera-identity" in both files_
* If you have few cameras, create copies of `ffmpeg-rtsp-hls.service` and `ffmpeg-rtsp-hls.path`, edit them
* Place `ffmpeg-rtsp-hls.service` and `ffmpeg-rtsp-hls.path` to `/etc/systemd/system`
* Start and enable path-unit
```
# systemctl start ffmpeg-rtsp-hls.path
# systemctl enable ffmpeg-rtsp-hls.path
```
* Install and configure PostgreSQL, create db and user. [A quick start on Fedora](https://fedoramagazine.org/postgresql-quick-start-fedora-24/).
* Copy `home_manager/conf.default.py` to `home_manager/conf.py` and edit `home_manager/conf.py`
* First init (create tables, etc)
```
$ ./db_manage.py init
```
* Add user
```
$ ./db_manage.py users -u username
```
* Create access token for Mikrotik
```
$ ./db_manage.py tokens -i mikrotik
```
* Create access token for camera (use identity and path from previous steps) and add video source
```
$ ./db_manage.py tokens -i camera-room
$ ./db_manage.py video -n camera-room -p /tmp/hmuser/camera-room/video/video.m3u8
```
* Add access restrictions
```
$ ./db_manage.py access -p /api/user/status -n 'update user status'
$ ./db_manage.py access -p /api/camera/motion -n 'send motion picture'
$ ./db_manage.py access -p /api/camera/setup -n 'get settings for camera'
```
* Check accesses ids
```
$ ./db_manage.py list-access
```
* Setup access (replace 1, 2 and 3 with correct ids from previous step) 
```
$ ./db_manage.py set-access -a 1 -i mikrotik
$ ./db_manage.py set-access -a 2 -i camera-room
$ ./db_manage.py set-access -a 3 -i camera-room
```
* Edit `homemanager.service`, enter correct paths and place service file to `/etc/systemd/system`
* Start and enable systemd unit
```
# systemctl start homemanager.service
# systemctl enable homemanager.service
```

## Mikrotik 
* Decide what device will mark that you are at home, check mac address of the device
* Edit `scripts/mikrotik_script`, enter correct host, token (from previous steps), mac-address, userid values
* Add script's content to Mikrotik scripts
  * Winbox: System - Scripts - plus, enter `check_devices` to "Name" field, enter script's content to "Source" field, Ok
* Set scheduler for script
  * Winbox: System - Scheduler - plus, enter `run_check_devices` to name field, set interval like `00:05:00` (how often router would check device and notify homemanager, '00:10:00' equals to 10 mins, '00:01:00' equals to 1 min), enter `/system script run check_devices` into "On Event" field, Ok
  * Terminal: `/system scheduler add name=run_check_devices interval=10m on-event=check_devices`

## Camera
* Edit `scripts/camera_module`, enter correct host and token (from previous steps) values
* Place `scripts/camera_module`, `scripts/camera_setup_script` and `scripts/camera_startup_script` to `/system/sdcard/config/userscripts` on your camera
* Place `scripts/camera_motion_script` to `/system/sdcard/config/userscripts/motiondetection` on camera
* Add `/system/sdcard/config/userscripts/camera_startup_script` to the end of `/system/sdcard/run.sh` on camera 
* Run `/system/sdcard/config/userscripts/camera_startup_script` 
* Add `/system/sdcard/config/userscripts/camera_setup_script` to crontab
  * `# crontab -c /system/sdcard/config/cron/crontabs -e`
  * Add `*/5     *       *       *       *       /system/sdcard/config/userscripts/camera_setup_script` in the end, in this way a command executes every 5 mins

# Additional information
## Motion detect
Swap has to be enabled on camera for motion detections. See [this issue](https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks/issues/552) for details. Script `script/camera_startup_script` includes all required commands for that. If you have completed all steps from installation instructions, everything should work fine. Additional actions are not required. 

### Telegram notifications
* Set `NOTIFICATIONS_SETTINGS['telegram']` = `True` in `home_manager/conf.py`
* [Register your bot](https://core.telegram.org/bots#6-botfather) and set correct `TELEGRAM_SETTINGS['bot_id']` in `home_manager/conf.py`
* Add bot to a chat
* Set `TELEGRAM_SETTINGS['chat_id']` in `home_manager/conf.py` (you are able to use link like `https://api.telegram.org/bot<bot_id>/getUpdates`, chat_id is presented in logs if you have added your bot to a chat)
* Enter proxies to `TELEGRAM_SETTINGS['proxy']` if telegram is blocked in your region

### Email notifications
Not implemented yet

## Restrict access from camera to the internet
Use mikrotik's firewall, something like
```
/ip firewall filter add chain=forward src-address=<camera's ip> dst-address=!192.168.1.0/24 action=drop comment="Drop 
tries to reach the internet from ip camera (local network is allowed)"
```

## sdcard is mounted in read-only mode
```
mount -o remount,rw /system/sdcard
```
Check [this issue](https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks/issues/409). 

## Dependencies and system requirements
* [Custom firmware](https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks) for cameras
* [Python](http://www.python.org) (3.5 or newer) and [Tornado](https://github.com/tornadoweb/tornado) (5.0 or newer)
* [PostgreSQL](http://www.postgresql.org) and [psycopg2](http://initd.org/psycopg), [aiopg](https://github.com/aio-libs/aiopg)
* [ffmpeg](https://ffmpeg.org)
* [bcrypt](https://github.com/pyca/bcrypt)
* [Astral](https://github.com/sffjunkie/astral)
* [requests](https://github.com/requests/requests) 

## License
HomeManager is free and opensource software, it is licensed under GNU GPL 3 (or newer) license. Check `LICENSE` for details.


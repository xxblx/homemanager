
# HomeManager

HomeManager is a simple solution for in-home ip cameras management. It allows to control devices with special politics and stream videos from cameras (rtsp) to web (hls).

HomeManager is designed for personal usage at home's local network (i.e. without access from the internet) with some kind of home server (where the app is installed), Mikrotik router and Xiaomi Xiaofang 1S cameras. You have to flash [custom firmware](https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks) for using these camera models with HomeManager. 

This solution is not suitable for using in the production and may have some security weaknesses (for example, token-based auth mechanism doesn't support tokens renew process).

# Installation
## HomeManager
* Create user 
```
# useradd hmuser -m -s /sbin/nologin
```
* Edit `ffmpeg-rtsp-hls.service`, enter correct path and address of rtsp feed
* If you have few cameras, create copies of `ffmpeg-rtsp-hls.service` and edit them
* Place `ffmpeg-rtsp-hls.service` to `/etc/systemd/system`
* Start and enable systemd unit
```
# systemctl start ffmpeg-rtsp-hls.service
# systemctl enable ffmpeg-rtsp-hls.service
```
* Install and configure PostgreSQL, create db and user. [A quick start on Fedora](https://fedoramagazine.org/postgresql-quick-start-fedora-24/).
* Copy `home_manager/conf.default.py` to `home_manager/conf.py` and edit `home_manager/conf.py`
* First init (create tables, etc)
```
$ ./db_manage.py init
```
* Add user and tokens
```
$ ./db_manage.py users -u username
$ ./db_manage.py tokens -i mikrotik
$ ./db_manage.py tokens -i camera-room
$ ./db_manage.py tokens -i camera-kitchen
```
* Add access restrictions
```
$ ./db_manage.py -p /api/user/status -n 'update user status'
$ ./db_manage.py -p /api/camera/motion -n 'send motion picture'
$ ./db_manage.py -p /api/camera/setup -n 'get settings for camera'
```
* Check ids
```
$ ./db_manage.py list-access
```
* Setup access (replace 1, 2 and 3 with correct ids from previous step) 
```
$ ./db_manage.py -a 1 -i mikrotik
$ ./db_manage.py -a 2 -i camera-room camera-kitchen
$ ./db_manage.py -a 3 -i camera-room camera-kitchen
```
* Add video sources 
```
# use paths from units like ffmpeg-rtsp-hls.service
$ ./db_manage.py video -p /path/video/camera1/video.m3u8 -n camera1 -c room
$ ./db_manage.py video -p /path/video/camera2/video.m3u8 -n camera2 -c kitchen
```
* Edit `homemanager.service`, enter correct paths and place the file to `/etc/systemd/system`
* Start and enable systemd unit
```
# systemctl start homemanager.service
# systemctl enable homemanager.service
```

## Mikrotik 
* Decide what device will mark that you are at home, check mac address of the device
* Edit `scripts/mikrotik_script`, enter correct host, token, mac-address, userid values
* Add script's content to Mikrotik scripts, if you are using Winbox, System - Scripts - plus, enter 'check_devices' to script's name field, enter script's content, Ok

## Camera
* Edit `scripts/camera_module`, enter correct host and token values
* Place `scripts/camera_module`, `scripts/camera_setup_script` and `scripts/camera_startup_script` to `/system/sdcard/config/userscripts` on your camera
* Place `scripts/camera_motion_script` to `/system/sdcard/config/userscripts/motiondetection` on camera
* Add `/system/sdcard/config/userscripts/camera_startup_script` to the end of `/system/sdcard/run.sh` on camera 
* Run `/system/sdcard/config/userscripts/camera_startup_script` 
* Add `/system/sdcard/config/userscripts/camera_setup_script` to crontab

# Additional information
## Motion detect
Swap have to be enabled on camera for motion detections. See [this issue](https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks/issues/552) for details. Script `script/camera_startup_script` includes all required commands for that. If you have completed all steps from installation instructions, everything should work fine. Additional actions are not required. 

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

## License
HomeManager is free and opensource software, it is licensed under GNU GPL 3 (or newer) license. Check `LICENSE` for details.





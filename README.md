
# HomeManager

HomeManager is a simple platform to manage cameras at home. HomeManager defines and controls device policies, including video streaming, motion detection, and night mode. Settings shared to a device depend on whether a user at home.

HomeManager is a solution designed for personal use at the private network (i.e., without access from the internet). The software might not be ready for production usage due to a lack of security focus during development. Use at your own risk.

HomeManager supports Xiaomi Xiaofang 1S cameras flashed with the [custom firmware](https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks) and Mikrotik routers. However, it should be possible to use other camera models without server-side changes or with minimal adaptation. Also, almost any router allowing execution of shell commands could work (e.g., models operated by OpenWRT). But if you are going to use any devices except Mikrotik and Xiaomi Xiaofang 1S, you need to adapt the client scripts.

# Installation
## HomeManager
* Edit `homemanager.service`, `ffmpeg-rtsp-hls.path`, `ffmpeg-rtsp-hls.service` and save to `/etc/systemd/system`.
* Copy `homemanager/conf.default.py` to `homemanager/conf.py` and edit conf.py.

```
# dnf install python3-tornado python3-aiopg python3-psycopg2 python3-astral python3-pynacl
# systemctl enable --now ffmpeg-rtsp-hls.path
$ ./db_manage.py init
$ ./db_manage.py router-add -n mikrotik
$ ./db_manage.py camera-add -n camera1 -p /path/to/video.m3u8 -a /path/from/ffmpeg-rtsp-hls.path
# systemd enable --now homemanager.service
$ ./db_manage.py token-add -n mikrotik
$ ./db_manage.py token-add -n camera1
$ ./db_manage.py user-add -u username
```

## Mikrotik
* Edit `scripts/mikrotik_script`
* Add the script to Mikrotik
  * Winbox: System - Scripts - plus, enter `check_device` to "Name" field, enter script's content to "Source" field, Ok
* Set scheduler
  * Winbox: System - Scheduler - plus, enter `run_check_device` to name field, set interval `00:05:00` ('00:10:00' equals to 10 mins, '00:01:00' equals to 1 min), enter `/system script run check_device` into "On Event" field
  * Terminal: `/system scheduler add name=run_check_device interval=10m on-event=check_device`

## Camera
* Edit `scripts/camera_module`
* Put `scripts/camera_module`, `scripts/camera_setup_script` and `scripts/camera_startup_script` to `/system/sdcard/config/userscripts`
* Put `scripts/camera_motion_script` to `/system/sdcard/config/userscripts/motiondetection`
* Append `/system/sdcard/config/userscripts/camera_startup_script` to the end of `/system/sdcard/run.sh`
* Run `/system/sdcard/config/userscripts/camera_startup_script` 
* Add `/system/sdcard/config/userscripts/camera_setup_script` to crontab
  * `# crontab -c /system/sdcard/config/cron/crontabs -e`
  * Append `*/5     *       *       *       *       /system/sdcard/config/userscripts/camera_setup_script > /system/sdcard/config/userscripts/camera_setup_log` - in this example the command executes every 5 minutes and saves the last configuration json to the log file.

# Additional information
## Motion detection
Cameras require swap for motion detection. See [this issue](https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks/issues/552). Note, `script/camera_startup_script` includes all required steps. If you followed the installation instructions, additional actions are not required. 

### Telegram notifications
* Set `NOTIFICATIONS_SETTINGS['telegram']` = `True` in `homemanager/conf.py`
* [Register your bot](https://core.telegram.org/bots#6-botfather)
* Set correct `TELEGRAM_SETTINGS['bot_id']` in `homemanager/conf.py`
* Add the bot to a chat
* Set `TELEGRAM_SETTINGS['chat_id']` in `homemanager/conf.py` (check `https://api.telegram.org/bot<bot_id>/getUpdates`, look for a chat_id in logs once you have added the bot to the chat)
* Enter proxies to `TELEGRAM_SETTINGS['proxy']` if telegram is blocked in your region

## Restrict access from a camera to the internet
Mikrotik firewall
```
/ip firewall filter add chain=forward src-address=camera_ip dst-address=!192.168.1.0/24 action=drop comment="Drop 
tries to reach the internet from ip camera (local network is allowed)"
```

## sdcard is mounted in read-only mode
```
mount -o remount,rw /system/sdcard
```
Check [this issue](https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks/issues/409). 

## Dependencies and bundled libraries
* [Python](http://www.python.org) and [Tornado](https://github.com/tornadoweb/tornado)
* [PostgreSQL](http://www.postgresql.org) and [psycopg2](http://initd.org/psycopg), [aiopg](https://github.com/aio-libs/aiopg)
* [ffmpeg](https://ffmpeg.org)
* [pynacl](https://github.com/pyca/pynacl/)
* [Astral](https://github.com/sffjunkie/astral)
* [Bootstrap](https://getbootstrap.com/)
* [HLS.js](https://github.com/video-dev/hls.js/)

## License
HomeManager is free and opensource software. Check LICENSE for details.

Bundled libraries: Bootstrap - [MIT](https://getbootstrap.com/docs/5.0/about/license/), HLS.js - [Apache 2.0](https://github.com/video-dev/hls.js/blob/v1.0.4/LICENSE). 

from infi.systray import SysTrayIcon
from threading import Thread
import discordrpc
from discordrpc import Activity
import time
import asyncio
import copy
import os, sys
from utils import *


def resource_path(relative_path):
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)


savedMediaInfo = Metadata()
systemManager = WindowsMediaInfo()

async def update_media_info():
	global savedMediaInfo
	currentMediaInfo = await systemManager.get_media_info()

	if not currentMediaInfo == savedMediaInfo:
		if currentMediaInfo.status == "PLAYING":
			answer = copy.copy(currentMediaInfo)
			if answer.thumbnail:
				answer.thumbnail = await answer.thumbnail.get()

			if answer.current and answer.total:
				ts_start = int(time.time()) - answer.current
				ts_end = ts_start + answer.total
			else:
				ts_start = None
				ts_end = None

			if rpc.set_activity(
				state=answer.artist if answer.artist else None,
				details=answer.title,
				act_type=Activity.Listening,
				ts_start=ts_start,
				ts_end=ts_end,
				large_image=answer.thumbnail if answer.thumbnail else None,
				small_image="https://raw.githubusercontent.com/SuperZombi/Discord-Music-Status/refs/heads/main/github/images/audio-wave.gif"
			):
				savedMediaInfo = currentMediaInfo
				await asyncio.sleep(15)
		else:
			rpc.clear()
	else:
		await asyncio.sleep(5)

async def addEventListeners():
	while True:
		await update_media_info()

def startBackgroundLoop():
	asyncio.run(addEventListeners())


rpc = discordrpc.RPC(app_id=1397914682659963050, exit_if_discord_close=False, exit_on_disconnect=False)
Thread(target=startBackgroundLoop, daemon=True).start()
systray = SysTrayIcon(resource_path("icon.ico"), "Discord Music Status", on_quit=lambda _: os._exit(0))
systray.start()
rpc.run()

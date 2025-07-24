import discordrpc
import time
import asyncio
import copy
from utils import *


MediaInfo = Metadata()
systemManager = WindowsMediaInfo()

async def update_media_info():
	global MediaInfo
	localMediaInfo = await systemManager.get_media_info()

	if not localMediaInfo == MediaInfo:
		MediaInfo = localMediaInfo

		if MediaInfo.status == "PLAYING":
			answer = copy.copy(localMediaInfo)
			if answer.thumbnail:
				answer.thumbnail = await answer.thumbnail.get()
			
			ts_start = int(time.time()) - answer.current
			ts_end = ts_start + answer.total

			rpc.set_activity(
				state=answer.artist,
				details=answer.title,
				act_type=2,
				ts_start=ts_start,
				ts_end=ts_end,
				large_image=answer.thumbnail if answer.thumbnail else None
			)
			await asyncio.sleep(15)
		else:
			rpc.set_activity(None)
	else:
		await asyncio.sleep(5)

async def addEventListeners():
	while True:
		await update_media_info()


rpc = discordrpc.RPC(app_id=1397914682659963050)
asyncio.run(addEventListeners())
rpc.run()

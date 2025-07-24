from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlayStatus
from winsdk.windows.storage.streams import DataReader, Buffer, InputStreamOptions
from dataclasses import dataclass
import base64
import requests


class Thumbnail:
	async def __new__(cls, *a, **kw):
		instance = super().__new__(cls)
		await instance.__init__(*a, **kw)
		return instance

	async def __init__(self, thumbnail):
		self.thumb = await thumbnail.open_read_async()
		self.size = self.thumb.size
		self.result = None

	def __eq__(self, other):
		return self.size == other.size

	async def get(self) -> str:
		if self.result: return self.result
		buffer = Buffer(self.size)
		await self.thumb.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
		buffer_reader = DataReader.from_buffer(buffer)
		byte_buffer = bytearray(buffer_reader.read_buffer(buffer.length))
		self.result = self.upload_image(byte_buffer)
		return self.result

	def upload_image(self, image_bytes):
		image_base64 = base64.b64encode(image_bytes).decode('utf-8')
		try:
			response = requests.post(
				"https://api.imgbb.com/1/upload",
				data={
					"key": "dc484814bd5344f8f87a97d292cea867",
					"image": image_base64,
					"expiration": 300
				}
			)
			data = response.json()
			if response.status_code == 200 and data.get("success"):
				return data["data"]["url"]
			else:
				raise Exception("Failed to upload image")
		except Exception as e:
			print(e)


@dataclass
class Metadata():
	artist: str = ""
	title: str = ""
	current: int = 0
	total: int = 0
	status: str = None
	thumbnail: Thumbnail = None

	def __eq__(self, other):
		return (
			self.artist == other.artist and
			self.title == other.title and
			self.current == other.current and
			self.total == other.total and
			self.status == other.status and
			self.thumbnail == other.thumbnail
		)

class WindowsMediaInfo():
	async def get_session(self):
		manager = await MediaManager.request_async()
		active_sessions = list(
			filter(
				lambda session: session.get_playback_info().playback_status == PlayStatus.PLAYING,
				manager.get_sessions()
			)
		)
		if len(active_sessions) > 0:
			return active_sessions[0]

	async def get_media_info(self):
		metadata = Metadata()
		current_session = await self.get_session()
		if current_session:
			playback_info = current_session.get_playback_info()

			metadata.status = playback_info.playback_status.name

			timeline_properties = current_session.get_timeline_properties()
			metadata.current = int(timeline_properties.position.total_seconds())
			metadata.total = int(timeline_properties.end_time.total_seconds())
			
			info = await current_session.try_get_media_properties_async()
			metadata.artist = info.artist
			metadata.title = info.title

			thumbnail = info.thumbnail
			if thumbnail:
				metadata.thumbnail = await Thumbnail(thumbnail)
		return metadata


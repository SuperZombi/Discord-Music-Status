from flask import Flask, request, make_response
from infi.systray import SysTrayIcon
from threading import Thread
import discordrpc
import time
import os, sys

def resource_path(relative_path):
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)

app = Flask(__name__)

last_update_time = 0

@app.after_request
def add_cors_headers(response):
	response.headers['Access-Control-Allow-Origin'] = '*'
	response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
	response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
	return response

@app.route('/update', methods=['POST', 'OPTIONS'])
def update_presence():
	global last_update_time
	if request.method == 'OPTIONS':
		return make_response('', 204)

	data = request.json
	last_update_time = time.time()

	if data.get('status') == "PLAYING":
		if data.get('current') and data.get('total'):
			ts_start = int(time.time()) - int(data.get('current'))
			ts_end = ts_start + int(data.get('total'))
		else:
			ts_start = None
			ts_end = None

		rpc.set_activity(
			state=data.get('artist'),
			details=data.get('title'),
			act_type=2,
			ts_start=ts_start,
			ts_end=ts_end,
			large_image=data.get('thumbnail'),
			small_image="https://raw.githubusercontent.com/SuperZombi/Discord-Music-Status/refs/heads/main/github/images/audio-wave.gif",
			buttons=[
				{ "label": "Open", "url": data.get('url') }
			]
		)
	else:
		rpc.disconnect()
	return 'OK'

def monitor_timeout():
	global last_update_time
	while True:
		time.sleep(30)
		TIMEOUT = 30
		if time.time() - last_update_time > TIMEOUT and last_update_time != 0:
			try:
				rpc.disconnect()
			except:
				None
			last_update_time = 0

if __name__ == '__main__':
	rpc = discordrpc.RPC(app_id=1397914682659963050, exit_if_discord_close=False, exit_on_disconnect=False)
	Thread(target=monitor_timeout, daemon=True).start()
	systray = SysTrayIcon(resource_path("icon.ico"), "Discord Music Status", on_quit=lambda _: os._exit(0))
	systray.start()
	app.run(port=5000)

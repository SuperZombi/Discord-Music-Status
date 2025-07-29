from flask import Flask, request, make_response
from infi.systray import SysTrayIcon
from threading import Thread
import discordrpc
from discordrpc import Activity, Button, Progressbar
import time
import os, sys

def resource_path(relative_path):
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)

app = Flask(__name__)

last_update_time = 0
last_data = {}

@app.after_request
def add_cors_headers(response):
	response.headers['Access-Control-Allow-Origin'] = '*'
	response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
	response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
	return response

@app.route('/update', methods=['POST', 'OPTIONS'])
def update_presence():
	global last_update_time, last_data
	if request.method == 'OPTIONS':
		return make_response('', 204)

	data = request.json
	if last_data == data: return 'OK'

	if data.get('status') == "PLAYING":
		if time.time() - last_update_time > 15:
			if data.get('current') and data.get('total'):
				progress = Progressbar(
					int(data.get('current')),
					int(data.get('total'))
				)
			else:
				progress = {}

			rpc.set_activity(
				state=data.get('artist'),
				details=data.get('title'),
				act_type=Activity.Listening,
				large_image=data.get('thumbnail'),
				details_url=data.get('url'),
				small_image="https://raw.githubusercontent.com/SuperZombi/Discord-Music-Status/refs/heads/main/github/images/audio-wave.gif",
				buttons=[ Button("Open", data.get('url') ) ],
				**progress
			)
			last_update_time = time.time()
			last_data = data
	else:
		rpc.clear()
		last_update_time = time.time()
		last_data = data

	return 'OK'

def monitor_timeout():
	global last_update_time
	while True:
		time.sleep(30)
		TIMEOUT = 30
		if time.time() - last_update_time > TIMEOUT and last_update_time != 0:
			try:
				rpc.clear()
			except:
				None
			last_update_time = 0

if __name__ == '__main__':
	rpc = discordrpc.RPC(app_id=1397914682659963050, exit_if_discord_close=False, exit_on_disconnect=False)
	Thread(target=monitor_timeout, daemon=True).start()
	systray = SysTrayIcon(resource_path("icon.ico"), "Discord Music Status", on_quit=lambda _: os._exit(0))
	systray.start()
	app.run(port=5000)

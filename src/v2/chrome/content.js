function sendMetadata(metadata) {
	fetch('http://localhost:5000/update', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(metadata)
	}).catch(() => {});
}

setInterval(() => {
	if (!navigator.mediaSession?.metadata) return;
	const metadata = navigator.mediaSession.metadata;
	let answer = {
		title: metadata.title,
		artist: metadata.artist,
		thumbnail: metadata.artwork[0].src,
		url: window.location.href
	}
	const media = document.querySelector('video, audio');
	if (media) {
		answer.current = media.currentTime
		answer.total = media.duration
		answer.status = media.paused ? "PAUSED" : "PLAYING"
	}
	sendMetadata(answer);
}, 15000);

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
		thumbnail: metadata.artwork[0].src
	}
	const media = document.querySelector('video, audio');
	if (media) {
		answer.current = parseInt(media.currentTime)
		answer.total = parseInt(media.duration)
		answer.status = media.paused ? "PAUSED" : "PLAYING"
	}
	if (isYoutubeUrl(window.location.href)){
		answer.url = buildYoutubeUrl(window.location.href, answer.current)
	} else {
		answer.url = window.location.href
	}

	sendMetadata(answer);
}, 15000);

function isYoutubeUrl(url) {
	try {
		const parsed = new URL(url);
		return (
			(parsed.hostname === "www.youtube.com" || parsed.hostname === "music.youtube.com")
		)
	} catch {
		return false;
	}
}
function buildYoutubeUrl(originalUrl, time) {
	try {
		const parsed = new URL(originalUrl)
		const host = parsed.hostname
		const videoId = parsed.searchParams.get("v")
		return `https://${host}/watch?v=${videoId}&t=${time}`;
	} catch {
		return originalUrl
	}
}

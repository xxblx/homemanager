
function getVideoId() {
  var video = document.getElementsByClassName('video')[0]
  return video.id;
}

function playAllVideos() {
  var videos = document.getElementsByClassName('video');
  for (var i = 0; i < videos.length; i++) {
    playVideo(videos[i].id);
  }
}

function playVideo(videoId) {
  var video = document.getElementById(videoId);

  if (Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource(videoId);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED,function() {
      video.play();
    });
  }
  else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = videoId;
    video.addEventListener('loadedmetadata',function() {
      video.play();
    });
  }
}

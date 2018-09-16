
function getVideoId() {
  var video = document.getElementsByClassName('video')[0]
  return video.id;
}

function playAllVideos() {
  var videos = document.getElementsByClassName('video');
  console.log(videos, videos[0]);
  for (var i = 0; i < videos.length; i++) {
    playVideo(videos[i].id);
  }
}

function playVideo(videoId) {
  var video = document.getElementById(videoId);
  var sourceNum = videoId.substring(5);

  if (Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource('/video/' + sourceNum + '/video.m3u8');
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED,function() {
      video.play();
    });
  } 
  else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = '/video/' + sourceNum + '/video.m3u8';
    video.addEventListener('loadedmetadata',function() {
      video.play();
    });
  }
}


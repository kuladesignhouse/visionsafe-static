document.addEventListener("DOMContentLoaded", function () {
  var thumbnail = document.querySelector(".thumbnail");
  var modal = document.getElementById("modal");
  var close = document.querySelector(".close");
  //var iframe = document.querySelector(".responsive-video");
  var iframes = document.querySelectorAll(".responsive-video");
  var player;

  var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

  if (isIOS) { // Display iOS specific content
    document.getElementById("iosContent").style.display = 'block';
    document.getElementById("otherContent").style.display = 'none';
    document.querySelector(".content-info").classList.add("isiOS");
    document.querySelector(".thumbnail").src = "vid-thumb-ios.jpg";
    player = new Vimeo.Player(iframes[1]);
  } else { // Display content for all other devices
    document.getElementById("iosContent").style.display = 'none';
    document.getElementById("otherContent").style.display = 'block';
    document.querySelector(".content-info").classList.remove("isiOS");
    document.querySelector(".thumbnail").src = "vid-thumb.jpg";
    player = new Vimeo.Player(iframes[0]);
  }

  thumbnail.addEventListener("click", function () {
      modal.style.display = "flex";
      player.play();
  });

  close.addEventListener("click", function () {
      modal.style.display = "none";
      player.pause();
  });

  window.addEventListener("click", function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
        player.pause();
    }
  });
});
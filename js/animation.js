(function () {
  function animationCharacter() {
    const imgCharacter = document.getElementById("imgCharacter");

    if (!imgCharacter) return;

    imgCharacter.src = "img/HandOpened.png";

    setTimeout(() => {
      imgCharacter.src = "img/HandCrossed.png";
    }, 1000);
  }

  window.animationCharacter = animationCharacter;
})();
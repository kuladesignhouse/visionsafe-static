var burgmenu = document.getElementById("burgmenu");
var hamburger = document.getElementById("hamburger-icon");
function handleNav(elm) {
  const child = elm.matches(".burg, .burg *, .line *, p#burgtxt");
  if (child) {
    if (!burgmenu.classList.contains("clckd")) {
      burgmenu.classList.add("clckd");
      hamburger.classList.add("active");
    } else {
      burgmenu.classList.remove("clckd");
      hamburger.classList.remove("active");
    }
  }
}
hamburger.addEventListener('click', event => {
  handleNav(event.target);
});
document.getElementById("burgtxt").addEventListener('click', event => {
  handleNav(event.target);
});
let checkboxes = document.querySelectorAll("input[type='checkbox']");
for (var i = 0; i < checkboxes.length; i++) {
  checkboxes[i].addEventListener("change", function(e) {
    for (var c = 0; c < checkboxes.length; c++) {
      if (checkboxes[c].checked && e.target != checkboxes[c]) {
        checkboxes[c].checked = false;
      }
    }
  });
}

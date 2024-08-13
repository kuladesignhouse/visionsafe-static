document.addEventListener("DOMContentLoaded", function() {
  const modal = document.getElementById('demoModal');
  const form = document.getElementById('demo');
  var requestDemoBtn = document.getElementById("request-demo");
  var desktopLogo = document.getElementById("evas-desktop-logo");
  var mobileLogo = document.getElementById("evas-mobile-logo");
  var span = document.getElementsByClassName("close-button")[0];
  const stickyDemoBtn = document.getElementById('stickyDemoBtn');
  var nav = document.querySelector(".nav");

  requestDemoBtn.onclick = function() {
    if (modal.classList.contains("successful")) {
      modal.classList.remove("successful");
    }
    modal.style.display = "flex";
  }

  stickyDemoBtn.onclick = function() {
    if (modal.classList.contains("successful")) {
      modal.classList.remove("successful");
    }
    modal.style.display = "flex";
  }

  span.onclick = function() {
    modal.style.display = "none";
  }

  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (checkValidation()) {
      const formData = {
        fullName: e.target.fullName.value,
        businessEmail: e.target.businessEmail.value,
        phone: e.target.phone.value
      };
      const response = await fetch('https://store.visionsafe.com/evas-for-commercial', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      const statusCode = response.status;
      if (!response.ok) {
        console.error(`Error occurred: ${statusCode}`);
        alert('Error submitting data.');
        return;
      } else {
      modal.classList.add("successful");
      //const data = await response.json();
    }
    }
  });

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
    }
  });

  document.addEventListener('keyup', (e) => {
    if (e.key === 'Escape') {
      modal.style.display = 'none';
    }
  });

  const fullNameInput = form.querySelector('#fullName');
  const businessEmailInput = form.querySelector('#businessEmail');
  const submitButton = form.querySelector('input[type="submit"]');

  function isValidEmail(email) {
    const pattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    return pattern.test(email);
  }

  function checkValidation() {
    if (fullNameInput.value.trim() !== '' && isValidEmail(businessEmailInput.value.trim())) {
      submitButton.classList.add('validated');
      return true;
    } else {
      submitButton.classList.remove('validated');
      return false;
    }
  }

  fullNameInput.addEventListener('input', checkValidation);
  businessEmailInput.addEventListener('input', checkValidation);

  // Initial check (in case the browser auto-fills the form)
  checkValidation();

  function showDemoBtn() {
    const mediaQuery = window.matchMedia("(min-width: 46rem)");
    const demoBtnPos = requestDemoBtn.getBoundingClientRect();
    const desktopLogoPos = desktopLogo.getBoundingClientRect();
/*
    if (desktopLogoPos.top <= 0 && mediaQuery.matches) { 
      nav.style.top = "0px";
    } else if (nav.style.top !== "-100px") {
      nav.style.top = "-100px";
    }
*/

    if (demoBtnPos.top <= 0) {
      if (nav.style.top !== "0px") { nav.style.top = "0px"; }
      stickyDemoBtn.style.opacity = '1';
      stickyDemoBtn.style.visibility = 'visible';
    } else {
      if (nav.style.top != "-100px") { nav.style.top = "-100px"; }
      stickyDemoBtn.style.opacity = '0';
      stickyDemoBtn.style.visibility = 'hidden';
    }
  }

  showDemoBtn();

  window.addEventListener('scroll', function() {
      showDemoBtn();
  });

});
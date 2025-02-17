// static/js/main.js
document.addEventListener("DOMContentLoaded", function() {
  // Mobile Navbar Toggle
  const navbarToggle = document.getElementById("navbar-toggle");
  if (navbarToggle) {
    navbarToggle.addEventListener("click", function() {
      document.getElementById("navbar-menu").classList.toggle("active");
    });
  }
});

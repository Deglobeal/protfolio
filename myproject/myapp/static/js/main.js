// main.js

// Toggle mobile menu
const mobileMenuIcon = document.querySelector(".mobile-menu");
const navList = document.querySelector("nav ul");

mobileMenuIcon.addEventListener("click", () => {
  navList.classList.toggle("mobile-nav");
});

// Scroll to section on link click
const links = document.querySelectorAll("nav ul li a");

links.forEach((link) => {
  link.addEventListener("click", (e) => {
    const targetId = link.getAttribute("href");
    if (targetId.startsWith("#")) {
      e.preventDefault();
      document.querySelector(targetId).scrollIntoView({ behavior: "smooth" });
    }
  });
});

// Optional: Scroll to top button
const scrollTopBtn = document.getElementById("scrollTopBtn");

window.addEventListener("scroll", () => {
  if (window.scrollY > 300) {
    scrollTopBtn.style.display = "block";
  } else {
    scrollTopBtn.style.display = "none";
  }
});

scrollTopBtn?.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});

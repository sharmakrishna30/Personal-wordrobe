const sections = document.querySelectorAll("section");

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add("fade-in");
    }
  });
}, {
  threshold: 0.2
});

sections.forEach(section => observer.observe(section));
exploreBtn.addEventListener("click", () => {
    window.location.href = "/outfits.html"; // future page
  });
  const toggleTheme = document.getElementById("themeToggle");
  if (toggleTheme) {
    toggleTheme.addEventListener("click", () => {
      document.body.classList.toggle("lightdark-mode");
    });
  }
    
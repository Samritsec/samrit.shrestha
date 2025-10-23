document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggle = document.getElementById("toggleSidebar");

  toggle.addEventListener("click", () => {
    sidebar.dataset.collapsed = sidebar.dataset.collapsed === "true" ? "false" : "true";
  });
});

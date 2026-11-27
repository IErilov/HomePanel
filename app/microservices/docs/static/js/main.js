document.addEventListener("DOMContentLoaded", () => {
  const search = document.querySelector("#endpoint-search");
  if (search) {
    const rows = [...document.querySelectorAll(".endpoint-row")];
    const empty = document.querySelector("#no-results");
    const filter = () => {
      const q = search.value.trim().toLowerCase();
      let visible = 0;
      rows.forEach(row => {
        const show = row.dataset.search.includes(q);
        row.hidden = !show;
        if (show) visible++;
      });
      document.querySelectorAll(".endpoint-group").forEach(group => {
        group.hidden = !group.querySelector(".endpoint-row:not([hidden])");
      });
      if (empty) empty.hidden = visible !== 0;
    };
    search.addEventListener("input", filter);
    document.addEventListener("keydown", event => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault(); search.focus();
      }
      if (event.key === "Escape") { search.value = ""; filter(); search.blur(); }
    });
  }

  document.querySelectorAll("[data-copy]").forEach(button => {
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(button.dataset.copy);
        const old = button.textContent;
        button.textContent = "Copied!";
        setTimeout(() => button.textContent = old, 1200);
      } catch {
        button.textContent = "Copy unavailable";
      }
    });
  });
});
